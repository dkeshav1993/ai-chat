"""LangGraph StateGraph for AI-orchestrated hotel search.

Flow:
  extract_intent → autosuggest → trigger_search → poll_background_status
    → (loop while inProgress) → fetch_poll_results → write_history → END

  extract_intent → clarification_node → END  (when destination/dates missing)

On any error: error_handler node formats a TraversiaError into state, graph terminates.
"""

import asyncio
import json
import time
import structlog
from typing import TypedDict, List, Optional, AsyncGenerator, Any

from langgraph.graph import StateGraph, END

from config import settings
from models.errors import TraversiaError, ErrorCode
from models.search import (
    AutosuggestIdentifier,
    HotelSearchPayload,
    Room,
)
from providers.factory import get_provider
from services.token_service import token_service
from memory.poll_state import save_poll_state, update_poll_iteration

logger = structlog.get_logger(__name__)


# ─── State Definition ─────────────────────────────────────────────────────────

class SearchState(TypedDict):
    session_id: str
    correlation_id: str
    query: str
    destination: str
    destination_type: str
    check_in: str
    check_out: str
    adult_count: int
    child_count: int
    room_count: int
    auto_suggest_id: Optional[str]
    autosuggest_identifier: Optional[dict]
    autosuggest_candidates: Optional[list]
    search_key: Optional[str]
    cache_key: Optional[str]
    poll_iteration: int
    poll_start_time: float
    poll_in_progress: bool
    hotels: List[dict]
    initial_hotels: List[dict]   # hotels returned directly from hotels/search
    curated_available: bool      # True when background processing finished AND initial_hotels exist
    is_search_complete: bool
    error: Optional[dict]
    # Interactive clarification
    needs_clarification: bool
    missing_fields: List[str]
    # Client-side filters (applied post-fetch; future: pass to request body)
    hotel_name_filter: Optional[str]
    star_rating_filter: Optional[int]   # e.g. 3, 4, 5
    budget_min: Optional[float]
    budget_max: Optional[float]
    # SSE event queue for streaming to caller
    _events: List[dict]


# ─── Filter Helper ────────────────────────────────────────────────────────────

def _apply_filters(hotels: List[dict], state: "SearchState") -> List[dict]:
    """Apply post-fetch client-side filters: hotel name, star rating, budget.

    TODO(future): pass filter params in the request body once backend API supports it.
    """
    hotel_name = (state.get("hotel_name_filter") or "").strip().lower()
    star = state.get("star_rating_filter")
    budget_min = state.get("budget_min")
    budget_max = state.get("budget_max")

    filtered = hotels

    if hotel_name:
        filtered = [
            h for h in filtered
            if hotel_name in (h.get("name") or "").lower()
        ]

    if star:
        def _star_matches(h: dict) -> bool:
            raw = h.get("starRating") or h.get("rating") or ""
            try:
                return int(float(str(raw))) == star
            except (ValueError, TypeError):
                return False
        filtered = [h for h in filtered if _star_matches(h)]

    if budget_min is not None or budget_max is not None:
        def _budget_in_range(h: dict) -> bool:
            # Try to find the cheapest total fare across all providers
            providers = h.get("providerInfo") or []
            if not providers:
                return True  # can't filter if no price info
            fares = []
            for p in providers:
                if isinstance(p, dict):
                    tf = p.get("totalFare")
                    if tf is not None:
                        try:
                            fares.append(float(tf))
                        except (ValueError, TypeError):
                            pass
            if not fares:
                return True
            min_fare = min(fares)
            if budget_min is not None and min_fare < budget_min:
                return False
            if budget_max is not None and min_fare > budget_max:
                return False
            return True
        filtered = [h for h in filtered if _budget_in_range(h)]

    return filtered


# ─── Nodes ────────────────────────────────────────────────────────────────────

async def extract_intent(state: SearchState) -> dict:
    """Parse natural-language hotel search query into structured params."""

    events = list(state.get("_events", []))

    events.append({
        "event": "thinking",
        "data": {"message": "Understanding your search..."}
    })

    # ------------------------------------------------------------------
    # FAKE AI / REGEX MODE
    # ------------------------------------------------------------------
    if settings.USE_FAKE_AI:

        import re
        from datetime import datetime, timedelta

        query = state["query"]
        query_lower = query.lower()

        # --------------------------------------------------------------
        # Defaults
        # --------------------------------------------------------------
        destination = "Mumbai"
        adult_count = 2
        child_count = 0
        room_count = 1

        # Dynamic fallback: checkin = today + 2, checkout = checkin + 1
        today = datetime.now().date()
        default_check_in  = today + timedelta(days=2)
        default_check_out = default_check_in + timedelta(days=1)

        # --------------------------------------------------------------
        # Destination Extraction
        # --------------------------------------------------------------
        supported_destinations = {
            "goa": "Goa",
            "mumbai": "Mumbai",
            "delhi": "New Delhi",
            "new delhi": "New Delhi",
            "dubai": "Dubai",
            "bangkok": "Bangkok",
            "singapore": "Singapore",
            "london": "London",
            "paris": "Paris",
            "bali": "Bali",
            "phuket": "Phuket",
            "jaipur": "Jaipur",
            "kolkata": "Kolkata",
            "chennai": "Chennai",
            "hyderabad": "Hyderabad",
            "bengaluru": "Bengaluru",
            "bangalore": "Bengaluru",
            "pune": "Pune",
            "agra": "Agra",
            "udaipur": "Udaipur",
            "kerala": "Kerala",
            "shimla": "Shimla",
            "manali": "Manali",
            "new york": "New York",
            "los angeles": "Los Angeles",
            "tokyo": "Tokyo",
            "sydney": "Sydney",
            "toronto": "Toronto",
        }

        destination_found = False
        for key, value in supported_destinations.items():
            if key in query_lower:
                destination = value
                destination_found = True
                break

        # Try generic "in <CityName>" pattern
        if not destination_found:
            import re as _re
            in_match = _re.search(r"\bin\s+([A-Z][a-zA-Z\s]{2,20}?)(?:\s+from|\s+for|\s+on|\s+at|$|\?)", query)
            if in_match:
                destination = in_match.group(1).strip()
                destination_found = True

        # --------------------------------------------------------------
        # Hotel name filter extraction
        # Patterns: "find taj hotel", "book marriott", "show me oberoi"
        # --------------------------------------------------------------
        hotel_name_filter: Optional[str] = None
        hotel_name_match = re.search(
            r"(?:find|show|book|search|looking for|looking at)\s+([\w\s]+?)\s+hotel",
            query_lower,
        )
        if hotel_name_match:
            candidate = hotel_name_match.group(1).strip()
            # Exclude generic words that are not real hotel names
            generic = {"a", "an", "the", "some", "any", "good", "best", "cheap", "luxury", "budget"}
            if candidate and candidate not in generic:
                hotel_name_filter = candidate
        # Also: "taj hotel", "marriott in delhi" style
        if not hotel_name_filter:
            brand_match = re.search(
                r"(taj|marriott|hilton|hyatt|oberoi|ibis|radisson|novotel|sheraton|westin|intercontinental|leela|itc|crowne)\s+(?:hotel|resort|plaza|palace)?",
                query_lower,
            )
            if brand_match:
                hotel_name_filter = brand_match.group(1).strip()

        # --------------------------------------------------------------
        # Star rating filter extraction
        # Patterns: "5 star", "4-star", "3 star hotel"
        # --------------------------------------------------------------
        star_rating_filter: Optional[int] = None
        star_match = re.search(r"(\d)\s*-?\s*star", query_lower)
        if star_match:
            try:
                star_rating_filter = int(star_match.group(1))
            except ValueError:
                pass

        # --------------------------------------------------------------
        # Budget extraction
        # Patterns: "under 5000", "below 3000", "max 10000 per night"
        # --------------------------------------------------------------
        budget_max: Optional[float] = None
        budget_min: Optional[float] = None
        budget_match = re.search(r"(?:under|below|max|maximum|less than|upto|up to)\s+(?:rs\.?|inr|₹|\$|usd)?\s*([\d,]+)", query_lower)
        if budget_match:
            try:
                budget_max = float(budget_match.group(1).replace(",", ""))
            except ValueError:
                pass
        budget_from_match = re.search(r"(?:from|above|min|minimum|at least)\s+(?:rs\.?|inr|₹|\$|usd)?\s*([\d,]+)", query_lower)
        if budget_from_match:
            try:
                budget_min = float(budget_from_match.group(1).replace(",", ""))
            except ValueError:
                pass

        # --------------------------------------------------------------
        # Guest / Room Extraction
        # --------------------------------------------------------------
        adult_match = re.search(r"(\d+)\s*(adult|adults)", query_lower)
        if adult_match:
            adult_count = int(adult_match.group(1))

        child_match = re.search(r"(\d+)\s*(child|children|kids)", query_lower)
        if child_match:
            child_count = int(child_match.group(1))

        room_match = re.search(r"(\d+)\s*(room|rooms)", query_lower)
        if room_match:
            room_count = int(room_match.group(1))

        # --------------------------------------------------------------
        # Date Extraction
        # Supports:
        #   ISO:        2026-06-09  /  2026/06/09
        #   Numeric DD/MM: 9/6  /  09/06
        #   Text: 20 Oct, 5 November, June 9
        # Priority: ISO > slash > text
        # If 1 date found  -> checkout = checkin + 1
        # If 0 dates found -> checkin = today+2, checkout = today+3
        # --------------------------------------------------------------
        month_map = {
            "jan": 1, "january": 1,
            "feb": 2, "february": 2,
            "mar": 3, "march": 3,
            "apr": 4, "april": 4,
            "may": 5,
            "jun": 6, "june": 6,
            "jul": 7, "july": 7,
            "aug": 8, "august": 8,
            "sep": 9, "sept": 9, "september": 9,
            "oct": 10, "october": 10,
            "nov": 11, "november": 11,
            "dec": 12, "december": 12,
        }

        current_year = today.year
        parsed_dates: list[datetime] = []

        # Pattern 1: ISO  2026-06-09  or  2026/06/09
        for m in re.finditer(r"(\d{4})[-/](\d{1,2})[-/](\d{1,2})", query):
            try:
                parsed_dates.append(datetime(int(m.group(1)), int(m.group(2)), int(m.group(3))))
            except ValueError:
                pass

        # Pattern 2: DD/MM  (no  only if no ISO dates foundyear) 
        if not parsed_dates:
            for m in re.finditer(r"(?<!\d)(\d{1,2})/(\d{1,2})(?!\d)", query):
                try:
                    d, mo = int(m.group(1)), int(m.group(2))
                    if 1 <= mo <= 12 and 1 <= d <= 31:
                        parsed_dates.append(datetime(current_year, mo, d))
                except ValueError:
                    pass

        # Pattern 3: DD MonthName  or  MonthName DD
        if not parsed_dates:
            month_names = "|".join(sorted(month_map.keys(), key=len, reverse=True))
            text_pat = re.compile(
                rf"(?:(\d{{1,2}})\s+({month_names})|({month_names})\s+(\d{{1,2}}))",
                re.IGNORECASE,
            )
            for m in text_pat.finditer(query_lower):
                day = int(m.group(1) or m.group(4))
                month_str = (m.group(2) or m.group(3)).lower()
                mo = month_map.get(month_str)
                if mo:
                    try:
                        parsed_dates.append(datetime(current_year, mo, day))
                    except ValueError:
                        pass

        # Resolve checkin / checkout
        if len(parsed_dates) >= 2:
            parsed_dates.sort()
            check_in_date  = parsed_dates[0]
            check_out_date = parsed_dates[1]
        elif len(parsed_dates) == 1:
            check_in_date  = parsed_dates[0]
            check_out_date = check_in_date + timedelta(days=1)
        else:
            check_in_date  = datetime.combine(default_check_in,  datetime.min.time())
            check_out_date = datetime.combine(default_check_out, datetime.min.time())

        check_in  = check_in_date.strftime("%Y-%m-%d")
        check_out = check_out_date.strftime("%Y-%m-%d")

        # --------------------------------------------------------------
        # Clarification check: if destination not found → ask user
        # --------------------------------------------------------------
        dates_are_default = len(parsed_dates) == 0
        missing_fields: List[str] = []
        if not destination_found:
            missing_fields.append("destination")
        if dates_are_default:
            missing_fields.append("check_in")
            missing_fields.append("check_out")

        needs_clarification = not destination_found

        if needs_clarification:
            missing_labels = {
                "destination": "city/destination",
                "check_in": "check-in date",
                "check_out": "check-out date",
            }
            missing_str = ", ".join(missing_labels.get(f, f) for f in missing_fields)
            clarification_message = (
                f"I'd love to help! To find the best hotels, could you please tell me: {missing_str}? "
                f"Also, how many adults, rooms, and any children? "
                f"(You can skip to use defaults: 1 adult, 1 room, check-in tomorrow+1, check-out the day after)"
            )
            events.append({
                "event": "clarification_needed",
                "data": {
                    "message": clarification_message,
                    "missing_fields": missing_fields,
                    "hotel_name_filter": hotel_name_filter,
                },
            })

            return {
                "destination": destination,
                "destination_type": "city",
                "check_in": check_in,
                "check_out": check_out,
                "adult_count": adult_count,
                "child_count": child_count,
                "room_count": room_count,
                "needs_clarification": True,
                "missing_fields": missing_fields,
                "hotel_name_filter": hotel_name_filter,
                "star_rating_filter": star_rating_filter,
                "budget_min": budget_min,
                "budget_max": budget_max,
                "_events": events,
            }

        logger.info(
            "fake_ai_intent_extracted",
            destination=destination,
            check_in=check_in,
            check_out=check_out,
            adult_count=adult_count,
            child_count=child_count,
            room_count=room_count,
        )

        events.append({
            "event": "thinking",
            "data": {
                "message": (
                    f"Searching hotels in {destination} "
                    f"from {check_in} to {check_out}"
                )
            },
        })

        return {
            "destination": destination,
            "destination_type": "city",
            "check_in": check_in,
            "check_out": check_out,
            "adult_count": adult_count,
            "child_count": child_count,
            "room_count": room_count,
            "needs_clarification": False,
            "missing_fields": [],
            "hotel_name_filter": hotel_name_filter,
            "star_rating_filter": star_rating_filter,
            "budget_min": budget_min,
            "budget_max": budget_max,
            "_events": events,
        }

    # ------------------------------------------------------------------
    # REAL OPENAI MODE
    # ------------------------------------------------------------------

    from openai import AsyncOpenAI
    from datetime import datetime, timedelta

    client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)

    _today = datetime.now().date()
    _default_ci = (_today + timedelta(days=2)).strftime("%Y-%m-%d")
    _default_co = (_today + timedelta(days=3)).strftime("%Y-%m-%d")

    system_prompt = (
        "You are a hotel search assistant. Extract structured search parameters from the user query. "
        "Return a JSON object with these fields:\n"
        "  - destination: string (city or location name; empty string '' if not specified)\n"
        "  - destination_type: string (city, hotel, or area — default city)\n"
        f"  - check_in: string (YYYY-MM-DD format; today is {_today}; default if unspecified: {_default_ci})\n"
        f"  - check_out: string (YYYY-MM-DD format; default if unspecified: {_default_co})\n"
        "  - adult_count: integer (default 2)\n"
        "  - child_count: integer (default 0)\n"
        "  - room_count: integer (default 1)\n"
        "  - hotel_name_filter: string or null (specific hotel brand/name mentioned, e.g. 'taj', 'marriott')\n"
        "  - star_rating_filter: integer or null (if user mentions 3-star, 4-star, 5-star)\n"
        "  - budget_max: number or null (max budget per night in INR/USD if mentioned)\n"
        "  - budget_min: number or null (min budget if mentioned)\n"
        "  - needs_clarification: boolean (true ONLY if destination is completely missing/unclear)\n"
        "  - missing_fields: array of strings (e.g. ['destination'] if destination missing; [] otherwise)\n\n"
        "Return ONLY valid JSON. Do not wrap in markdown."
    )

    try:
        response = await client.chat.completions.create(
            model=settings.OPENAI_MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": state["query"]},
            ],
            temperature=0,
            response_format={"type": "json_object"},
        )

        raw = response.choices[0].message.content or "{}"

        intent = json.loads(raw)

    except Exception as exc:

        logger.error(
            "extract_intent_failed",
            error=str(exc)
        )

        return {
            "error": TraversiaError(
                code=ErrorCode.INTERNAL_ERROR,
                message="Could not understand your search query. Please try rephrasing.",
                recoverable=True,
            ).to_dict(),
            "_events": events,
        }

    # Apply dynamic defaults if OpenAI left dates empty
    ci = intent.get("check_in", "") or _default_ci
    co = intent.get("check_out", "") or _default_co
    needs_clarification = bool(intent.get("needs_clarification", False))
    missing_fields = intent.get("missing_fields") or []
    hotel_name_filter = intent.get("hotel_name_filter") or None
    star_rating_filter = intent.get("star_rating_filter") or None
    budget_min = intent.get("budget_min") or None
    budget_max = intent.get("budget_max") or None

    if not intent.get("destination"):
        needs_clarification = True
        if "destination" not in missing_fields:
            missing_fields.append("destination")

    if needs_clarification:
        missing_labels = {
            "destination": "city/destination",
            "check_in": "check-in date",
            "check_out": "check-out date",
        }
        missing_str = ", ".join(missing_labels.get(f, f) for f in missing_fields)
        clarification_message = (
            f"I'd love to help! To find the best hotels, could you please tell me: {missing_str}? "
            f"Also, how many adults, rooms, and any children? "
            f"(You can skip to use defaults: 1 adult, 1 room, check-in {_default_ci}, check-out {_default_co})"
        )
        events.append({
            "event": "clarification_needed",
            "data": {
                "message": clarification_message,
                "missing_fields": missing_fields,
                "hotel_name_filter": hotel_name_filter,
            },
        })

        return {
            "destination": intent.get("destination", ""),
            "destination_type": intent.get("destination_type", "city"),
            "check_in": ci,
            "check_out": co,
            "adult_count": int(intent.get("adult_count", 2)),
            "child_count": int(intent.get("child_count", 0)),
            "room_count": int(intent.get("room_count", 1)),
            "needs_clarification": True,
            "missing_fields": missing_fields,
            "hotel_name_filter": hotel_name_filter,
            "star_rating_filter": int(star_rating_filter) if star_rating_filter else None,
            "budget_min": float(budget_min) if budget_min else None,
            "budget_max": float(budget_max) if budget_max else None,
            "_events": events,
        }

    logger.info(
        "intent_extracted",
        destination=intent.get("destination"),
        check_in=ci,
    )

    events.append({
        "event": "thinking",
        "data": {
            "message": (
                f"Searching for hotels in "
                f"{intent.get('destination', 'your destination')}..."
            )
        },
    })

    return {
        "destination": intent.get("destination", ""),
        "destination_type": intent.get("destination_type", "city"),
        "check_in": ci,
        "check_out": co,
        "adult_count": int(intent.get("adult_count", 2)),
        "child_count": int(intent.get("child_count", 0)),
        "room_count": int(intent.get("room_count", 1)),
        "needs_clarification": False,
        "missing_fields": [],
        "hotel_name_filter": hotel_name_filter,
        "star_rating_filter": int(star_rating_filter) if star_rating_filter else None,
        "budget_min": float(budget_min) if budget_min else None,
        "budget_max": float(budget_max) if budget_max else None,
        "_events": events,
    }


async def clarification_node(state: SearchState) -> dict:
    """Emit the clarification_needed event and terminate the graph.

    This node is reached when extract_intent determines that destination or
    other mandatory fields are missing. The frontend will capture the user's
    answers and restart the search with a complete query.
    """
    # Events are already populated by extract_intent; nothing more to add.
    return {"is_search_complete": True, "_events": state.get("_events", [])}


async def autosuggest(state: SearchState) -> dict:
    """Resolve the destination to an AutoSuggest ID and identifier."""
    events = list(state.get("_events", []))
    events.append({"event": "thinking", "data": {"message": f"Looking up {state['destination']}..."}})

    try:
        token = None
        # For handling both real and fake providers without branching the graph, we attempt to fetch a token but allow it to fail gracefully if not needed.
        if not settings.USE_MOCK_PROVIDER:
            token = await token_service.get_token()
        result = await get_provider().autosuggest(
            destination_keyword=state["destination"],
            correlation_id=state["correlation_id"],
            token=token,
        )
    except TraversiaError as exc:
        return {"error": exc.to_dict(), "_events": events}

    suggestions = result.autoSuggests
    if not suggestions:
        return {
            "error": TraversiaError(
                code=ErrorCode.NO_AUTOSUGGEST_RESULT,
                message=f"No destinations found for '{state['destination']}'.",
                recoverable=True,
                capability="AUTOSUGGEST",
            ).to_dict(),
            "_events": events,
        }

    candidates = [s.model_dump() for s in suggestions]

    # Prefer type="cities" → "locations" → first result
    selected = next((s for s in suggestions if s.type == "cities"), None) \
            or next((s for s in suggestions if s.type == "locations"), None) \
            or suggestions[0]

    events.append({
        "event": "thinking",
        "data": {
            "message": f"Found destination: '{selected.name}' ({selected.cityName or selected.name}, {selected.countryName or ''})."
        },
    })

    identifier = AutosuggestIdentifier(
        uniqueIdentifier=selected.uniqueId,
        type=selected.type,
        name=selected.name,
        cityName=selected.cityName,
        countryName=selected.countryName,
        stateName=selected.stateName,
    )

    await save_poll_state(state["session_id"], {
        "autoSuggestId": result.autoSuggestId,
        "uniqueIdentifier": selected.uniqueId,
        "identifierType": selected.type,
        "identifierName": selected.name,
    })

    return {
        "auto_suggest_id": result.autoSuggestId,
        "autosuggest_identifier": identifier.model_dump(),
        "autosuggest_candidates": candidates,
        "_events": events,
    }


async def trigger_search(state: SearchState) -> dict:
    """Trigger a hotel search using the resolved AutoSuggest data."""
    events = list(state.get("_events", []))
    events.append({"event": "thinking", "data": {"message": "Initiating hotel search..."}})

    # Build rooms with mocked guest data (MVP: one lead adult guest per room)
    MOCK_GUEST = {
        "city": "Mumbai",
        "country": "India",
        "dateOfBirth": "02-12-1993",
        "email": "traveller@nextrip.ai",
        "employeeCode": "NXT001",
        "firstName": "NexTrip",
        "guestType": "ADT",
        "lastName": "Traveller",
        "mobileNo": "9999999999",
        "state": "Maharashtra",
        "title": "Mr",
        "travellerId": 1,
    }

    rooms: List[Room] = []
    for i in range(state["room_count"]):
        adults_in_room = max(1, state["adult_count"] // state["room_count"])
        children_in_room = state["child_count"] if i == 0 else 0
        guests = [MOCK_GUEST] * adults_in_room
        rooms.append(Room(
            roomNo=i + 1,
            adultCount=adults_in_room,
            childrenCount=children_in_room,
            guests=guests,
        ))

    identifier = state["autosuggest_identifier"] or {}
    payload = HotelSearchPayload(
        autoSuggestId=state["auto_suggest_id"] or "",
        checkIn=state["check_in"],
        checkOut=state["check_out"],
        autosuggestIdentifier=AutosuggestIdentifier(**identifier),
        rooms=rooms,
        journeyType="Domestic",
        travelType="Business Travel",
    )

    try:
        token = None
        # For handling both real and fake providers without branching the graph, we attempt to fetch a token but allow it to fail gracefully if not needed.
        if not settings.USE_MOCK_PROVIDER:
            token = await token_service.get_token()
        result = await get_provider().hotel_search(payload=payload, correlation_id=state["correlation_id"], token=token)
    except TraversiaError as exc:
        return {"error": exc.to_dict(), "_events": events}

    search_key = result.data.searchKey or ""
    cache_key = result.data.cacheKey or ""

    # Capture any hotels returned directly by the search API
    initial_hotel_list = [h.model_dump() for h in (result.data.hotels or [])]

    # Apply post-fetch client-side filters
    filtered_initial = _apply_filters(initial_hotel_list, state)
    # If filters removed all hotels but there were results, keep originals and note filtering
    display_initial = filtered_initial if filtered_initial else initial_hotel_list

    await save_poll_state(state["session_id"], {
        "autoSuggestId": state["auto_suggest_id"] or "",
        "searchKey": search_key,
        "cacheKey": cache_key,
        "pollIteration": 0,
    })

    # Emit initial hotels immediately so the UI shows them before polling finishes
    if display_initial:
        events.append({
            "event": "initial_hotels",
            "data": {
                "hotels": display_initial,
                "count": len(display_initial),
            },
        })

    return {
        "search_key": search_key,
        "cache_key": cache_key,
        "initial_hotels": initial_hotel_list,
        "hotels": display_initial,
        "curated_available": False,
        "poll_iteration": 0,
        "poll_start_time": time.time(),
        "poll_in_progress": True,
        "_events": events,
    }


async def poll_background_status(state: SearchState) -> dict:
    """Check whether the background hotel search is still running.

    Loops back to itself while inProgress is True. Emits a POLL_TIMEOUT error after
    settings.POLL_TIMEOUT_SECONDS.
    """
    events = list(state.get("_events", []))

    elapsed = time.time() - state.get("poll_start_time", time.time())
    has_initial = bool(state.get("initial_hotels"))

    if elapsed > settings.POLL_TIMEOUT_SECONDS:
        logger.warning("poll_timeout", elapsed=elapsed, session_id=state["session_id"])
        # Timed out. If we have initial hotels, stop gracefully and let write_history close.
        # If we have no initial hotels, proceed to fetch_poll_results as fallback.
        return {
            "poll_in_progress": False,
            "curated_available": False,
            "_events": events,
        }

    # Sleep before polling (except on very first iteration)
    if state["poll_iteration"] > 0:
        await asyncio.sleep(settings.POLL_INTERVAL_SECONDS)

    try:
        token = None
        # For handling both real and fake providers without branching the graph, we attempt to fetch a token but allow it to fail gracefully if not needed.
        if not settings.USE_MOCK_PROVIDER:
            token = await token_service.get_token()
        status = await get_provider().background_status(
            cache_key=state["cache_key"] or "",
            search_key=state["search_key"] or "",
            auto_suggest_id=state["auto_suggest_id"] or "",
            correlation_id=state["correlation_id"],
            token=token,
        )
    except TraversiaError as exc:
        return {"error": exc.to_dict(), "poll_in_progress": False, "_events": events}

    await update_poll_iteration(state["session_id"])

    in_progress = status.data.inProgress
    events.append({
        "event": "thinking",
        "data": {"message": f"Enriching hotel data... (pass {state['poll_iteration'] + 1})"},
    })

    # If background processing just finished AND we already have initial hotels,
    # mark curated_available so we prompt the user instead of auto-overwriting results.
    just_finished = (not in_progress) and bool(state.get("initial_hotels"))

    return {
        "poll_iteration": state["poll_iteration"] + 1,
        "poll_in_progress": in_progress,
        "curated_available": just_finished,
        "_events": events,
    }


async def fetch_poll_results(state: SearchState) -> dict:
    """Fetch the current batch of hotels via search-by-poll."""
    events = list(state.get("_events", []))

    try:
        token = None
        # For handling both real and fake providers without branching the graph, we attempt to fetch a token but allow it to fail gracefully if not needed.
        if not settings.USE_MOCK_PROVIDER:
            token = await token_service.get_token()
        result = await get_provider().search_by_poll(
            search_key=state["search_key"] or "",
            cache_key=state["cache_key"] or "",
            auto_suggest_id=state["auto_suggest_id"] or "",
            correlation_id=state["correlation_id"],
            token=token,
            check_in=state.get("check_in", ""),
            check_out=state.get("check_out", ""),
        )
    except TraversiaError as exc:
        return {"error": exc.to_dict(), "_events": events}

    new_hotels = [h.model_dump() for h in result.data.hotels]

    # Apply post-fetch client-side filters
    filtered_new = _apply_filters(new_hotels, state)
    display_new = filtered_new if filtered_new else new_hotels

    all_hotels = list(state.get("hotels", [])) + display_new
    batch_index = state.get("poll_iteration", 0)

    events.append({
        "event": "hotels_batch",
        "data": {"hotels": display_new, "batchIndex": batch_index},
    })

    return {
        "hotels": all_hotels,
        "_events": events,
    }


async def write_history(state: SearchState) -> dict:
    """Fire-and-forget write of search history to MySQL. Never blocks the SSE stream."""
    from services.history_service import write_search_history, SearchHistoryRecord

    record = SearchHistoryRecord(
        session_id=state["session_id"],
        destination=state.get("destination", ""),
        destination_type=state.get("destination_type", "city"),
        unique_identifier=(state.get("autosuggest_identifier") or {}).get("uniqueIdentifier", ""),
        check_in=state.get("check_in", ""),
        check_out=state.get("check_out", ""),
        adult_count=state.get("adult_count", 1),
        child_count=state.get("child_count", 0),
        room_count=state.get("room_count", 1),
        auto_suggest_id=state.get("auto_suggest_id"),
        search_key=state.get("search_key"),
    )

    events = list(state.get("_events", []))
    if state.get("curated_available"):
        events.append({
            "event": "curated_ready",
            "data": {
                "message": "I found more curated hotel options! Would you like me to refresh the list with the best results?",
                "searchKey": state.get("search_key", ""),
                "sessionId": state.get("session_id", ""),
            },
        })

    events.append({
        "event": "search_complete",
        "data": {
            "totalHotels": len(state.get("hotels", [])),
            "searchKey": state.get("search_key", ""),
            "autoSuggestId": state.get("auto_suggest_id", ""),
        },
    })

    # Fire and forget — never on critical path
    asyncio.create_task(write_search_history(record))

    return {
        "is_search_complete": True,
        "_events": events,
    }


async def error_handler(state: SearchState) -> dict:
    """Format any error in state and emit a structured SSE error event."""
    events = list(state.get("_events", []))
    error = state.get("error") or {
        "code": ErrorCode.INTERNAL_ERROR.value,
        "message": "An unexpected error occurred.",
        "recoverable": True,
        "capability": None,
    }
    events.append({"event": "error", "data": error})
    return {"_events": events, "is_search_complete": True}


# ─── Conditional Edges ────────────────────────────────────────────────────────

def should_continue_polling(state: SearchState) -> str:
    """Route after poll_background_status:
    - error             -> error_handler
    - still running     -> loop poll_background_status
    - curated_available -> write_history (will emit curated_ready event)
    - no initial hotels -> fetch_poll_results (search-by-poll fallback)
    """
    if state.get("error"):
        return "error_handler"
    if state.get("poll_in_progress"):
        return "poll_background_status"
    if state.get("curated_available"):
        return "write_history"
    return "fetch_poll_results"


def route_after_node(node_name: str):
    """Returns a routing function that checks for error before proceeding."""
    def _route(state: SearchState) -> str:
        if state.get("error"):
            return "error_handler"
        return node_name
    return _route


def route_after_extract_intent(state: SearchState) -> str:
    """Route after extract_intent:
    - error              → error_handler
    - needs_clarification→ clarification_node
    - else               → autosuggest
    """
    if state.get("error"):
        return "error_handler"
    if state.get("needs_clarification"):
        return "clarification_node"
    return "autosuggest"


# ─── Graph Construction ───────────────────────────────────────────────────────

def build_graph() -> Any:
    graph = StateGraph(SearchState)

    graph.add_node("extract_intent", extract_intent)
    graph.add_node("clarification_node", clarification_node)
    graph.add_node("autosuggest", autosuggest)
    graph.add_node("trigger_search", trigger_search)
    graph.add_node("poll_background_status", poll_background_status)
    graph.add_node("fetch_poll_results", fetch_poll_results)
    graph.add_node("write_history", write_history)
    graph.add_node("error_handler", error_handler)

    graph.set_entry_point("extract_intent")

    graph.add_conditional_edges("extract_intent", route_after_extract_intent, {
        "clarification_node": "clarification_node",
        "autosuggest": "autosuggest",
        "error_handler": "error_handler",
    })
    graph.add_edge("clarification_node", END)
    graph.add_conditional_edges("autosuggest", route_after_node("trigger_search"), {
        "trigger_search": "trigger_search",
        "error_handler": "error_handler",
    })
    graph.add_conditional_edges("trigger_search", route_after_node("poll_background_status"), {
        "poll_background_status": "poll_background_status",
        "error_handler": "error_handler",
    })
    graph.add_conditional_edges(
        "poll_background_status",
        should_continue_polling,
        {
            "poll_background_status": "poll_background_status",
            "fetch_poll_results": "fetch_poll_results",
            "write_history": "write_history",
            "error_handler": "error_handler",
        },
    )
    graph.add_conditional_edges("fetch_poll_results", route_after_node("write_history"), {
        "write_history": "write_history",
        "error_handler": "error_handler",
    })

    graph.add_edge("write_history", END)
    graph.add_edge("error_handler", END)

    return graph.compile()


# Module-level compiled graph
hotel_search_graph = build_graph()


# ─── SSE Stream Helper ────────────────────────────────────────────────────────

async def run_search_and_stream(
    session_id: str,
    correlation_id: str,
    query: str,
) -> AsyncGenerator[dict, None]:
    """Run the hotel search graph and yield SSE events as they are emitted.

    Guarantees a structured error event is yielded before the generator closes.
    """
    initial_state: SearchState = {
        "session_id": session_id,
        "correlation_id": correlation_id,
        "query": query,
        "destination": "",
        "destination_type": "city",
        "check_in": "",
        "check_out": "",
        "adult_count": 2,
        "child_count": 0,
        "room_count": 1,
        "auto_suggest_id": None,
        "autosuggest_identifier": None,
        "autosuggest_candidates": None,
        "search_key": None,
        "cache_key": None,
        "poll_iteration": 0,
        "poll_start_time": 0.0,
        "poll_in_progress": False,
        "hotels": [],
        "initial_hotels": [],
        "curated_available": False,
        "is_search_complete": False,
        "error": None,
        "_events": [],
        # interactive chat / filter fields
        "needs_clarification": False,
        "missing_fields": [],
        "hotel_name_filter": None,
        "star_rating_filter": None,
        "budget_min": None,
        "budget_max": None,
    }

    emitted_events: set = set()
    try:
        async for chunk in hotel_search_graph.astream(initial_state):
            for _node_name, node_state in chunk.items():
                new_events = node_state.get("_events", [])
                for i, event in enumerate(new_events):
                    event_key = f"{id(event)}_{i}"
                    if event_key not in emitted_events:
                        emitted_events.add(event_key)
                        yield event
    except TraversiaError as exc:
        logger.error("graph_traversia_error", code=exc.code.value, message=exc.message)
        yield {"event": "error", "data": exc.to_dict()}
    except Exception as exc:
        logger.error("graph_unexpected_error", error=str(exc))
        yield {
            "event": "error",
            "data": {
                "code": ErrorCode.INTERNAL_ERROR.value,
                "message": "An unexpected error occurred. Please try your search again.",
                "recoverable": True,
                "capability": None,
            },
        }

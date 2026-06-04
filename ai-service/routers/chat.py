"""SSE chat router: GET /chat/search streams hotel search results.

The EventSource browser API requires GET. Query parameters carry session_id and query.
All orchestration happens inside the LangGraph hotel_search_graph.

POST /chat/curated-feed – called by the frontend when the user accepts the curated results
prompt. Reads the session poll state from Redis and calls search-by-poll.

POST /chat/lead – saves a lead form contact when user requests human sales agent assistance.

GET /chat/weather – proxies wttr.in weather for a city, cached in Redis for 30 minutes.
"""

import json
import uuid
import structlog
import httpx
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, EmailStr
from sse_starlette.sse import EventSourceResponse

from config import settings
from models.errors import ErrorCode, TraversiaError
from memory.poll_state import get_poll_state
from memory.redis_client import get_redis_client

logger = structlog.get_logger(__name__)

router = APIRouter(prefix="/chat", tags=["chat"])

_WEATHER_CACHE_TTL = 1800  # 30 minutes


@router.get("/search")
async def chat_search(session_id: str, query: str):
    """Stream hotel search results as Server-Sent Events.

    Events emitted:
      - thinking:             { message: str }
      - clarification_needed: { missing_fields: str[], message: str }
      - initial_hotels:       { hotels: HotelCard[] }
      - hotels_batch:         { hotels: HotelCard[], batchIndex: int }
      - curated_ready:        { message: str, sessionId: str }
      - search_complete:      { totalHotels: int, searchKey: str, autoSuggestId: str }
      - error:                { code: str, message: str, recoverable: bool, capability?: str }
    """
    import uuid
    correlation_id = str(uuid.uuid4())

    async def event_generator():
        # Wrap the entire generator in try/except so we NEVER close silently.
        try:
            from agents.hotel_search_graph import run_search_and_stream

            async for sse_event in run_search_and_stream(
                session_id=session_id,
                correlation_id=correlation_id,
                query=query,
            ):
                event_type = sse_event.get("event", "message")
                event_data = sse_event.get("data", {})
                logger.debug("sse_event_emitted", sse_event=sse_event, session_id=session_id)
                yield {
                    "event": event_type,
                    "data": json.dumps(event_data),
                }
        except Exception as exc:
            # Safety net: emit a structured INTERNAL_ERROR before closing.
            logger.error("sse_generator_unexpected_error", error=str(exc), session_id=session_id)
            yield {
                "event": "error",
                "data": json.dumps({
                    "code": ErrorCode.INTERNAL_ERROR.value,
                    "message": "An unexpected error occurred. Please try again.",
                    "recoverable": True,
                    "capability": None,
                }),
            }

    return EventSourceResponse(event_generator())


# ─── Curated Feed Endpoint ────────────────────────────────────────────────────

class CuratedFeedRequest(BaseModel):
    session_id: str


@router.post("/curated-feed")
async def load_curated_feed(body: CuratedFeedRequest):
    """Called when the user accepts the curated results prompt.

    Reads the cached searchKey/cacheKey/autoSuggestId from Redis and calls
    search-by-poll to return the backend-curated hotel list.

    Returns:
        { hotels: HotelCard[], totalHotels: int }
    """
    correlation_id = str(uuid.uuid4())
    session_id = body.session_id

    poll_state = await get_poll_state(session_id)
    if not poll_state:
        raise HTTPException(
            status_code=400,
            detail={
                "code": "VALIDATION_ERROR",
                "message": "Session expired or not found. Please start a new search.",
            },
        )

    search_key = poll_state.get("searchKey", "")
    cache_key = poll_state.get("cacheKey", "")
    auto_suggest_id = poll_state.get("autoSuggestId", "")

    if not search_key:
        raise HTTPException(
            status_code=400,
            detail={
                "code": "VALIDATION_ERROR",
                "message": "No active search found for this session.",
            },
        )

    try:
        from providers.factory import get_provider
        from services.token_service import token_service

        token = None
        if not settings.USE_MOCK_PROVIDER:
            token = await token_service.get_token()

        result = await get_provider().search_by_poll(
            search_key=search_key,
            cache_key=cache_key,
            auto_suggest_id=auto_suggest_id,
            correlation_id=correlation_id,
            token=token,
            check_in="",
            check_out="",
        )

        hotels = [h.model_dump() for h in result.data.hotels]

        logger.info(
            "curated_feed_loaded",
            session_id=session_id,
            hotel_count=len(hotels),
            correlation_id=correlation_id,
        )

        return {
            "success": True,
            "hotels": hotels,
            "totalHotels": len(hotels),
        }

    except TraversiaError as exc:
        logger.error("curated_feed_error", code=exc.code.value, message=exc.message)
        raise HTTPException(
            status_code=502,
            detail={"code": exc.code.value, "message": exc.message},
        )
    except Exception as exc:
        logger.error("curated_feed_unexpected", error=str(exc))
        raise HTTPException(
            status_code=500,
            detail={"code": "INTERNAL_ERROR", "message": "An unexpected error occurred."},
        )


# ─── Weather Proxy Endpoint ───────────────────────────────────────────────────

@router.get("/weather")
async def get_weather(city: str = Query(..., description="City name for weather lookup")):
    """Proxy weather data from wttr.in for a given city.

    Results are cached in Redis for 30 minutes.

    Returns:
        Parsed weather object with temp_C, humidity, weatherDesc, windspeedKmph, uvIndex, etc.
    """
    redis = get_redis_client()
    cache_key = f"traversia:weather:{city.lower().replace(' ', '_')}"

    # Check Redis cache
    cached = await redis.get(cache_key)
    if cached:
        try:
            return json.loads(cached)
        except Exception:
            pass

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.get(
                f"https://wttr.in/{city}?format=j1",
                headers={"Accept": "application/json", "User-Agent": "NexTripAI/1.0"},
            )
            resp.raise_for_status()
            data = resp.json()
    except httpx.TimeoutException:
        raise HTTPException(status_code=504, detail={"message": "Weather service timed out."})
    except httpx.HTTPStatusError as exc:
        raise HTTPException(status_code=502, detail={"message": f"Weather service error: {exc.response.status_code}"})
    except Exception as exc:
        logger.error("weather_fetch_error", city=city, error=str(exc))
        raise HTTPException(status_code=500, detail={"message": "Could not fetch weather data."})

    # Extract the first current_condition entry
    conditions = data.get("current_condition", [])
    if not conditions:
        raise HTTPException(status_code=404, detail={"message": "No weather data available for this city."})

    cond = conditions[0]
    result = {
        "city": city,
        "temp_C": cond.get("temp_C", ""),
        "feelsLike_C": cond.get("FeelsLikeC", ""),
        "humidity": cond.get("humidity", ""),
        "weatherDesc": cond.get("weatherDesc", [{}])[0].get("value", ""),
        "weatherIconUrl": cond.get("weatherIconUrl", [{}])[0].get("value", ""),
        "windspeedKmph": cond.get("windspeedKmph", ""),
        "winddir16Point": cond.get("winddir16Point", ""),
        "uvIndex": cond.get("uvIndex", ""),
        "visibility": cond.get("visibility", ""),
        "cloudcover": cond.get("cloudcover", ""),
        "pressure": cond.get("pressure", ""),
        "precipMM": cond.get("precipMM", ""),
    }

    # Cache result
    try:
        await redis.set(cache_key, json.dumps(result), ex=_WEATHER_CACHE_TTL)
    except Exception:
        pass

    return result


# ─── Nearby Cities Endpoint ───────────────────────────────────────────────────

_NEARBY_CACHE_TTL = 60 * 60 * 6  # 6 hours

@router.get("/nearby")
async def get_nearby_cities(city: str = Query(..., description="City name to find nearby cities for")):
    """Return a list of nearby cities for a given city.

    Uses Open-Meteo Geocoding API (free, no key) to resolve coordinates,
    then GeoNames citiesJSON API (free) to find nearby populated places.
    Results are cached in Redis for 6 hours.

    Returns:
        { city: str, nearby: [{ name: str, country: str, distance_km: float }] }
    """
    redis = get_redis_client()
    cache_key = f"traversia:nearby:{city.lower().replace(' ', '_')}"

    cached = await redis.get(cache_key)
    if cached:
        try:
            return json.loads(cached)
        except Exception:
            pass

    try:
        async with httpx.AsyncClient(timeout=10.0, headers={"User-Agent": "NexTripAI/1.0 (hotel discovery; admin@nextrip.ai)"}) as client:
            # Step 1: Get coordinates via Open-Meteo geocoding (free, no key)
            geo_resp = await client.get(
                "https://geocoding-api.open-meteo.com/v1/search",
                params={"name": city, "count": 1, "language": "en", "format": "json"},
            )
            geo_resp.raise_for_status()
            geo_data = geo_resp.json()
            results_list = geo_data.get("results", [])
            if not results_list:
                return {"city": city, "nearby": []}

            main = results_list[0]
            lat = main["latitude"]
            lon = main["longitude"]
            country = main.get("country", "")

            # Step 2: Wikipedia Geosearch (free, no API key, returns nearby places sorted by distance)
            # gsradius is in metres (300 km = 300000 m), gsnamespace=0 = articles only
            wiki_resp = await client.get(
                "https://en.wikipedia.org/w/api.php",
                params={
                    "action": "query",
                    "list": "geosearch",
                    "gscoord": f"{lat}|{lon}",
                    "gsradius": 300000,
                    "gslimit": 30,
                    "format": "json",
                },
            )
            wiki_resp.raise_for_status()
            wiki_data = wiki_resp.json()

    except httpx.TimeoutException:
        return {"city": city, "nearby": []}
    except Exception as exc:
        logger.warning("nearby_cities_fetch_error", city=city, error=str(exc))
        return {"city": city, "nearby": []}

    import math

    def haversine(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        R = 6371
        phi1, phi2 = math.radians(lat1), math.radians(lat2)
        dphi = math.radians(lat2 - lat1)
        dlambda = math.radians(lon2 - lon1)
        a = math.sin(dphi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2) ** 2
        return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    # Words in article titles that indicate it's NOT a city article
    _exclude = {
        'university', 'college', 'airport', 'stadium', 'museum', 'temple',
        'church', 'mosque', 'hospital', 'school', 'railway', 'station',
        'district', 'taluka', 'tehsil', 'canton', 'county', 'parish',
        'river', 'lake', 'mount', 'mountain', 'island', 'beach', 'fort',
        'palace', 'garden', 'zoo', 'park', 'club', 'fc', 'sc', 'ac',
        'express', 'highway', 'road', 'bridge', 'dam', 'reservoir',
    }

    input_city_lower = city.lower()
    nearby = []

    for place in wiki_data.get("query", {}).get("geosearch", []):
        title = place.get("title", "")
        title_lower = title.lower()

        # Skip the input city itself and disambiguation pages
        if input_city_lower in title_lower:
            continue
        if "(disambiguation)" in title_lower or " of " in title_lower:
            continue

        # Skip articles that are clearly NOT cities
        title_words = set(title_lower.split())
        if title_words & _exclude:
            continue

        dist_m = place.get("dist", 0)
        dist_km = round(dist_m / 1000)
        if dist_km < 10:  # skip same metro area
            continue

        nearby.append({"name": title, "country": country, "distance_km": dist_km})

    # Sort by distance, dedupe, limit to 5
    seen: set = set()
    deduped = []
    for item in sorted(nearby, key=lambda x: x["distance_km"]):
        key = item["name"].lower()
        if key not in seen:
            seen.add(key)
            deduped.append(item)
        if len(deduped) >= 5:
            break

    result = {"city": city, "nearby": deduped}

    try:
        await redis.set(cache_key, json.dumps(result), ex=_NEARBY_CACHE_TTL)
    except Exception:
        pass

    return result




class LeadFormRequest(BaseModel):
    name: str
    phone: str
    email: str
    query: str = ""


@router.post("/lead")
async def save_lead(body: LeadFormRequest):
    """Save a lead form entry when user requests human sales agent assistance.

    Stores name, phone, email, and the original query in the lead_form table.

    Returns:
        { success: bool, message: str }
    """
    try:
        import aiomysql
        conn = await aiomysql.connect(
            host=settings.MYSQL_HOST,
            port=settings.MYSQL_PORT,
            user=settings.MYSQL_USER,
            password=settings.MYSQL_PASSWORD,
            db=settings.MYSQL_DB,
            charset="utf8mb4",
        )
        async with conn.cursor() as cur:
            await cur.execute(
                "INSERT INTO lead_form (name, phone, email, query) VALUES (%s, %s, %s, %s)",
                (body.name.strip(), body.phone.strip(), body.email.strip(), body.query.strip()),
            )
        await conn.commit()
        conn.close()

        logger.info("lead_saved", name=body.name, email=body.email)
        return {"success": True, "message": "Thank you! Our sales team will reach out to you shortly."}

    except Exception as exc:
        logger.error("lead_save_error", error=str(exc))
        # Don't expose DB errors to frontend; still return success UX
        return {"success": True, "message": "Thank you! Our sales team will reach out to you shortly."}



@router.get("/search")
async def chat_search(session_id: str, query: str):
    """Stream hotel search results as Server-Sent Events.

    Events emitted:
      - thinking:       { message: str }
      - hotels_batch:   { hotels: HotelCard[], batchIndex: int }
      - search_complete:{ totalHotels: int, searchKey: str, autoSuggestId: str }
      - error:          { code: str, message: str, recoverable: bool, capability?: str }
    """
    import uuid
    correlation_id = str(uuid.uuid4())

    async def event_generator():
        # Wrap the entire generator in try/except so we NEVER close silently.
        try:
            from agents.hotel_search_graph import run_search_and_stream

            async for sse_event in run_search_and_stream(
                session_id=session_id,
                correlation_id=correlation_id,
                query=query,
            ):
                event_type = sse_event.get("event", "message")
                event_data = sse_event.get("data", {})
                logger.debug("sse_event_emitted", sse_event=sse_event, session_id=session_id)
                yield {
                    "event": event_type,
                    "data": json.dumps(event_data),
                }
        except Exception as exc:
            # Safety net: emit a structured INTERNAL_ERROR before closing.
            logger.error("sse_generator_unexpected_error", error=str(exc), session_id=session_id)
            yield {
                "event": "error",
                "data": json.dumps({
                    "code": ErrorCode.INTERNAL_ERROR.value,
                    "message": "An unexpected error occurred. Please try again.",
                    "recoverable": True,
                    "capability": None,
                }),
            }

    return EventSourceResponse(event_generator())


# ─── Curated Feed Endpoint ────────────────────────────────────────────────────

class CuratedFeedRequest(BaseModel):
    session_id: str


@router.post("/curated-feed")
async def load_curated_feed(body: CuratedFeedRequest):
    """Called when the user accepts the curated results prompt.

    Reads the cached searchKey/cacheKey/autoSuggestId from Redis and calls
    search-by-poll to return the backend-curated hotel list.

    Returns:
        { hotels: HotelCard[], totalHotels: int }
    """
    correlation_id = str(uuid.uuid4())
    session_id = body.session_id

    poll_state = await get_poll_state(session_id)
    if not poll_state:
        raise HTTPException(
            status_code=400,
            detail={
                "code": "VALIDATION_ERROR",
                "message": "Session expired or not found. Please start a new search.",
            },
        )

    search_key = poll_state.get("searchKey", "")
    cache_key = poll_state.get("cacheKey", "")
    auto_suggest_id = poll_state.get("autoSuggestId", "")

    if not search_key:
        raise HTTPException(
            status_code=400,
            detail={
                "code": "VALIDATION_ERROR",
                "message": "No active search found for this session.",
            },
        )

    try:
        from providers.factory import get_provider
        from services.token_service import token_service

        token = None
        if not settings.USE_MOCK_PROVIDER:
            token = await token_service.get_token()

        result = await get_provider().search_by_poll(
            search_key=search_key,
            cache_key=cache_key,
            auto_suggest_id=auto_suggest_id,
            correlation_id=correlation_id,
            token=token,
            check_in="",
            check_out="",
        )

        hotels = [h.model_dump() for h in result.data.hotels]

        logger.info(
            "curated_feed_loaded",
            session_id=session_id,
            hotel_count=len(hotels),
            correlation_id=correlation_id,
        )

        return {
            "success": True,
            "hotels": hotels,
            "totalHotels": len(hotels),
        }

    except TraversiaError as exc:
        logger.error("curated_feed_error", code=exc.code.value, message=exc.message)
        raise HTTPException(
            status_code=502,
            detail={"code": exc.code.value, "message": exc.message},
        )
    except Exception as exc:
        logger.error("curated_feed_unexpected", error=str(exc))
        raise HTTPException(
            status_code=500,
            detail={"code": "INTERNAL_ERROR", "message": "An unexpected error occurred."},
        )

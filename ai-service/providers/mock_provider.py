"""Mock hotel provider — serves pre-loaded JSON data for local/offline development."""
import asyncio
import copy
import json
import re
from collections import defaultdict
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import structlog

from config import settings
from models.errors import ErrorCode, TraversiaError
from models.hotel import HotelDetailsResponse
from models.room import RoomDetailsResponse
from models.search import (
    AutoSuggestResponse,
    BackgroundStatusData,
    BackgroundStatusResponse,
    HotelSearchPayload,
    HotelSearchResponse,
    SearchHotelResult,
    HotelSearchData,
)
from providers.hotel_provider import IHotelProvider

logger = structlog.get_logger(__name__)

_DATA_DIR = Path(__file__).parent.parent / "mock-data"

_poll_counters: Dict[str, int] = defaultdict(int)

_POLLS_BEFORE_COMPLETE = 2

_DEST_REGEX_MAP: List[Tuple[re.Pattern, str]] = [
    (re.compile(r"delhi|new[_\-\s]?delhi|ndl|DEL", re.IGNORECASE), "delhi"),
    (re.compile(r"\bgoa\b|panaji|PNJ|GOA", re.IGNORECASE), "goa"),
    (re.compile(r"mumbai|bombay|bom|BOM|MUM", re.IGNORECASE), "mumbai"),
    (re.compile(r"dubai|dxb|DXB|UAE", re.IGNORECASE), "dubai"),
    (re.compile(r"bangkok|bkk|BKK|THA", re.IGNORECASE), "bangkok"),
]


def _load(path: Path) -> Any:
    with open(path) as f:
        return json.load(f)


def _destination_key(identifier: str) -> str:
    for pattern, dest in _DEST_REGEX_MAP:
        if pattern.search(identifier):
            return dest
    return "delhi"


def _regex_match_key(data_map: Dict[str, Any], hotel_id: str) -> Optional[Any]:
    if hotel_id in data_map:
        return data_map[hotel_id]
    dest = _destination_key(hotel_id)
    for key in data_map:
        if key.startswith("_"):
            continue
        if _destination_key(key) == dest:
            return data_map[key]
    for key, value in data_map.items():
        if not key.startswith("_"):
            return value
    return None


class MockHotelProvider(IHotelProvider):
    """Serves pre-loaded JSON mock data."""

    async def autosuggest(
        self,
        destination_keyword: str,
        correlation_id: str,
        token: str,
    ) -> AutoSuggestResponse:
        await asyncio.sleep(0.2)

        if settings.MOCK_SCENARIO == "empty":
            return AutoSuggestResponse(
                success=False,
                status=404,
                message="No matching destinations found",
                autoSuggestId="",
                autoSuggests=[],
            )

        dest = _destination_key(destination_keyword)
        data = _load(_DATA_DIR / "autosuggest" / f"{dest}.json")
        logger.info("mock.autosuggest", destination=dest, scenario=settings.MOCK_SCENARIO)
        return AutoSuggestResponse(**data)

    async def hotel_search(
        self,
        payload: HotelSearchPayload,
        correlation_id: str,
        token: str,
    ) -> HotelSearchResponse:
        await asyncio.sleep(1.0)

        if settings.MOCK_SCENARIO == "downstream_error":
            raise TraversiaError(
                code=ErrorCode.DOWNSTREAM_ERROR,
                message="Mock downstream service returned 500",
                status_code=502,
            )

        dest = _destination_key(payload.autosuggestIdentifier.name)
        data = _load(_DATA_DIR / "search" / f"{dest}.json")

        cache_key = data["data"]["cacheKey"]
        _poll_counters[cache_key] = 0

        logger.info("mock.hotel_search", destination=dest, cache_key=cache_key)
        return HotelSearchResponse(**data)

    async def background_status(
        self,
        cache_key: str,
        search_key: str,
        auto_suggest_id: str,
        correlation_id: str,
        token: str,
    ) -> BackgroundStatusResponse:
        if settings.MOCK_SCENARIO == "timeout":
            await asyncio.sleep(max(settings.POLL_TIMEOUT_SECONDS + 10, 70))

        await asyncio.sleep(2.0)

        _poll_counters[cache_key] += 1
        in_progress = _poll_counters[cache_key] < _POLLS_BEFORE_COMPLETE

        logger.info(
            "mock.background_status",
            cache_key=cache_key,
            call_count=_poll_counters[cache_key],
            in_progress=in_progress,
        )

        return BackgroundStatusResponse(
            success=True,
            status=0,
            message="Background process status fetched successfully.",
            data=BackgroundStatusData(
                status=200,
                inProgress=in_progress,
                cacheKey=cache_key,
            ),
        )

    async def search_by_poll(
        self,
        search_key: str,
        cache_key: str,
        auto_suggest_id: str,
        correlation_id: str,
        token: str,
        check_in: str = "",
        check_out: str = "",
    ) -> HotelSearchResponse:
        await asyncio.sleep(2.0)

        dest = _destination_key(cache_key)
        poll_data = _load(_DATA_DIR / "poll" / f"{dest}.json")

        call_count = _poll_counters.get(cache_key, 1)
        batch_index = min(call_count - 1, len(poll_data) - 1)
        batch = poll_data[batch_index]

        logger.info(
            "mock.search_by_poll",
            destination=dest,
            batch_index=batch_index,
            hotel_count=len(batch["data"]["hotels"]),
        )
        return HotelSearchResponse(**batch)

    async def hotel_details(
        self,
        hotel_id: str,
        search_key: str,
        correlation_id: str,
        token: str,
    ) -> HotelDetailsResponse:
        await asyncio.sleep(0.5)

        dest = _destination_key(hotel_id)
        details_map: Dict[str, Any] = _load(_DATA_DIR / "hotel-details" / f"{dest}.json")

        data = _regex_match_key(details_map, hotel_id)
        if data is None:
            raise TraversiaError(
                code=ErrorCode.NO_RESULT,
                message=f"No mock hotel details found for hotel_id={hotel_id}",
                recoverable=False,
                capability="HOTEL_DETAILS",
            )

        data = copy.deepcopy(data)
        data["searchKey"] = search_key
        logger.info("mock.hotel_details", hotel_id=hotel_id, destination=dest)
        return HotelDetailsResponse(**data)

    async def room_details(
        self,
        hotel_id: str,
        search_key: str,
        auto_suggest_id: str,
        correlation_id: str,
        token: str,
    ) -> RoomDetailsResponse:
        await asyncio.sleep(0.5)

        dest = _destination_key(hotel_id)
        rooms_map: Dict[str, Any] = _load(_DATA_DIR / "room-details" / f"{dest}.json")

        data = _regex_match_key(rooms_map, hotel_id)
        if data is None:
            raise TraversiaError(
                code=ErrorCode.NO_RESULT,
                message=f"No mock room data found for hotel_id={hotel_id}",
                recoverable=False,
                capability="ROOM_DETAILS",
            )

        data = copy.deepcopy(data)
        data["searchKey"] = search_key
        data["autoSuggestId"] = auto_suggest_id
        if isinstance(data.get("roomData"), dict):
            data["roomData"]["hotelId"] = hotel_id
        logger.info(
            "mock.room_details",
            hotel_id=hotel_id,
            destination=dest,
            room_count=len((data.get("roomData") or {}).get("standardRooms", [])),
        )
        return RoomDetailsResponse(**data)

"""Real hotel provider — delegates to existing service functions.

This is a thin adapter over the existing service layer.
No business logic lives here — services remain the authoritative implementation.
"""
import structlog

from models.hotel import HotelDetailsResponse
from models.room import RoomDetailsResponse
from models.search import (
    AutoSuggestResponse,
    BackgroundStatusResponse,
    HotelSearchPayload,
    HotelSearchResponse,
)
from providers.hotel_provider import IHotelProvider
from services.autosuggest_service import call_autosuggest
from services.hotel_detail_service import get_hotel_details
from services.poll_service import check_background_status, search_by_poll as _search_by_poll
from services.room_detail_service import get_room_details
from services.search_service import call_hotel_search

logger = structlog.get_logger(__name__)


class RealHotelProvider(IHotelProvider):
    """Delegates every call to the live Spring Boot wrapper APIs via existing services."""

    async def autosuggest(
        self,
        destination_keyword: str,
        correlation_id: str,
        token: str,
    ) -> AutoSuggestResponse:
        return await call_autosuggest(destination_keyword, correlation_id, token)

    async def hotel_search(
        self,
        payload: HotelSearchPayload,
        correlation_id: str,
        token: str,
    ) -> HotelSearchResponse:
        return await call_hotel_search(payload, correlation_id, token)

    async def background_status(
        self,
        cache_key: str,
        search_key: str,
        auto_suggest_id: str,
        correlation_id: str,
        token: str,
    ) -> BackgroundStatusResponse:
        return await check_background_status(
            cache_key, search_key, auto_suggest_id, correlation_id, token
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
        return await _search_by_poll(
            search_key, cache_key, auto_suggest_id, correlation_id, token,
            check_in=check_in, check_out=check_out,
        )

    async def hotel_details(
        self,
        hotel_id: str,
        search_key: str,
        correlation_id: str,
        token: str,
    ) -> HotelDetailsResponse:
        return await get_hotel_details(hotel_id, search_key, correlation_id, token)

    async def room_details(
        self,
        hotel_id: str,
        search_key: str,
        auto_suggest_id: str,
        correlation_id: str,
        token: str,
    ) -> RoomDetailsResponse:
        return await get_room_details(hotel_id, search_key, auto_suggest_id, correlation_id, token)

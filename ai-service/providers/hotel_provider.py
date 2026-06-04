"""Provider interface — abstract base class for all hotel API interactions.

All concrete providers (real, mock) must implement this interface.
DTOs are never simplified — they match api/Hotel-Search-doc.md exactly.
"""
from abc import ABC, abstractmethod

from models.hotel import HotelDetailsResponse
from models.room import RoomDetailsResponse
from models.search import (
    AutoSuggestResponse,
    BackgroundStatusResponse,
    HotelSearchPayload,
    HotelSearchResponse,
)


class IHotelProvider(ABC):
    """Contract for all hotel API interactions.

    Both the real (Spring Boot) and mock providers implement this interface
    so that the LangGraph graph and routers are provider-agnostic.
    """

    @abstractmethod
    async def autosuggest(
        self,
        destination_keyword: str,
        correlation_id: str,
        token: str,
    ) -> AutoSuggestResponse:
        """Resolve a destination keyword to AutoSuggest identifiers."""
        ...

    @abstractmethod
    async def hotel_search(
        self,
        payload: HotelSearchPayload,
        correlation_id: str,
        token: str,
    ) -> HotelSearchResponse:
        """Trigger a hotel search and return searchKey + cacheKey."""
        ...

    @abstractmethod
    async def background_status(
        self,
        cache_key: str,
        search_key: str,
        auto_suggest_id: str,
        correlation_id: str,
        token: str,
    ) -> BackgroundStatusResponse:
        """Poll background processing status for a search session."""
        ...

    @abstractmethod
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
        """Fetch incremental hotel results from a completed poll batch."""
        ...

    @abstractmethod
    async def hotel_details(
        self,
        hotel_id: str,
        search_key: str,
        correlation_id: str,
        token: str,
    ) -> HotelDetailsResponse:
        """Fetch full hotel profile for a given hotelId."""
        ...

    @abstractmethod
    async def room_details(
        self,
        hotel_id: str,
        search_key: str,
        auto_suggest_id: str,
        correlation_id: str,
        token: str,
    ) -> RoomDetailsResponse:
        """Fetch available room categories for a given hotel."""
        ...

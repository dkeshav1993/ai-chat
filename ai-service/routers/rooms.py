"""Rooms router: GET /hotels/{hotelId}/rooms — fetch room details."""

import uuid
import structlog
from fastapi import APIRouter, HTTPException

from config import settings
from memory.session_memory import get_search_key, get_auto_suggest_id
from providers.factory import get_provider
from services.token_service import token_service
from models.errors import TraversiaError

logger = structlog.get_logger(__name__)

router = APIRouter(tags=["rooms"])


@router.get("/hotels/{hotel_id}/rooms")
async def get_rooms(hotel_id: str, session_id: str):
    """Return room details for the given hotelId.

    When USE_MOCK_PROVIDER=true, session keys are fetched from Redis but missing
    keys are tolerated — the mock provider does not need real search keys.
    When USE_MOCK_PROVIDER=false, both searchKey and autoSuggestId are required
    from the session (they were stored by trigger_search during the search flow).
    """
    correlation_id = str(uuid.uuid4())

    search_key = await get_search_key(session_id)
    auto_suggest_id = await get_auto_suggest_id(session_id)

    if not settings.USE_MOCK_PROVIDER:
        # Real provider: strict session check — keys must exist in Redis
        if not search_key or not auto_suggest_id:
            raise HTTPException(
                status_code=400,
                detail={
                    "success": False,
                    "code": "VALIDATION_ERROR",
                    "message": "Session not found or search keys expired. Please run a new search.",
                },
            )
    else:
        # Mock provider: use placeholder values when session data is absent
        # (e.g. developer navigates directly to rooms URL without a prior search)
        if not search_key:
            search_key = f"MOCK-SK-{hotel_id}"
        if not auto_suggest_id:
            auto_suggest_id = f"MOCK-AS-{hotel_id}"

    try:
        # Token is only required for the real provider
        token = None
        if not settings.USE_MOCK_PROVIDER:
            token = await token_service.get_token()

        result = await get_provider().room_details(
            hotel_id=hotel_id,
            search_key=search_key,
            auto_suggest_id=auto_suggest_id,
            correlation_id=correlation_id,
            token=token,
        )
    except TraversiaError as exc:
        logger.error("room_details_error", code=exc.code.value, hotel_id=hotel_id)
        raise HTTPException(status_code=502, detail=exc.to_dict()) from exc

    # Generate placeholder PG redirect URL for MVP
    pg_redirect_url = (
        f"https://booking.nextrip.ai/checkout"
        f"?hotelId={hotel_id}"
        f"&searchKey={search_key}"
        f"&autoSuggestId={auto_suggest_id}"
        f"&correlationId={correlation_id}"
    )

    return {
        "success": True,
        "capability": "ROOM_DETAILS",
        "data": {
            "roomData": result.roomData,
            "pgRedirectUrl": pg_redirect_url,
        },
    }

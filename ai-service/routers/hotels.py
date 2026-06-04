"""Hotels router: GET /hotels/{hotelId} - fetch hotel details."""

import uuid
import structlog
from fastapi import APIRouter, HTTPException

from config import settings
from memory.session_memory import get_search_key
from providers.factory import get_provider
from services.token_service import token_service
from models.errors import TraversiaError

logger = structlog.get_logger(__name__)

router = APIRouter(prefix="/hotels", tags=["hotels"])


@router.get("/{hotel_id}")
async def get_hotel(hotel_id: str, session_id: str):
    """Return hotel details for the given hotelId.

    When USE_MOCK_PROVIDER=true:
      - reads from mock JSON files via MockHotelProvider (no Redis required)
      - token fetch is skipped
    When USE_MOCK_PROVIDER=false:
      - validates searchKey from Redis (required)
      - fetches a bearer token, calls the real Spring Boot hotel details API
    """
    correlation_id = str(uuid.uuid4())

    logger.info(
        "hotel_detail_requested",
        hotel_id=hotel_id,
        session_id=session_id,
        mock_mode=settings.USE_MOCK_PROVIDER,
    )

    search_key = await get_search_key(session_id)

    if not settings.USE_MOCK_PROVIDER:
        # Real provider: strict session check
        if not search_key:
            raise HTTPException(
                status_code=400,
                detail={
                    "success": False,
                    "code": "VALIDATION_ERROR",
                    "message": "Session not found or search key expired. Please run a new search.",
                },
            )
    else:
        # Mock provider: use placeholder search key when session is absent
        if not search_key:
            search_key = f"MOCK-SK-{hotel_id}"

    try:
        # Token is only required for the real provider
        token = None
        if not settings.USE_MOCK_PROVIDER:
            token = await token_service.get_token()

        result = await get_provider().hotel_details(
            hotel_id=hotel_id,
            search_key=search_key,
            correlation_id=correlation_id,
            token=token,
        )
    except TraversiaError as exc:
        logger.error("hotel_details_error", code=exc.code.value, hotel_id=hotel_id)
        raise HTTPException(status_code=502, detail=exc.to_dict()) from exc

    logger.info("hotel_detail_success", hotel_id=hotel_id)

    return {
        "success": True,
        "capability": "HOTEL_DETAILS",
        "data": {
            "hotelData": result.hotelData,
            "searchKey": result.searchKey,
        },
    }

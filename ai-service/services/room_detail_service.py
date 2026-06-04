import structlog
import httpx

from config import settings
from models.room import RoomDetailsRequest, RoomDetailsResponse
from models.errors import TraversiaError, ErrorCode
from services.token_service import token_service
from utils.api_logger import log_request, log_response

logger = structlog.get_logger(__name__)

_ROOM_DETAILS_PATH = "/api/v1/room/getRoomDetails"


async def get_room_details(
    hotel_id: str,
    search_key: str,
    auto_suggest_id: str,
    correlation_id: str,
    token: str,
) -> RoomDetailsResponse:
    """Call POST /api/v1/room/getRoomDetails with filterBySupplier: [].

    Applies token-refresh-and-retry pattern on 401.

    Raises:
        TraversiaError: on any downstream failure.
    """
    async def _do_call(t: str) -> RoomDetailsResponse:
        return await _call_room_details(hotel_id, search_key, auto_suggest_id, correlation_id, t)

    try:
        return await _do_call(token)
    except TraversiaError as exc:
        if exc.code == ErrorCode.TOKEN_EXPIRED:
            return await token_service.refresh_and_retry(_do_call)
        raise


async def _call_room_details(
    hotel_id: str,
    search_key: str,
    auto_suggest_id: str,
    correlation_id: str,
    token: str,
) -> RoomDetailsResponse:
    """Internal: actual HTTP call to room details API."""
async def _call_room_details(
    hotel_id: str,
    search_key: str,
    auto_suggest_id: str,
    correlation_id: str,
    token: str,
) -> RoomDetailsResponse:
    """Internal: actual HTTP call to room details API."""
    request_body = RoomDetailsRequest(
        autoSuggestId=auto_suggest_id,
        filterBySupplier=[],
        hotelId=hotel_id,
        searchKey=search_key,
    )
    headers = {
    "Authorization": f"Bearer {token}",
    "Content-Type": "application/json",
    "Accept": "application/json",
    "User-Agent": "Mozilla/5.0",
}

    async with httpx.AsyncClient(base_url=settings.HOTEL_API_BASE_URL, timeout=20.0) as client:
        url = str(settings.HOTEL_API_BASE_URL).rstrip("/") + _ROOM_DETAILS_PATH
        start = log_request("POST", url, request_body.model_dump(), "ROOM_DETAILS", correlation_id, headers=headers)
        try:
            response = await client.post(
                _ROOM_DETAILS_PATH,
                json=request_body.model_dump(),
                headers=headers,
            )
        except httpx.TimeoutException as exc:
            raise TraversiaError(
                code=ErrorCode.DOWNSTREAM_TIMEOUT,
                message="Room details request timed out. Please try again.",
                recoverable=True,
                capability="ROOM_DETAILS",
            ) from exc
        except httpx.RequestError as exc:
            raise TraversiaError(
                code=ErrorCode.DOWNSTREAM_ERROR,
                message="Could not reach the room details service.",
                recoverable=True,
                capability="ROOM_DETAILS",
            ) from exc

    log_response("POST", url, response, start, "ROOM_DETAILS")
    _handle_http_errors(response, "ROOM_DETAILS", correlation_id)

    try:
        data = response.json()
        if data is None:
            raise TraversiaError(
                code=ErrorCode.DOWNSTREAM_NULL,
                message="Room details returned a null response.",
                recoverable=True,
                capability="ROOM_DETAILS",
            )
        result = RoomDetailsResponse(**data)
    except TraversiaError:
        raise
    except Exception as exc:
        raise TraversiaError(
            code=ErrorCode.DOWNSTREAM_ERROR,
            message="Room details returned an unexpected format.",
            recoverable=True,
            capability="ROOM_DETAILS",
        ) from exc

    logger.info("room_details_fetched", hotel_id=hotel_id, search_key=search_key)
    return result


def _handle_http_errors(response: httpx.Response, capability: str, correlation_id: str) -> None:
    if response.status_code == 400:
        raise TraversiaError(
            code=ErrorCode.VALIDATION_ERROR,
            message="Invalid room details request.",
            recoverable=True,
            capability=capability,
        )
    if response.status_code == 401:
        raise TraversiaError(
            code=ErrorCode.TOKEN_EXPIRED,
            message="Authentication token expired.",
            recoverable=True,
            capability=capability,
        )
    if response.status_code == 404:
        raise TraversiaError(
            code=ErrorCode.NO_RESULT,
            message="No rooms found for this hotel.",
            recoverable=False,
            capability=capability,
        )
    if response.status_code == 500:
        raise TraversiaError(
            code=ErrorCode.DOWNSTREAM_ERROR,
            message="Room details service encountered an error.",
            recoverable=True,
            capability=capability,
        )
    if response.status_code in (502, 504):
        raise TraversiaError(
            code=ErrorCode.DOWNSTREAM_TIMEOUT,
            message="Room details service is temporarily unavailable.",
            recoverable=True,
            capability=capability,
        )
    if response.status_code >= 400:
        raise TraversiaError(
            code=ErrorCode.DOWNSTREAM_ERROR,
            message="An unexpected error occurred fetching room details.",
            recoverable=True,
            capability=capability,
        )

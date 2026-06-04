import structlog
import httpx

from config import settings
from models.search import HotelSearchPayload, HotelSearchResponse
from models.errors import TraversiaError, ErrorCode
from services.token_service import token_service
from utils.api_logger import log_request, log_response

logger = structlog.get_logger(__name__)

_SEARCH_PATH = "/api/v1/hotels/search"


async def call_hotel_search(
    payload: HotelSearchPayload,
    correlation_id: str,
    token: str,
) -> HotelSearchResponse:
    """Call POST /api/v1/hotels/search and return parsed response.

    Applies token-refresh-and-retry pattern on 401.

    Raises:
        TraversiaError: on any downstream failure.
    """
    async def _do_call(t: str) -> HotelSearchResponse:
        return await _call_search(payload, correlation_id, t)

    try:
        return await _do_call(token)
    except TraversiaError as exc:
        if exc.code == ErrorCode.TOKEN_EXPIRED:
            return await token_service.refresh_and_retry(_do_call)
        raise


async def _call_search(
    payload: HotelSearchPayload,
    correlation_id: str,
    token: str,
) -> HotelSearchResponse:
    """Internal: actual HTTP call to hotel search API."""
    headers = {
    "Authorization": f"Bearer {token}",
    "Content-Type": "application/json",
    "Accept": "application/json",
    "User-Agent": "Mozilla/5.0",
}

    async with httpx.AsyncClient(base_url=settings.HOTEL_API_BASE_URL, timeout=30.0) as client:
        url = str(settings.HOTEL_API_BASE_URL).rstrip("/") + _SEARCH_PATH
        start = log_request("POST", url, payload.model_dump(), "HOTEL_SEARCH", correlation_id, headers=headers)
        try:
            response = await client.post(
                _SEARCH_PATH,
                json=payload.model_dump(),
                headers=headers,
            )
        except httpx.TimeoutException as exc:
            logger.error("search_timeout", correlation_id=correlation_id)
            raise TraversiaError(
                code=ErrorCode.DOWNSTREAM_TIMEOUT,
                message="Hotel search timed out. Please try again.",
                recoverable=True,
                capability="HOTEL_SEARCH",
            ) from exc
        except httpx.RequestError as exc:
            logger.error("search_request_error", error=str(exc))
            raise TraversiaError(
                code=ErrorCode.DOWNSTREAM_ERROR,
                message="Could not reach the hotel search service.",
                recoverable=True,
                capability="HOTEL_SEARCH",
            ) from exc

    log_response("POST", url, response, start, "HOTEL_SEARCH")
    _handle_http_errors(response, "HOTEL_SEARCH", correlation_id)

    try:
        data = response.json()
    except Exception as exc:
        raise TraversiaError(
            code=ErrorCode.DOWNSTREAM_NULL,
            message="Hotel search service returned an invalid response.",
            recoverable=True,
            capability="HOTEL_SEARCH",
        ) from exc

    if data is None:
        raise TraversiaError(
            code=ErrorCode.DOWNSTREAM_NULL,
            message="Hotel search returned a null response.",
            recoverable=True,
            capability="HOTEL_SEARCH",
        )

    try:
        result = HotelSearchResponse(**data)
    except Exception as exc:
        logger.error("search_parse_error", error=str(exc))
        raise TraversiaError(
            code=ErrorCode.DOWNSTREAM_ERROR,
            message="Hotel search returned an unexpected format.",
            recoverable=True,
            capability="HOTEL_SEARCH",
        ) from exc

    if not result.success:
        raise TraversiaError(
            code=ErrorCode.NO_RESULT,
            message="No hotels found for your search criteria.",
            recoverable=True,
            capability="HOTEL_SEARCH",
        )

    logger.info(
        "hotel_search_success",
        correlation_id=correlation_id,
        search_key=result.data.searchKey,
        cache_key=result.data.cacheKey,
    )
    return result


def _handle_http_errors(response: httpx.Response, capability: str, correlation_id: str) -> None:
    """Map HTTP status codes to typed TraversiaError exceptions."""
    if response.status_code == 400:
        raise TraversiaError(
            code=ErrorCode.VALIDATION_ERROR,
            message="Invalid hotel search request. Please check your dates and guest counts.",
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
            message="No hotels found for your search.",
            recoverable=True,
            capability=capability,
        )
    if response.status_code == 500:
        raise TraversiaError(
            code=ErrorCode.DOWNSTREAM_ERROR,
            message="The hotel search service encountered an error. Please try again.",
            recoverable=True,
            capability=capability,
        )
    if response.status_code in (502, 504):
        raise TraversiaError(
            code=ErrorCode.DOWNSTREAM_TIMEOUT,
            message="Hotel search service is temporarily unavailable.",
            recoverable=True,
            capability=capability,
        )
    if response.status_code >= 400:
        raise TraversiaError(
            code=ErrorCode.DOWNSTREAM_ERROR,
            message="An unexpected error occurred during hotel search.",
            recoverable=True,
            capability=capability,
        )

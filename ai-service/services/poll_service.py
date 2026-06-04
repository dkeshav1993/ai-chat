import structlog
import httpx

from config import settings
from models.search import (
    BackgroundStatusRequest,
    BackgroundStatusResponse,
    HotelSearchResponse,
    SearchByPollRequest,
)
from models.errors import TraversiaError, ErrorCode
from services.token_service import token_service
from utils.api_logger import log_request, log_response

logger = structlog.get_logger(__name__)

_BG_STATUS_PATH = "/api/v1/hotels/backgroundProcessStatus"
_SEARCH_BY_POLL_PATH = "/api/v1/hotels/search-by-poll"


async def check_background_status(
    cache_key: str,
    search_key: str,
    auto_suggest_id: str,
    correlation_id: str,
    token: str,
) -> BackgroundStatusResponse:
    """Call POST /api/v1/hotels/backgroundProcessStatus.

    Applies token-refresh-and-retry pattern on 401.

    Raises:
        TraversiaError: on any downstream failure.
    """
    async def _do_call(t: str) -> BackgroundStatusResponse:
        return await _call_background_status(cache_key, search_key, auto_suggest_id, correlation_id, t)

    try:
        return await _do_call(token)
    except TraversiaError as exc:
        if exc.code == ErrorCode.TOKEN_EXPIRED:
            return await token_service.refresh_and_retry(_do_call)
        raise


async def search_by_poll(
    search_key: str,
    cache_key: str,
    auto_suggest_id: str,
    correlation_id: str,
    token: str,
    check_in: str = "",
    check_out: str = "",
) -> HotelSearchResponse:
    """Call POST /api/v1/hotels/search-by-poll.

    Applies token-refresh-and-retry pattern on 401.

    Raises:
        TraversiaError: on any downstream failure.
    """
    async def _do_call(t: str) -> HotelSearchResponse:
        return await _call_search_by_poll(
            search_key, cache_key, auto_suggest_id, correlation_id, t,
            check_in=check_in, check_out=check_out,
        )

    try:
        return await _do_call(token)
    except TraversiaError as exc:
        if exc.code == ErrorCode.TOKEN_EXPIRED:
            return await token_service.refresh_and_retry(_do_call)
        raise


# ─── Internal helpers ─────────────────────────────────────────────────────────

async def _call_background_status(
    cache_key: str,
    search_key: str,
    auto_suggest_id: str,
    correlation_id: str,
    token: str,
) -> BackgroundStatusResponse:
    request_body = BackgroundStatusRequest(
        autoSuggestId=auto_suggest_id,
        cacheKey=cache_key,
        searchKey=search_key,
    )
    headers = {
    "Authorization": f"Bearer {token}",
    "Content-Type": "application/json",
    "Accept": "application/json",
    "User-Agent": "Mozilla/5.0",
}

    async with httpx.AsyncClient(base_url=settings.HOTEL_API_BASE_URL, timeout=15.0) as client:
        url = str(settings.HOTEL_API_BASE_URL).rstrip("/") + _BG_STATUS_PATH
        start = log_request("POST", url, request_body.model_dump(), "BACKGROUND_STATUS", correlation_id, headers=headers)
        try:
            response = await client.post(
                _BG_STATUS_PATH,
                json=request_body.model_dump(),
                headers=headers,
            )
        except httpx.TimeoutException as exc:
            raise TraversiaError(
                code=ErrorCode.DOWNSTREAM_TIMEOUT,
                message="Background status check timed out.",
                recoverable=True,
                capability="BACKGROUND_STATUS",
            ) from exc
        except httpx.RequestError as exc:
            raise TraversiaError(
                code=ErrorCode.DOWNSTREAM_ERROR,
                message="Could not reach the hotel service.",
                recoverable=True,
                capability="BACKGROUND_STATUS",
            ) from exc

    log_response("POST", url, response, start, "BACKGROUND_STATUS")
    _handle_http_errors(response, "BACKGROUND_STATUS", correlation_id)

    try:
        data = response.json()
        result = BackgroundStatusResponse(**data)
    except Exception as exc:
        raise TraversiaError(
            code=ErrorCode.DOWNSTREAM_NULL,
            message="Background status returned an invalid response.",
            recoverable=True,
            capability="BACKGROUND_STATUS",
        ) from exc

    logger.debug(
        "background_status_checked",
        in_progress=result.data.inProgress,
        correlation_id=correlation_id,
    )
    return result


async def _call_search_by_poll(
    search_key: str,
    cache_key: str,
    auto_suggest_id: str,
    correlation_id: str,
    token: str,
    check_in: str = "",
    check_out: str = "",
) -> HotelSearchResponse:
    request_body = SearchByPollRequest(
        autoSuggestId=auto_suggest_id,
        cacheKey=cache_key,
        capping_reached=False,
        checkIn=check_in,
        checkOut=check_out,
        hotelReceived=0,
        isSearchResultsProcessed=True,
        pageIndex=1,
        pageSize=300,
        searchKey=search_key,
    )
    headers = {
    "Authorization": f"Bearer {token}",
    "Content-Type": "application/json",
    "Accept": "application/json",
    "User-Agent": "Mozilla/5.0",
}

    async with httpx.AsyncClient(base_url=settings.HOTEL_API_BASE_URL, timeout=30.0) as client:
        url = str(settings.HOTEL_API_BASE_URL).rstrip("/") + _SEARCH_BY_POLL_PATH
        start = log_request("POST", url, request_body.model_dump(), "SEARCH_BY_POLL", correlation_id, headers=headers)
        try:
            response = await client.post(
                _SEARCH_BY_POLL_PATH,
                json=request_body.model_dump(),
                headers=headers,
            )
        except httpx.TimeoutException as exc:
            raise TraversiaError(
                code=ErrorCode.DOWNSTREAM_TIMEOUT,
                message="Hotel results fetch timed out.",
                recoverable=True,
                capability="SEARCH_BY_POLL",
            ) from exc
        except httpx.RequestError as exc:
            raise TraversiaError(
                code=ErrorCode.DOWNSTREAM_ERROR,
                message="Could not retrieve hotel results.",
                recoverable=True,
                capability="SEARCH_BY_POLL",
            ) from exc

    log_response("POST", url, response, start, "SEARCH_BY_POLL")
    _handle_http_errors(response, "SEARCH_BY_POLL", correlation_id)

    try:
        data = response.json()
        if data is None:
            raise TraversiaError(
                code=ErrorCode.DOWNSTREAM_NULL,
                message="Hotel results returned a null response.",
                recoverable=True,
                capability="SEARCH_BY_POLL",
            )
        result = HotelSearchResponse(**data)
    except TraversiaError:
        raise
    except Exception as exc:
        raise TraversiaError(
            code=ErrorCode.DOWNSTREAM_ERROR,
            message="Hotel results returned an unexpected format.",
            recoverable=True,
            capability="SEARCH_BY_POLL",
        ) from exc

    logger.info(
        "search_by_poll_success",
        correlation_id=correlation_id,
        hotel_count=len(result.data.hotels),
    )
    return result


def _handle_http_errors(response: httpx.Response, capability: str, correlation_id: str) -> None:
    """Map HTTP status codes to typed TraversiaError exceptions."""
    if response.status_code == 400:
        raise TraversiaError(
            code=ErrorCode.VALIDATION_ERROR,
            message="Invalid request for hotel polling.",
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
            message="No hotel results found.",
            recoverable=True,
            capability=capability,
        )
    if response.status_code == 500:
        raise TraversiaError(
            code=ErrorCode.DOWNSTREAM_ERROR,
            message="Hotel service encountered an error. Please try again.",
            recoverable=True,
            capability=capability,
        )
    if response.status_code in (502, 504):
        raise TraversiaError(
            code=ErrorCode.DOWNSTREAM_TIMEOUT,
            message="Hotel service is temporarily unavailable.",
            recoverable=True,
            capability=capability,
        )
    if response.status_code >= 400:
        raise TraversiaError(
            code=ErrorCode.DOWNSTREAM_ERROR,
            message="An unexpected error occurred.",
            recoverable=True,
            capability=capability,
        )

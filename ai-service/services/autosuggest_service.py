import structlog
import httpx

from config import settings
from models.search import AutoSuggestResponse
from models.errors import TraversiaError, ErrorCode
from services.token_service import token_service
from utils.api_logger import log_request, log_response

logger = structlog.get_logger(__name__)

_AUTOSUGGEST_PATH = "/api/v1/landing/fetchAutoSuggest"


async def call_autosuggest(
    destination_keyword: str,
    correlation_id: str,
    token: str,
) -> AutoSuggestResponse:
    """Call POST /api/v1/landing/fetchAutoSuggest and return parsed response.

    Applies token-refresh-and-retry pattern on 401.

    Raises:
        TraversiaError: on any downstream failure.
    """
    async def _do_call(t: str) -> AutoSuggestResponse:
        return await _call_autosuggest(destination_keyword, correlation_id, t)

    try:
        return await _do_call(token)
    except TraversiaError as exc:
        if exc.code == ErrorCode.TOKEN_EXPIRED:
            return await token_service.refresh_and_retry(_do_call)
        raise


async def _call_autosuggest(
    destination_keyword: str,
    correlation_id: str,
    token: str,
) -> AutoSuggestResponse:
    """Internal: actual HTTP call to autosuggest API."""
    request_body = {"autoSuggestKey": destination_keyword}

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "Accept": "application/json",
        "User-Agent": "Mozilla/5.0",
    }

    async with httpx.AsyncClient(base_url=settings.HOTEL_API_BASE_URL, timeout=15.0) as client:
        url = str(settings.HOTEL_API_BASE_URL).rstrip("/") + _AUTOSUGGEST_PATH
        start = log_request("POST", url, request_body, "AUTOSUGGEST", correlation_id, headers=headers)
        try:
            response = await client.post(
                _AUTOSUGGEST_PATH,
                json=request_body,
                headers=headers,
            )
        except httpx.TimeoutException as exc:
            logger.error("autosuggest_timeout", correlation_id=correlation_id)
            raise TraversiaError(
                code=ErrorCode.DOWNSTREAM_TIMEOUT,
                message="The hotel suggestion service timed out. Please try again.",
                recoverable=True,
                capability="AUTOSUGGEST",
            ) from exc
        except httpx.RequestError as exc:
            logger.error("autosuggest_request_error", error=str(exc))
            raise TraversiaError(
                code=ErrorCode.DOWNSTREAM_ERROR,
                message="Could not reach the hotel suggestion service.",
                recoverable=True,
                capability="AUTOSUGGEST",
            ) from exc

    log_response("POST", url, response, start, "AUTOSUGGEST")
    _handle_http_errors(response, "AUTOSUGGEST", correlation_id)

    try:
        data = response.json()
    except Exception as exc:
        raise TraversiaError(
            code=ErrorCode.DOWNSTREAM_NULL,
            message="Hotel suggestion service returned an invalid response.",
            recoverable=True,
            capability="AUTOSUGGEST",
        ) from exc

    if data is None:
        raise TraversiaError(
            code=ErrorCode.DOWNSTREAM_NULL,
            message="Hotel suggestion service returned a null response.",
            recoverable=True,
            capability="AUTOSUGGEST",
        )

    try:
        result = AutoSuggestResponse(**data)
    except Exception as exc:
        logger.error("autosuggest_parse_error", error=str(exc))
        raise TraversiaError(
            code=ErrorCode.DOWNSTREAM_ERROR,
            message="Hotel suggestion service returned an unexpected format.",
            recoverable=True,
            capability="AUTOSUGGEST",
        ) from exc

    if not result.success or not result.autoSuggests:
        msg = result.message.lower() if result.message else ""
        if "no matching" in msg or "no suggestion" in msg or not result.autoSuggests:
            raise TraversiaError(
                code=ErrorCode.NO_AUTOSUGGEST_RESULT,
                message=f"No destinations found for '{destination_keyword}'. Please try a different city name.",
                recoverable=True,
                capability="AUTOSUGGEST",
            )

    logger.info(
        "autosuggest_success",
        correlation_id=correlation_id,
        result_count=len(result.autoSuggests),
        auto_suggest_id=result.autoSuggestId,
    )
    return result


def _handle_http_errors(response: httpx.Response, capability: str, correlation_id: str) -> None:
    """Map HTTP status codes to typed TraversiaError exceptions."""
    if response.status_code == 400:
        raise TraversiaError(
            code=ErrorCode.VALIDATION_ERROR,
            message="Invalid search request. Please check your destination and dates.",
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
            message="No results found for your search.",
            recoverable=True,
            capability=capability,
        )
    if response.status_code == 500:
        raise TraversiaError(
            code=ErrorCode.DOWNSTREAM_ERROR,
            message="The hotel service encountered an error. Please try again.",
            recoverable=True,
            capability=capability,
        )
    if response.status_code in (502, 504):
        raise TraversiaError(
            code=ErrorCode.DOWNSTREAM_TIMEOUT,
            message="The hotel service is temporarily unavailable.",
            recoverable=True,
            capability=capability,
        )
    if response.status_code >= 400:
        raise TraversiaError(
            code=ErrorCode.DOWNSTREAM_ERROR,
            message="An unexpected error occurred with the hotel service.",
            recoverable=True,
            capability=capability,
        )

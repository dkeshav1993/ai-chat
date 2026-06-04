import structlog
from typing import Callable, Any, Awaitable
import httpx
import redis.asyncio as aioredis

from config import settings
from memory.redis_client import get_redis_client, token_key
from models.errors import TraversiaError, ErrorCode
from utils.api_logger import log_request, log_response

logger = structlog.get_logger(__name__)

_TOKEN_TTL = 360  # 6 minutes — API tokens expire in ~420s; cache slightly less to prevent stale token

# Token API lives on the root domain — NOT under /hotels-search
# e.g. base = "https://travelonedev-services.thomascook.in/hotels-search"
# → root = "https://travelonedev-services.thomascook.in"
def _token_api_root() -> str:
    base = str(settings.HOTEL_API_BASE_URL).rstrip("/")
    # Strip known path suffixes so we always land on the root origin
    for suffix in ("/hotels-search", "/hotels-search-prod"):
        if base.endswith(suffix):
            return base[: -len(suffix)]
    return base


class TokenService:
    """Singleton service that manages the Bearer token lifecycle.

    - On cache miss: calls the Token API and stores the token in Redis.
    - On 401 / token expiry: force-refreshes and retries the original call once.
    - Credentials come exclusively from config.py (env vars).
    - NOTE: Token API is on the ROOT domain; hotel APIs are under /hotels-search.
    """

    _instance: "TokenService | None" = None

    def __new__(cls) -> "TokenService":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._redis: aioredis.Redis = get_redis_client()
            # Separate client for token API (root domain, no /hotels-search prefix)
            cls._instance._token_http: httpx.AsyncClient = httpx.AsyncClient(
                base_url=_token_api_root(),
                timeout=30.0,
            )
        return cls._instance

    # ─── Public API ──────────────────────────────────────────────────────────

    async def get_token(self) -> str:
        """Return a valid Bearer token, fetching from Redis cache first."""
        cached = await self._redis.get(token_key())
        if cached:
            logger.debug("token_cache_hit")
            return str(cached)
        return await self._fetch_and_cache()

    async def refresh_and_retry(
        self,
        call: Callable[..., Awaitable[Any]],
    ) -> Any:
        """Force-refresh the token then retry *call* with the fresh token.

        If the retry also fails, the exception propagates to the caller.
        call must accept a single positional argument: the new token string.
        """
        logger.info("token_refresh_triggered")
        new_token = await self._fetch_and_cache(force=True)
        try:
            return await call(new_token)
        except Exception as exc:
            logger.error("token_refresh_retry_failed", error=str(exc))
            raise TraversiaError(
                code=ErrorCode.TOKEN_REFRESH_FAILED,
                message="Token refresh failed. Please try again.",
                recoverable=True,
            ) from exc

    # ─── Internal ────────────────────────────────────────────────────────────

    async def _fetch_and_cache(self, force: bool = False) -> str:
        """Call the Token API, store the result in Redis, and return the token."""
        if force:
            await self._redis.delete(token_key())

        token_path = "/authenticationserver/authenticationService/generateToken"
        token_url = _token_api_root() + token_path
        req_headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "User-Agent": "Mozilla/5.0",
        }
        body = {
            "moduleID": settings.HOTEL_API_MODULE_ID,
            "userName": settings.HOTEL_API_USERNAME,
            "password": "***",  # masked in logs
        }
        start = log_request("POST", token_url, body, "TOKEN", headers=req_headers)

        # Restore real password for the actual request
        actual_body = {
            "moduleID": settings.HOTEL_API_MODULE_ID,
            "userName": settings.HOTEL_API_USERNAME,
            "password": settings.HOTEL_API_PASSWORD,
        }
        try:
            response = await self._token_http.post(
                token_path,
                json=actual_body,
                headers=req_headers,
            )
            log_response("POST", token_url, response, start, "TOKEN")
            response.raise_for_status()
            data = response.json()
        except httpx.HTTPStatusError as exc:
            logger.error("token_api_http_error", status=exc.response.status_code)
            raise TraversiaError(
                code=ErrorCode.TOKEN_REFRESH_FAILED,
                message="Unable to authenticate with the hotel service.",
                recoverable=False,
            ) from exc
        except httpx.RequestError as exc:
            logger.error("token_api_request_error", error=str(exc))
            raise TraversiaError(
                code=ErrorCode.DOWNSTREAM_ERROR,
                message="Could not reach the hotel service.",
                recoverable=True,
            ) from exc

        token_value: str = data.get("token", "")
        token_valid: bool = data.get("tokenValid", False)

        if not token_value:
            raise TraversiaError(
                code=ErrorCode.TOKEN_REFRESH_FAILED,
                message="Token API returned an empty token.",
                recoverable=False,
            )
        if not token_valid:
            logger.warning("token_api_returned_invalid_token", tokenValid=token_valid)
            raise TraversiaError(
                code=ErrorCode.TOKEN_REFRESH_FAILED,
                message="Token API returned an invalid token (tokenValid=false).",
                recoverable=False,
            )

        await self._redis.set(token_key(), token_value, ex=_TOKEN_TTL)
        logger.info("token_fetched_and_cached", token_valid=token_valid)
        return token_value


# Module-level singleton
token_service = TokenService()

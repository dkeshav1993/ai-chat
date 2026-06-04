import redis.asyncio as aioredis
from config import settings


def get_redis_client() -> aioredis.Redis:
    """Create and return an async Redis client from the configured REDIS_URL."""
    return aioredis.from_url(settings.REDIS_URL, decode_responses=True)


# ─── Key Helpers ──────────────────────────────────────────────────────────────

def token_key() -> str:
    """Redis key for the shared Bearer token."""
    return "traversia:token"


def session_memory_key(session_id: str) -> str:
    """Redis key for a session's conversational memory (chat turns)."""
    return f"traversia:session:{session_id}:memory"


def session_poll_key(session_id: str) -> str:
    """Redis key for a session's polling state (searchKey / cacheKey / autoSuggestId)."""
    return f"traversia:session:{session_id}:poll"

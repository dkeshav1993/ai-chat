from typing import Optional

from memory.redis_client import get_redis_client, session_poll_key


async def get_search_key(session_id: str) -> Optional[str]:
    """Return the searchKey stored in the session poll hash, or None."""
    redis = get_redis_client()
    key = session_poll_key(session_id)
    value = await redis.hget(key, "searchKey")
    return value  # type: ignore[return-value]


async def get_auto_suggest_id(session_id: str) -> Optional[str]:
    """Return the autoSuggestId stored in the session poll hash, or None."""
    redis = get_redis_client()
    key = session_poll_key(session_id)
    value = await redis.hget(key, "autoSuggestId")
    return value  # type: ignore[return-value]


async def get_poll_state(session_id: str) -> Optional[dict]:
    """Return the full poll state dict for a session, or None."""
    redis = get_redis_client()
    key = session_poll_key(session_id)
    data = await redis.hgetall(key)
    if not data:
        return None
    return dict(data)

import structlog
from typing import Optional

from memory.redis_client import get_redis_client, session_poll_key

logger = structlog.get_logger(__name__)

_POLL_STATE_TTL = 86400  # 24 hours


async def save_poll_state(session_id: str, state_dict: dict) -> None:
    """Persist the full poll state hash for a session in Redis (TTL 86400s)."""
    redis = get_redis_client()
    key = session_poll_key(session_id)
    await redis.hset(key, mapping={k: str(v) for k, v in state_dict.items()})
    await redis.expire(key, _POLL_STATE_TTL)
    logger.debug("poll_state_saved", session_id=session_id, fields=list(state_dict.keys()))


async def get_poll_state(session_id: str) -> Optional[dict]:
    """Return the full poll state dict for a session, or None if not found."""
    redis = get_redis_client()
    key = session_poll_key(session_id)
    data = await redis.hgetall(key)
    if not data:
        return None
    return dict(data)


async def update_poll_iteration(session_id: str) -> None:
    """Atomically increment the poll iteration counter for a session."""
    redis = get_redis_client()
    key = session_poll_key(session_id)
    await redis.hincrby(key, "pollIteration", 1)
    await redis.expire(key, _POLL_STATE_TTL)
    logger.debug("poll_iteration_updated", session_id=session_id)


async def clear_poll_state(session_id: str) -> None:
    """Delete the poll state key for a session."""
    redis = get_redis_client()
    key = session_poll_key(session_id)
    await redis.delete(key)
    logger.debug("poll_state_cleared", session_id=session_id)

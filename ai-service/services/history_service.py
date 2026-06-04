import structlog
from dataclasses import dataclass
from typing import Optional

logger = structlog.get_logger(__name__)


@dataclass
class SearchHistoryRecord:
    session_id: str
    destination: str
    destination_type: str
    unique_identifier: str
    check_in: str
    check_out: str
    adult_count: int = 1
    child_count: int = 0
    room_count: int = 1
    auto_suggest_id: Optional[str] = None
    search_key: Optional[str] = None


async def write_search_history(record: SearchHistoryRecord, pool=None) -> None:
    """Async INSERT of a search history record.

    Catches ALL exceptions and logs them — never re-raises.
    This function is always called via asyncio.create_task() (fire-and-forget).
    """
    try:
        # Import here to avoid circular dependency issues at module load time
        if pool is None:
            # Attempt to get pool from app state if not explicitly provided
            try:
                from main import app
                pool = getattr(app.state, "db_pool", None)
            except Exception:
                pool = None

        if pool is None:
            logger.warning("search_history_skipped_no_pool", session_id=record.session_id)
            return

        sql = """
            INSERT INTO search_history (
                session_id, destination, destination_type, unique_identifier,
                check_in, check_out, adult_count, child_count, room_count,
                auto_suggest_id, search_key
            ) VALUES (
                %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
            )
        """
        values = (
            record.session_id,
            record.destination,
            record.destination_type,
            record.unique_identifier,
            record.check_in,
            record.check_out,
            record.adult_count,
            record.child_count,
            record.room_count,
            record.auto_suggest_id,
            record.search_key,
        )

        async with pool.acquire() as conn:
            async with conn.cursor() as cur:
                await cur.execute(sql, values)

        logger.info(
            "search_history_written",
            session_id=record.session_id,
            destination=record.destination,
        )
    except Exception as exc:
        # Never re-raise — this is fire-and-forget
        logger.error(
            "search_history_write_failed",
            session_id=record.session_id,
            error=str(exc),
        )

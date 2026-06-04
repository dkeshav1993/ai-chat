import aiomysql
import structlog
from typing import Optional

from config import settings

logger = structlog.get_logger(__name__)


async def create_pool() -> aiomysql.Pool:
    """Create and return an async aiomysql connection pool.

    Pool min=2, max=10. Should be stored in app.state.db_pool at startup.
    """
    pool = await aiomysql.create_pool(
        host=settings.MYSQL_HOST,
        port=settings.MYSQL_PORT,
        user=settings.MYSQL_USER,
        password=settings.MYSQL_PASSWORD,
        db=settings.MYSQL_DB,
        minsize=2,
        maxsize=10,
        autocommit=True,
        charset="utf8mb4",
    )
    logger.info("mysql_pool_created", host=settings.MYSQL_HOST, db=settings.MYSQL_DB)
    return pool

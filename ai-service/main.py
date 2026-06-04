import structlog
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Configure logging FIRST — redirects all output (structlog + stdlib + uvicorn)
# to the external rolling log file. Nothing is printed to the terminal.
from logging_config import configure_logging
configure_logging()

from config import settings
from routers import chat, hotels, rooms

logger = structlog.get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):

    # Startup: eagerly populate Redis token cache
    if settings.USE_MOCK_PROVIDER:
        logger.info("mock_provider_enabled_skipping_token_fetch")
    else:
        try:
            from services.token_service import token_service
            from memory.redis_client import get_redis_client, token_key

            # Always flush the cached token on startup — forces a fresh fetch
            # so stale/expired tokens from a previous run never cause 401s.
            redis = get_redis_client()
            await redis.delete(token_key())
            logger.info("startup_stale_token_cleared")

            token = await token_service.get_token()

            logger.info(
                "startup_token_fetch_success",
                token_length=len(token)
            )

        except Exception as exc:
            logger.error(
                "startup_token_fetch_failed",
                error=str(exc)
            )

    # Startup: create MySQL connection pool
    try:
        from db.mysql_client import create_pool

        app.state.db_pool = await create_pool()

        logger.info("startup_mysql_pool_created")

    except Exception as exc:
        logger.warning(
            "startup_mysql_pool_failed",
            error=str(exc)
        )

        app.state.db_pool = None

    yield

    # Shutdown: close MySQL pool
    if getattr(app.state, "db_pool", None):
        app.state.db_pool.close()
        await app.state.db_pool.wait_closed()

        logger.info("shutdown_mysql_pool_closed")


app = FastAPI(
    title="NexTrip AI Service",
    description="AI-orchestrated hotel discovery platform",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(chat.router)
app.include_router(hotels.router)
app.include_router(rooms.router)


@app.get("/")
async def root():
    return {
        "service": "NexTrip AI Service",
        "status": "UP",
        "mockProvider": settings.USE_MOCK_PROVIDER,
        "environment": settings.ENVIRONMENT
        if hasattr(settings, "ENVIRONMENT")
        else "local",
    }


@app.get("/health")
async def health():
    return {
        "status": "ok",
        "mockProvider": settings.USE_MOCK_PROVIDER,
    }
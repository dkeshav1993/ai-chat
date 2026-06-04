"""Provider factory — returns the active IHotelProvider based on configuration.

Usage:
    from providers.factory import get_provider
    provider = get_provider()

Environment variables:
    USE_MOCK_PROVIDER=true   → MockHotelProvider
    USE_MOCK_PROVIDER=false  → RealHotelProvider (default)
    MOCK_SCENARIO=success|timeout|empty|downstream_error
"""
import structlog

from config import settings
from providers.hotel_provider import IHotelProvider

logger = structlog.get_logger(__name__)

_provider_instance: IHotelProvider | None = None


def get_provider() -> IHotelProvider:
    """Return a singleton provider.  Safe to call repeatedly.

    Cached after first resolution so config is read once at startup.
    """
    global _provider_instance
    if _provider_instance is not None:
        return _provider_instance

    if settings.USE_MOCK_PROVIDER:
        from providers.mock_provider import MockHotelProvider
        _provider_instance = MockHotelProvider()
        logger.info(
            "provider.active",
            provider="MockHotelProvider",
            scenario=settings.MOCK_SCENARIO,
        )
    else:
        from providers.real_provider import RealHotelProvider
        _provider_instance = RealHotelProvider()
        logger.info("provider.active", provider="RealHotelProvider")

    return _provider_instance

from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )

    # Spring Boot Hotel API DEV environment credentials and config
    HOTEL_API_BASE_URL: str = "https://travelonedev-services.thomascook.in/hotels-search"
    HOTEL_API_MODULE_ID: str = "Traversia"
    HOTEL_API_USERNAME: str = "traversia"
    HOTEL_API_PASSWORD: str = "Traversia@123"

    # Spring Boot Hotel API PROD environment credentials and config
    # HOTEL_API_BASE_URL: str = "https://travelone-services.thomascook.in"
    # HOTEL_API_MODULE_ID: str = "TRAVERSIA"
    # HOTEL_API_USERNAME: str = "TRAVERSIA_USER"
    # HOTEL_API_PASSWORD: str = "VSRlI1J0KkB2ZXIkaUB0YyhpbF9ASG5z"

    # Redis
    REDIS_URL: str = "redis://localhost:6379"

    # MySQL
    MYSQL_HOST: str = "localhost"
    MYSQL_PORT: int = 3308
    MYSQL_DB: str = "traversia"
    MYSQL_USER: str = "traversia"
    MYSQL_PASSWORD: str = "traversia_local"

    # OpenAI
    OPENAI_API_KEY: str = ""
    OPENAI_MODEL: str = "gpt-4.1-mini"

    # Polling
    POLL_TIMEOUT_SECONDS: int = 20
    POLL_INTERVAL_SECONDS: int = 2

    # Mock provider — set USE_MOCK_PROVIDER=true for local/offline development
    USE_MOCK_PROVIDER: bool = False
    MOCK_SCENARIO: str = "success"  # success | timeout | empty | downstream_error

    # Mock AI
    USE_FAKE_AI: bool = False

    # GeoNames API for nearby cities (free — https://www.geonames.org/login)
    GEONAMES_USERNAME: str = "demo"


settings = Settings()

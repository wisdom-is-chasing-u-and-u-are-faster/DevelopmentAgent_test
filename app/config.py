"""
Application Configuration
"""
from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field


class Settings(BaseSettings):
    PROJECT_NAME: str = "Carbon Footprint Engine API"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"

    # Database
    DATABASE_URL: str = Field(default="sqlite:///./carbon_ledger.db")

    # Redis Cache (falls back to memory if None)
    REDIS_URL: Optional[str] = None
    CACHE_DEFAULT_TTL: int = 86400  # 24 hours

    # Patch API
    PATCH_API_KEY: str = Field(default="test_patch_key_123")
    PATCH_API_URL: str = Field(default="https://api.patch.io/v1")
    OFFSET_RATE_USD_PER_METRIC_TON: float = 30.00  # $30 per 1,000 kg ($0.03/kg)

    # Auth
    API_BEARER_TOKEN: str = "test-secret-token"
    RATE_LIMIT_PER_MINUTE: int = 100

    model_config = SettingsConfigDict(env_file=".env", extra="allow")


settings = Settings()

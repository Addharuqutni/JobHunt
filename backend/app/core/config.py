"""
Application configuration using Pydantic Settings.
Centralizes all environment-based configuration with validation.
"""
import logging
from functools import lru_cache
from typing import List

from pydantic import field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

logger = logging.getLogger(__name__)

# Default API key only allowed in development
_DEV_DEFAULT_API_KEY = "dev-secret-key-123"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # API Settings
    API_KEY: str = _DEV_DEFAULT_API_KEY
    APP_ENV: str = "development"
    FRONTEND_URL: str = "http://localhost:5173"
    CORS_ORIGINS: str = "http://localhost:5173,http://127.0.0.1:5173"

    # Database Settings - PostgreSQL
    POSTGRES_USER: str = "jobsentinel"
    POSTGRES_PASSWORD: str = "jobsentinel123"
    POSTGRES_HOST: str = "localhost"
    POSTGRES_PORT: str = "5432"
    POSTGRES_DB: str = "jobsentinel"

    # Redis / Celery Settings
    USE_REDIS: str = "false"
    REDIS_URL: str = "redis://localhost:6379/0"
    CELERY_BROKER_URL: str = "redis://localhost:6379/0"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/0"

    # Telegram (optional, configured via dashboard)
    TELEGRAM_BOT_TOKEN: str = ""
    TELEGRAM_CHAT_ID: str = ""

    @field_validator("APP_ENV")
    @classmethod
    def normalize_app_env(cls, value: str) -> str:
        """Normalize app environment names so downstream checks stay consistent."""
        return value.strip().lower()

    @model_validator(mode="after")
    def validate_production_secrets(self) -> "Settings":
        """
        Reject insecure defaults when running in production.
        Prevents accidental deployment with dev credentials.
        """
        if self.APP_ENV == "production":
            if self.API_KEY == _DEV_DEFAULT_API_KEY:
                raise ValueError(
                    "API_KEY must be set to a strong secret in production. "
                    "Do not use the default dev key."
                )
            if self.POSTGRES_PASSWORD == "jobsentinel123":
                raise ValueError(
                    "POSTGRES_PASSWORD must be changed from the default in production."
                )
        return self

    @property
    def is_development(self) -> bool:
        """Check if running in development mode."""
        return self.APP_ENV in {"development", "dev", "local"}

    @property
    def DB_URL(self) -> str:
        """Construct PostgreSQL connection URL from components."""
        return (
            f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
            f"@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )

    @property
    def cors_origins_list(self) -> List[str]:
        """Return normalized frontend origins allowed to call the API from browsers."""
        origins = [
            origin.strip().rstrip("/")
            for origin in self.CORS_ORIGINS.split(",")
            if origin.strip()
        ]
        frontend_url = self.FRONTEND_URL.strip().rstrip("/")
        if frontend_url and frontend_url not in origins:
            origins.append(frontend_url)
        return origins

    @property
    def redis_enabled(self) -> bool:
        """Convert USE_REDIS string env values into a safe boolean flag."""
        return self.USE_REDIS.lower() in {"1", "true", "yes", "on"}


@lru_cache
def get_settings() -> Settings:
    """Return cached settings instance so environment parsing happens once per process."""
    return Settings()


settings = get_settings()

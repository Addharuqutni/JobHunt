import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # API Settings
    API_KEY: str = "dev-secret-key-123"
    
    # Database Settings
    # Default to a local SQLite database for development if POSTGRES_URL isn't set
    DB_URL: str = os.environ.get(
        "DB_URL", 
        f"sqlite:///{os.path.join(os.path.dirname(os.path.dirname(__file__)), 'jobs.db')}"
    )

    # Redis / Celery Settings
    REDIS_URL: str = os.environ.get("REDIS_URL", "redis://localhost:6379/0")
    CELERY_BROKER_URL: str = os.environ.get("CELERY_BROKER_URL", "redis://localhost:6379/0")
    CELERY_RESULT_BACKEND: str = os.environ.get("CELERY_RESULT_BACKEND", "redis://localhost:6379/0")

    class Config:
        env_file = ".env"

settings = Settings()

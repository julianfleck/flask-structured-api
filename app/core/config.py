from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache


class Settings(BaseSettings):
    # API Settings
    API_VERSION: str = "1.0.0"
    API_DEBUG: bool = False
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 5000
    ENVIRONMENT: str = "development"

    # Database
    DATABASE_URL: str
    DB_POOL_SIZE: int = 20

    # Redis
    REDIS_URL: str
    REDIS_MAX_CONNECTIONS: int = 100

    # Security
    SECRET_KEY: str
    JWT_SECRET_KEY: str
    CORS_ORIGINS: str = "*"
    ALLOWED_HOSTS: str = "*"

    # Rate Limiting
    RATE_LIMIT_ENABLED: bool = True
    RATE_LIMIT_DEFAULT: int = 60  # requests per minute
    RATE_LIMIT_WINDOW: int = 3600  # time window in seconds

    # AI Service
    AI_PROVIDER: Optional[str] = "openai"  # or 'azure', 'anthropic'
    AI_API_KEY: Optional[str] = None
    AI_MODEL: str = "gpt-4"
    AI_MAX_TOKENS: int = 2000
    AI_TEMPERATURE: float = 0.7

    # Optional Provider-Specific Settings
    AI_AZURE_ENDPOINT: Optional[str] = None
    AI_ANTHROPIC_VERSION: Optional[str] = None

    # Background Tasks
    CELERY_BROKER_URL: Optional[str] = None
    CELERY_RESULT_BACKEND: Optional[str] = None
    CELERY_TASK_DEFAULT_QUEUE: str = "default"

    # Performance
    GUNICORN_WORKERS: int = 4
    GUNICORN_THREADS: int = 2

    # Monitoring
    LOG_LEVEL: str = "INFO"
    SENTRY_DSN: Optional[str] = None
    PROMETHEUS_ENABLED: bool = False

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True
    )


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance"""
    return Settings()


# Create a global settings instance
settings = get_settings()

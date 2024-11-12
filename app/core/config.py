from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # API Settings
    API_NAME: str = "Flask AI API Boilerplate"
    API_VERSION: str = "1.0.0"
    API_DEBUG: bool = False
    API_HOST: str = "${API_HOST}"
    API_PORT: int = "${API_PORT}"
    ENVIRONMENT: str = "development"
    FLASK_APP: str = "app.main:create_app"
    FLASK_ENV: str = "development"

    # Database
    DATABASE_URL: str = "sqlite:///./test.db"
    DB_POOL_SIZE: int = 20

    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"
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

    # Database Backups
    BACKUP_SCHEDULE: str = "@daily"  # Cron schedule expression
    BACKUP_KEEP_DAYS: int = 7
    BACKUP_KEEP_WEEKS: int = 4
    BACKUP_KEEP_MONTHS: int = 6
    BACKUP_COMPRESSION: bool = True

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="allow",
        env_nested_delimiter="__",
        # Force environment variable reload
        env_prefix="",
        use_enum_values=True,
    )


def get_settings() -> Settings:
    """Get settings instance"""
    return Settings()


# Create a global settings instance
settings = get_settings()

# Add debug print to verify settings
print(
    f"🔧 Loaded settings - API_PORT: {settings.API_PORT}, API_HOST: {settings.API_HOST}")

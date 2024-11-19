from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field


class Settings(BaseSettings):
    # API Settings
    API_NAME: str = "Flask AI API Boilerplate"
    API_VERSION: str = "1.0.0"  # This will be used for endpoint normalization
    API_VERSION_PREFIX: str = "v1"
    API_DEBUG: bool = False
    API_HOST: str = "${API_HOST}"
    API_PORT: int = "${API_PORT}"
    ENVIRONMENT: str = "development"
    FLASK_APP: str = "app.main:create_app"
    FLASK_ENV: str = "development"

    # PostgreSQL Settings
    POSTGRES_HOST: str = "db"
    POSTGRES_USER: str = "user"
    POSTGRES_PASSWORD: str = "password"
    POSTGRES_DB: str = "api"
    POSTGRES_PORT: int = 5432

    # Database URL constructed from PostgreSQL settings
    @property
    def DATABASE_URL(self) -> str:
        return f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"

    # Database
    DB_POOL_SIZE: int = 20

    # Redis
    REDIS_URL: str = Field(..., env="REDIS_URL")
    REDIS_MAX_CONNECTIONS: int = 100

    # Security
    SECRET_KEY: str
    CORS_ORIGINS: str = "*"
    ALLOWED_HOSTS: str = "*"

    # JWT Settings
    JWT_SECRET_KEY: str = Field(..., env="JWT_SECRET_KEY")
    JWT_REFRESH_SECRET_KEY: str = Field(..., env="JWT_REFRESH_SECRET_KEY")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(
        default=30, env="ACCESS_TOKEN_EXPIRE_MINUTES")
    REFRESH_TOKEN_EXPIRE_MINUTES: int = Field(
        default=10080, env="REFRESH_TOKEN_EXPIRE_MINUTES")  # 7 days

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

    # API Key Settings
    MAX_API_KEYS_PER_USER: int = 5
    API_KEY_PREFIX: str = "sk_"  # For identifying API keys

    # Storage settings
    STORAGE_SESSION_TIMEOUT: int = 30  # minutes

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

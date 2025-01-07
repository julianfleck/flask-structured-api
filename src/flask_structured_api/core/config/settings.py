from typing import Optional

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # API Settings
    API_NAME: str = Field("Flask Structured API Boilerplate", env="API_NAME")
    API_VERSION: str = Field("1.0.0", env="API_VERSION")
    API_VERSION_PREFIX: str = Field("v1", env="API_VERSION_PREFIX")
    API_DEBUG: bool = Field(False, env="API_DEBUG")
    API_HOST: str = Field("localhost", env="API_HOST")
    API_PORT: int = Field(8000, env="API_PORT")
    ENVIRONMENT: str = Field("development", env="ENVIRONMENT")
    FLASK_APP: str = Field("app.main:create_flask_app", env="FLASK_APP")
    FLASK_ENV: str = Field("development", env="FLASK_ENV")

    # PostgreSQL Settings
    POSTGRES_HOST: str = Field("localhost", env="POSTGRES_HOST")
    POSTGRES_USER: str = Field("user", env="POSTGRES_USER")
    POSTGRES_PASSWORD: str = Field("password", env="POSTGRES_PASSWORD")
    POSTGRES_DB: str = Field("api", env="POSTGRES_DB")
    POSTGRES_PORT: int = Field(5432, env="POSTGRES_PORT")

    # Database URL constructed from PostgreSQL settings
    @property
    def DATABASE_URL(self) -> str:
        return f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"

    # Database
    DB_POOL_SIZE: int = Field(20, env="DB_POOL_SIZE")

    # Redis
    REDIS_URL: str = Field(..., env="REDIS_URL")
    REDIS_MAX_CONNECTIONS: int = 100

    # Security
    SECRET_KEY: str = Field(..., env="SECRET_KEY")
    CORS_ORIGINS: str = Field("*", env="CORS_ORIGINS")
    ALLOWED_HOSTS: str = Field("*", env="ALLOWED_HOSTS")

    # JWT Settings
    JWT_SECRET_KEY: str = Field(..., env="JWT_SECRET_KEY")
    JWT_REFRESH_SECRET_KEY: str = Field(..., env="JWT_REFRESH_SECRET_KEY")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(
        default=30, env="ACCESS_TOKEN_EXPIRE_MINUTES"
    )
    REFRESH_TOKEN_EXPIRE_MINUTES: int = Field(
        default=10080, env="REFRESH_TOKEN_EXPIRE_MINUTES"
    )  # 7 days

    # Rate Limiting
    RATE_LIMIT_ENABLED: bool = True
    RATE_LIMIT_DEFAULT: int = 60  # requests per minute
    RATE_LIMIT_WINDOW: int = 3600  # time window in seconds

    # AI Service
    AI_PROVIDER: Optional[str] = Field("openai", env="AI_PROVIDER")
    AI_API_KEY: Optional[str] = Field(None, env="AI_API_KEY")
    AI_MODEL: str = Field("gpt-4o", env="AI_MODEL")
    AI_MAX_TOKENS: int = Field(3000, env="AI_MAX_TOKENS")
    AI_TEMPERATURE: float = Field(0.1, env="AI_TEMPERATURE")

    # Optional Provider-Specific Settings

    # OPENAI
    AI_OPENAI_API_KEY: Optional[str] = Field(None, env="AI_OPENAI_API_KEY")
    AI_OPENAI_MODEL: str = Field("gpt-4o", env="AI_OPENAI_MODEL")

    # Azure
    AI_AZURE_API_KEY: Optional[str] = Field(None, env="AI_AZURE_API_KEY")
    AI_AZURE_MODEL: str = Field("gpt-4", env="AI_AZURE_MODEL")
    AI_AZURE_ENDPOINT: str = Field(
        "https://your-resource.openai.azure.com/", env="AI_AZURE_ENDPOINT")
    AI_AZURE_DEPLOYMENT: str = Field("your-deployment", env="AI_AZURE_DEPLOYMENT")
    AI_AZURE_API_VERSION: str = Field("2024-02-15-preview", env="AI_AZURE_API_VERSION")

    # Anthropic
    AI_ANTHROPIC_API_KEY: Optional[str] = Field(None, env="AI_ANTHROPIC_API_KEY")
    AI_ANTHROPIC_MODEL: str = Field("claude-3.5-sonnet", env="AI_ANTHROPIC_MODEL")

    # Background Tasks
    CELERY_BROKER_URL: Optional[str] = None
    CELERY_RESULT_BACKEND: Optional[str] = None
    CELERY_TASK_DEFAULT_QUEUE: str = "default"

    # Performance
    GUNICORN_WORKERS: int = 4
    GUNICORN_THREADS: int = 2

    # Monitoring
    @property
    def LOG_LEVEL(self) -> str:
        if self.ENVIRONMENT.lower() in ["development", "dev", "local"]:
            return "DEBUG"
        return "WARNING"
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

    # Admin User Settings
    ADMIN_EMAIL: str = Field("mail@julianfleck.net", env="ADMIN_EMAIL")
    # Default should be changed in production!
    ADMIN_PASSWORD: str = Field("654c5f6d22a8", env="ADMIN_PASSWORD")
    ADMIN_NAME: str = Field("Julian Fleck", env="ADMIN_NAME")

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="allow",
        env_nested_delimiter="__",
        env_prefix="",
        use_enum_values=True,
    )

from .settings import Settings


def get_settings() -> Settings:
    """Get settings instance"""
    return Settings()


# Create a global settings instance
settings = get_settings()

__all__ = ["settings", "get_settings"]

from .settings import Settings


def get_settings() -> Settings:
    """Get settings instance"""
    return Settings()


# Create a global settings instance
settings = get_settings()

# Add debug print to verify settings
print(
    f"🔧 Loaded settings - API_PORT: {settings.API_PORT}, API_HOST: {settings.API_HOST}")

__all__ = ['settings', 'get_settings']

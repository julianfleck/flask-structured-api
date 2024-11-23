from redis import Redis, ConnectionPool, RedisError
from flask_structured_api.core.config import settings
from flask_structured_api.core.exceptions import APIError
from flask_structured_api.core.utils.logger import system_logger


def create_redis_client() -> Redis:
    """Create Redis client with error handling"""
    try:
        pool = ConnectionPool.from_url(
            settings.REDIS_URL,
            max_connections=settings.REDIS_MAX_CONNECTIONS,
            decode_responses=True,
            socket_connect_timeout=2,
            socket_keepalive=True,
            retry_on_timeout=True
        )
        client = Redis(connection_pool=pool)
        client.ping()
        system_logger.info("Redis connection established")
        return client
    except RedisError as e:
        system_logger.error(
            f"Redis connection failed: {str(e)}. "
            "Please ensure Redis is running and REDIS_URL is correct in your .env file. "
            "See docs/getting-started/README.md for setup instructions."
        )
        raise APIError(
            message="Redis service unavailable. Please check your configuration.",
            code="REDIS_UNAVAILABLE",
            status_code=503
        )


# Global redis client
redis_client = create_redis_client()


def get_redis() -> Redis:
    """Get Redis client"""
    if redis_client is None:
        raise APIError(
            message="Redis service unavailable",
            code="REDIS_UNAVAILABLE",
            status_code=503
        )
    return redis_client

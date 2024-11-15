from redis import Redis, ConnectionPool, RedisError
from app.core.config import settings
from app.core.exceptions import APIError
import logging

logger = logging.getLogger(__name__)


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
        # Test connection
        client.ping()
        return client
    except RedisError as e:
        logger.error(f"Redis connection failed: {str(e)}")
        # Don't raise here, return None so the app can still function
        return None


# Global redis client
redis_client = create_redis_client()


def get_redis() -> Redis:
    """Get Redis client with fallback"""
    if redis_client is None:
        raise APIError(
            message="Redis service unavailable",
            code="REDIS_UNAVAILABLE",
            status_code=503
        )
    return redis_client

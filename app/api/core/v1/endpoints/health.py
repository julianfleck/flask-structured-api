from flask import Blueprint, current_app, g
from app.models.responses import SuccessResponse
from app.core.config import settings
from app.utils.routes import get_filtered_routes
from app.core.storage.decorators import store_api_data
from app.models.enums import StorageType
import platform
import psutil
import time
from sqlalchemy import text
from app.core.db import engine
from app.core.auth import optional_auth, require_auth
from app.core.cache import redis_client

health_bp = Blueprint('health', __name__)


def check_database() -> bool:
    """Check database connectivity"""
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return True
    except Exception:
        return False


def check_redis() -> bool:
    """Check Redis connectivity"""
    try:
        redis_client.ping()
        return True
    except Exception:
        return False


@health_bp.route('/health', methods=['GET'])
@require_auth
@store_api_data(
    storage_type=StorageType.BOTH,
    ttl_days=1,  # Keep health check data for 1 day
    metadata={"check_type": "health"}
)
def health_check():
    """Health check endpoint that returns system status and component health."""
    start_time = time.time()
    is_authenticated = hasattr(g, 'user')
    db_healthy = check_database()
    response_time = round((time.time() - start_time) * 1000, 2)

    response_data = {
        "status": "healthy" if db_healthy else "unhealthy",
        "name": settings.API_NAME,
        "version": settings.API_VERSION,
        "components": {
            "database": "healthy" if db_healthy else "unhealthy",
            "redis": "healthy" if check_redis() else "unhealthy"
        }
    }

    # Only include detailed metrics in debug mode
    if settings.API_DEBUG:
        response_data.update({
            "environment": settings.ENVIRONMENT,
            "response_time_ms": response_time,
            "system": {
                "cpu_usage": psutil.cpu_percent(),
                "memory_usage": psutil.virtual_memory().percent,
                "disk_usage": psutil.disk_usage('/').percent,
                "python_version": platform.python_version(),
                "platform": platform.platform()
            },
            "endpoints": get_filtered_routes(check_auth=is_authenticated)
        })

    return SuccessResponse(
        message="{} health check".format(settings.API_NAME),
        data=response_data
    ).dict()

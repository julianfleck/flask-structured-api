import platform
import time

import psutil
from flask import Blueprint, current_app, g, jsonify, request
from sqlalchemy import text

from flask_structured_api.core.auth import optional_auth, require_auth
from flask_structured_api.core.cache import redis_client
from flask_structured_api.core.config import settings
from flask_structured_api.core.db import engine
from flask_structured_api.core.enums import StorageType
from flask_structured_api.core.models.responses import SuccessResponse
from flask_structured_api.core.storage.decorators import store_api_data
from flask_structured_api.core.utils.routes import get_filtered_routes
from flask_structured_api.core.middleware.logging import log_request, log_response, debug_request, debug_response

health_bp = Blueprint("health", __name__)


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


@health_bp.route("/health", methods=["GET"])
@optional_auth
def health_check():
    """Health check endpoint that returns system status and component health."""
    start_time = time.time()
    db_healthy = check_database()
    response_time = round((time.time() - start_time) * 1000, 2)

    # Check if request is authenticated
    is_authenticated = hasattr(g, "api_key") or hasattr(g, "user")

    response_data = {
        "status": "healthy" if db_healthy else "unhealthy",
        "name": settings.API_NAME,
        "version": settings.API_VERSION,
        "components": {
            "database": "healthy" if db_healthy else "unhealthy",
            "redis": "healthy" if check_redis() else "unhealthy",
        },
    }

    response_data.update(
        {
            "environment": settings.ENVIRONMENT,
            "response_time_ms": response_time,
            "service": {
                "host": request.host,
                "url": request.url_root.rstrip('/'),
            },
            "system": {
                "cpu_usage": psutil.cpu_percent(),
                "memory_usage": psutil.virtual_memory().percent,
                "disk_usage": psutil.disk_usage("/").percent,
                "python_version": platform.python_version(),
                "platform": platform.platform(),
            },
            # Simple path -> description mapping
            "endpoints": get_filtered_routes(check_auth=is_authenticated),
        }
    )

    response = jsonify(SuccessResponse(
        message="{} health check".format(settings.API_NAME),
        data=response_data
    ).dict())

    response.headers['X-API-Version'] = settings.API_VERSION
    response.headers['X-Response-Time'] = str(response_time)

    return response

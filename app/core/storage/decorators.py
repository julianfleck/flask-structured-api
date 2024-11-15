from functools import wraps
from flask import request, g, Response
from datetime import datetime
from typing import Optional, Dict, Any, Callable
from app.core.db import get_session
from app.core.session import get_or_create_session
from app.services.storage import StorageService
from app.models.enums import StorageType
import json
from app.core.config import settings


def store_api_data(
    ttl_days: Optional[int] = None,
    compress: bool = False,
    metadata: Optional[Dict[str, Any]] = None,
    storage_type: StorageType = StorageType.REQUEST,
    session_timeout_minutes: int = 30,
) -> Callable:
    """Decorator to store API request/response data"""
    def decorator(f: Callable) -> Callable:
        @wraps(f)
        def wrapper(*args, **kwargs):
            db = next(get_session())
            storage_service = StorageService(db)
            endpoint = request.path.strip('/')

            # Get or create session with custom timeout
            session_id = get_or_create_session(
                g.user_id, session_timeout_minutes)

            # Merge session_id into metadata
            request_metadata = metadata.copy() if metadata else {}
            request_metadata['session_id'] = session_id

            # Store request if needed
            if storage_type in (StorageType.REQUEST, StorageType.BOTH):
                storage_service.store_request(
                    user_id=g.user_id,
                    endpoint=endpoint,
                    request_data={
                        "method": request.method,
                        "path": request.path,
                        "args": dict(request.args),
                        "headers": dict(request.headers),
                        "data": request.get_json() if request.is_json else None
                    },
                    ttl_days=ttl_days,
                    compress=compress,
                    metadata=request_metadata
                )

            # Execute the route handler
            response = f(*args, **kwargs)

            # Store response if needed
            if storage_type in (StorageType.RESPONSE, StorageType.BOTH):
                storage_service.store_response(
                    user_id=g.user_id,
                    endpoint=endpoint,
                    response_data=response,
                    ttl_days=ttl_days,
                    compress=compress,
                    metadata=request_metadata
                )

            return response
        return wrapper
    return decorator

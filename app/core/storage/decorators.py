from functools import wraps
from flask import request, g, Response
from datetime import datetime
from typing import Optional, Dict, Any
from app.core.db import get_session
from app.services.storage import StorageService
from app.models.enums import StorageType


def store_api_data(
    storage_type: StorageType = StorageType.BOTH,
    ttl_days: Optional[int] = None,
    compress: bool = False,
    metadata: Optional[Dict[str, Any]] = None
):
    """Store API request/response data"""
    def decorator(f):
        @wraps(f)
        def wrapped(*args, **kwargs):
            db = next(get_session())
            storage_service = StorageService(db)

            # Capture request if needed
            if storage_type in [StorageType.REQUEST, StorageType.BOTH]:
                request_data = {
                    'method': request.method,
                    'path': request.path,
                    'headers': dict(request.headers),
                    'args': dict(request.args),
                    'data': request.get_data(as_text=True)
                }
                storage_service.store_request(
                    user_id=g.user_id,
                    endpoint=request.path.lstrip('/'),
                    request_data=request_data,
                    ttl_days=ttl_days,
                    compress=compress,
                    metadata=metadata
                )

            # Execute endpoint
            response = f(*args, **kwargs)

            # Store response if needed
            if storage_type in [StorageType.RESPONSE, StorageType.BOTH]:
                # Handle both Response objects and dicts
                response_data = response.get_json() if isinstance(
                    response, Response) else response

                storage_service.store_response(
                    user_id=g.user_id,
                    endpoint=request.path.lstrip('/'),
                    response_data=response_data,
                    ttl_days=ttl_days,
                    compress=compress,
                    metadata=metadata
                )

            return response
        return wrapped
    return decorator

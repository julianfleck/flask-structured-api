import json
from datetime import datetime
from functools import wraps
from typing import Any, Callable, Dict, Optional
import inspect

from flask import Response, g, request, current_app

from flask_structured_api.core.config import settings
from flask_structured_api.core.db import get_session
from flask_structured_api.core.enums import StorageType
from flask_structured_api.core.services.storage import StorageService
from flask_structured_api.core.session import get_or_create_session


def store_api_data(
    ttl_days: Optional[int] = None,
    compress: bool = False,
    metadata: Optional[Dict[str, Any]] = None,
    storage_type: StorageType = StorageType.BOTH,
    session_timeout_minutes: int = 30,
) -> Callable:
    """Decorator to store API request/response data"""

    def decorator(f):
        @wraps(f)
        async def wrapper(*args, **kwargs):
            # Get storage service instance with a new session
            db = next(get_session())
            # Create new service instance with session
            storage_service = StorageService(db)
            endpoint = request.path.strip("/")

            # Get or create session with custom timeout
            session_id = get_or_create_session(g.user_id, session_timeout_minutes)

            # Merge session_id into metadata
            request_metadata = metadata.copy() if metadata else {}
            request_metadata["session_id"] = session_id

            # Store request data if needed
            if storage_type in [StorageType.REQUEST, StorageType.BOTH]:
                storage_service.store_request(
                    user_id=g.user_id,
                    endpoint=endpoint,
                    request_data={
                        "method": request.method,
                        "path": request.path,
                        "args": dict(request.args),
                        "headers": dict(request.headers),
                        "data": request.get_json() if request.is_json else None,
                    },
                    ttl_days=ttl_days,
                    compress=compress,
                    metadata=request_metadata
                )

            # Execute the function and get response
            response = await f(*args, **kwargs)

            # Await the response if it's a coroutine
            if inspect.iscoroutine(response):
                response = await response

            # Store response data if needed
            if storage_type in [StorageType.RESPONSE, StorageType.BOTH]:
                # Extract response data for storage
                if hasattr(response, 'get_json'):
                    response_data = response.get_json()
                elif hasattr(response, 'json'):
                    response_data = response.json
                else:
                    # Fallback to response data if it's already a dict
                    response_data = response if isinstance(
                        response, dict) else str(response)

                storage_service.store_response(
                    user_id=g.user_id,
                    endpoint=endpoint,
                    response_data=response_data,
                    ttl_days=ttl_days,
                    compress=compress,
                    metadata=request_metadata
                )

            return response
        return wrapper
    return decorator

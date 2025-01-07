import uuid
from time import time
import inspect
import asyncio
from flask import g, request, Response
from functools import wraps


def setup_request_context(app):
    """Setup request context with unique ID and other request-scoped data"""

    @app.before_request
    def before_request():
        # Always ensure request_id is set first
        g.request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
        g.request_start_time = time()

        # Make loggers available in request context
        g.logger = app.logger
        g.db_logger = app.db_logger
        g.ai_logger = app.ai_logger
        g.api_logger = app.api_logger
        g.system_logger = app.system_logger

    @app.after_request
    async def after_request(response):
        """Add request ID to response headers"""
        # Handle async responses
        if inspect.iscoroutine(response):
            response = await response

        # Add request ID to headers if available
        if hasattr(g, 'request_id'):
            if isinstance(response, Response):
                response.headers["X-Request-ID"] = g.request_id

        return response

    return app

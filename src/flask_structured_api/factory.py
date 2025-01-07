import os
import socket
import asyncio
import logging
import json
import inspect
from functools import wraps

from flask import Flask, request, make_response
from asgiref.wsgi import WsgiToAsgi
from asgiref.sync import sync_to_async, async_to_sync
from flask_openapi3 import Info, Tag
from functools import partial
from flask_migrate import Migrate

from flask_structured_api.core.cli import init_cli
from flask_structured_api.core.config import settings
from flask_structured_api.core.db.shared import db  # Import shared instance
from flask_structured_api.core.handlers import register_error_handlers
from flask_structured_api.core.middleware import setup_request_context, setup_cors
from flask_structured_api.core.middleware.logging import (
    setup_request_logging,
    setup_response_logging,
)
from flask_structured_api.core.utils.logger import create_logger_system, get_standalone_logger
from flask_structured_api.core.services.ai import AIService
from flask_structured_api.core.ai.providers import get_provider
from flask_structured_api.api.core import init_app
from flask_structured_api.core.services.storage import StorageService

_debugger_initialized = False
_flask_app = None

# Create standalone logger for system initialization
init_logger = get_standalone_logger("init")


def _init_debugger():
    """Initialize debugger if not already initialized"""
    global _debugger_initialized
    if _debugger_initialized:
        return

    if not (settings.API_DEBUG and os.getenv("DEBUGPY_ENABLE")):
        return

    try:
        import debugpy
        base_port = int(os.getenv("DEBUGPY_PORT", "5678"))

        # Check if debugpy is already running
        if hasattr(debugpy, "_listen_socket") or debugpy.is_client_connected():
            init_logger.debug("🐛 Debugpy already running")
            _debugger_initialized = True
            return

        # Check if port is available
        if is_port_in_use(base_port):
            init_logger.debug(
                f"🐛 Port {base_port} already in use, assuming debugpy is running")
            _debugger_initialized = True
            return

        # Set environment variable to suppress frozen modules warning
        os.environ["PYDEVD_DISABLE_FILE_VALIDATION"] = "1"

        # Try to start debugpy
        debugpy.listen(("0.0.0.0", base_port))
        init_logger.info(f"🐛 Debugpy listening on port {base_port}")
        _debugger_initialized = True

    except Exception as e:
        # Only log as debug since this might happen during hot reloads
        init_logger.debug(f"🐛 Debugpy initialization skipped: {str(e)}")
        _debugger_initialized = True  # Prevent further attempts


def is_port_in_use(port: int) -> bool:
    """Check if a port is already in use"""
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
    try:
        sock.bind(("0.0.0.0", port))
        return False
    finally:
        cleanup_socket(sock)


def cleanup_socket(sock):
    """Ensure socket is properly closed"""
    try:
        sock.shutdown(socket.SHUT_RDWR)
    except:
        pass
    try:
        sock.close()
    except:
        pass


class AsyncFlask(Flask):
    """Flask subclass that handles both sync and async responses"""

    def make_response(self, rv):
        """Override to handle both coroutine and regular returns"""
        if inspect.iscoroutine(rv):
            # For async endpoints, return the coroutine directly
            # It will be handled by the ASGI wrapper
            return rv
        # For sync endpoints, handle normally
        return super().make_response(rv)


def create_flask_app():
    """Create and configure Flask application"""
    global _flask_app

    # Return existing instance if already created
    if _flask_app is not None:
        return _flask_app

    app = AsyncFlask(__name__)
    _flask_app = app

    # Initialize logging system first
    app.loggers = create_logger_system()

    # Add logger shortcuts to app
    app.system_logger = app.loggers['system']
    app.db_logger = app.loggers['database']
    app.ai_logger = app.loggers['ai']
    app.backup_logger = app.loggers['backup']
    app.api_logger = app.loggers['api']

    # Set AI logger to DEBUG level explicitly
    app.loggers['ai'].setLevel(logging.DEBUG)

    # Also keep the standard Flask logger for compatibility
    app.logger = app.loggers['system']

    # Add SQLAlchemy config
    app.config["SQLALCHEMY_DATABASE_URI"] = settings.DATABASE_URL
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    # Add API settings to config
    app.config.update({
        "API_NAME": settings.API_NAME,
        "API_VERSION": settings.API_VERSION,
        "API_DEBUG": settings.API_DEBUG,
        "API_HOST": settings.API_HOST,
        "API_PORT": settings.API_PORT
    })

    # Initialize shared db instance
    if not hasattr(app, 'db'):
        db.init_app(app)
        app.db = db

    # Initialize Flask-Migrate
    migrations_dir = os.environ.get('FLASK_MIGRATIONS_DIR', '/app/migrations')
    Migrate(app, db, directory=migrations_dir)

    # Initialize CLI commands
    init_cli(app)

    # Initialize storage service
    app.storage_service = StorageService(db)

    # Register middleware in correct order
    setup_request_context(app)
    # app.before_request(setup_request_logging)

    # Register blueprints and handlers
    init_app(app)
    register_error_handlers(app)

    # Register CORS and response logging last
    setup_cors(app)
    # app.after_request(setup_response_logging)

    return app


class AsyncCompatibleWsgiToAsgi(WsgiToAsgi):
    """Custom ASGI wrapper that handles both sync and async responses"""

    async def __call__(self, scope, receive, send):
        if scope["type"] == "http":
            async def modified_send(message):
                if message["type"] == "http.response.start":
                    headers = list(message.get("headers", []))
                    headers = [h for h in headers if h[0].lower() != b"content-length"]
                    headers.append((b"transfer-encoding", b"chunked"))
                    message["headers"] = headers
                await send(message)

            response = await super().__call__(scope, receive, modified_send)

            # If response is a coroutine, await it
            if inspect.iscoroutine(response):
                response = await response

            return response
        return await super().__call__(scope, receive, send)


def create_app():
    """Create main ASGI application"""
    flask_app = create_flask_app()
    app = AsyncFlask(__name__)

    # Copy config and setup from create_flask_app
    app.config.update(flask_app.config)

    # Setup request context first
    setup_request_context(app)

    # Then set up CORS
    setup_cors(app)

    # Copy over loggers and services
    for attr in ['loggers', 'system_logger', 'logger', 'db_logger',
                 'ai_logger', 'backup_logger', 'api_logger',
                 'ai_service', 'db', 'redis', 'storage_service']:
        if hasattr(flask_app, attr):
            setattr(app, attr, getattr(flask_app, attr))

    # Register other middleware
    init_app(app)
    register_error_handlers(app)

    # Initialize debugger if needed
    _init_debugger()

    # Use our custom ASGI wrapper
    asgi_app = AsyncCompatibleWsgiToAsgi(app)
    asgi_app.flask_app = app

    return asgi_app


# Create app instance for Hypercorn
app = create_app()

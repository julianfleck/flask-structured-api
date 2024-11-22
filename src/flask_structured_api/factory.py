from flask import Flask
from flask_openapi3 import OpenAPI
from flask_cors import CORS
import os
import socket

from flask_structured_api.core.config import settings
from flask_structured_api.core.db import init_db
from flask_structured_api.core.handlers import register_error_handlers
from flask_structured_api.core.middleware import setup_request_context
from flask_structured_api.core.cli import init_cli
from flask_structured_api.core.utils.logger import system_logger
from flask_structured_api.core.middleware.logging import setup_request_logging, setup_response_logging

_debugger_initialized = False


def _init_debugger():
    """Initialize debugger if not already initialized"""
    global _debugger_initialized
    if _debugger_initialized:
        return

    if settings.API_DEBUG and os.getenv('DEBUGPY_ENABLE'):
        try:
            import debugpy
            base_port = int(os.getenv('DEBUGPY_PORT', '5678'))

            # Check if debugpy is already listening
            if hasattr(debugpy, '_listen_socket') and debugpy._listen_socket is not None:
                system_logger.info("🐛 Debugpy is already listening")
                _debugger_initialized = True
                return

            # Check if debugpy is already connected (alternative method)
            try:
                if debugpy.is_client_connected():
                    system_logger.info("🐛 Debugpy is already connected")
                    _debugger_initialized = True
                    return
            except:
                pass  # ignore if this check fails

            # Try to initialize debugpy
            try:
                debugpy.listen(('0.0.0.0', base_port))
                system_logger.info(
                    "🐛 Debugpy is listening on port {}".format(base_port))
                _debugger_initialized = True
            except RuntimeError as e:
                if "Address already in use" in str(e):
                    system_logger.info(
                        "🐛 Debugpy appears to be already running on port {}".format(base_port))
                    _debugger_initialized = True
                else:
                    raise
        except Exception as e:
            system_logger.error(
                "⚠️ Failed to initialize debugger: {}".format(e), exc_info=True)


def is_port_in_use(port: int) -> bool:
    """Check if a port is already in use"""
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
    try:
        sock.bind(('0.0.0.0', port))
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


def create_app() -> Flask:
    """Create and configure Flask application"""
    _init_debugger()  # Initialize debugger once

    # Create app first
    app = OpenAPI(__name__)
    app.config.from_object(settings)

    # Add SQLAlchemy config
    app.config['SQLALCHEMY_DATABASE_URI'] = settings.DATABASE_URL
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Handle frozen modules
    if os.environ.get('FLASK_ENV') == 'development':
        import sys
        sys.frozen = False  # Disable frozen modules in development
        os.environ['PYDEVD_DISABLE_FILE_VALIDATION'] = '1'

    # Initialize extensions
    CORS(app)
    init_db(app)

    # Register blueprints
    try:
        from flask_structured_api.api.core import init_app
        init_app(app)
    except ImportError as e:
        print(f"⚠️  Failed to register blueprints: {e}")

    # Register error handlers and middleware
    register_error_handlers(app)
    setup_request_context(app)
    init_cli(app)

    # Register logging middleware using the setup functions directly
    # Use setup function, not decorator
    app.before_request(setup_request_logging)
    # Use setup function, not decorator
    app.after_request(setup_response_logging)

    return app

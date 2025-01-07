import logging
import os
import re
import sys
from datetime import datetime
from functools import wraps
from logging.handlers import MemoryHandler, RotatingFileHandler
from pathlib import Path
from time import time
import json

import click
from werkzeug.serving import WSGIRequestHandler

from flask_structured_api.core.config import settings


def get_log_dir():
    """Get log directory from environment or use sensible defaults"""
    log_dir = os.getenv("FLASK_LOG_DIR")
    if log_dir:
        try:
            os.makedirs(log_dir, exist_ok=True)
            return log_dir
        except (OSError, PermissionError):
            pass

    # Try current directory first
    cwd_logs = os.path.join(os.getcwd(), "logs")
    try:
        os.makedirs(cwd_logs, exist_ok=True)
        return cwd_logs
    except (OSError, PermissionError):
        pass

    # Fallback to temp directory
    import tempfile

    tmp_dir = os.path.join(tempfile.gettempdir(), "flask-api-logs")
    try:
        os.makedirs(tmp_dir, exist_ok=True)
        return tmp_dir
    except (OSError, PermissionError):
        return None


class ColorPreservingFormatter(logging.Formatter):
    def format(self, record):
        # Always format extra parameters consistently
        extra = {
            k: v for k, v in record.__dict__.items()
            if k not in logging.LogRecord.__dict__ and k != 'msg'
        }

        # # If we have extra fields, add them to the message
        if extra:
            try:
                # Format the original message first
                formatted_msg = super().format(record)
                # Add extras as JSON
                extra_str = json.dumps(extra, indent=2, default=str)
                return f"{formatted_msg}\nExtras: {extra_str}"
            except Exception as e:
                # If JSON serialization fails, format as string
                extra_str = "\n".join(f"{k}: {v}" for k, v in extra.items())
                return f"{super().format(record)}\nExtras: {extra_str}"

        return super().format(record)


class WerkzeugFilter(logging.Filter):
    def filter(self, record):
        if hasattr(record, "name") and record.name == "werkzeug":
            # Always allow error and warning logs through
            if record.levelno >= logging.WARNING:
                return True

            if hasattr(record, "msg") and isinstance(record.msg, str):
                # Filter out standard HTTP method logs
                if (
                    '"GET ' in record.msg
                    or '"POST ' in record.msg
                    or '"PUT ' in record.msg
                    or '"DELETE ' in record.msg
                ):
                    # Additional check for health endpoint
                    if 'GET /health' in record.msg:
                        return False
                    # Check for Google Cloud health check IPs
                    google_health_ips = ['35.191.', '130.211.']
                    if any(ip in record.msg for ip in google_health_ips):
                        return False
                    return False

                # Allow all other Werkzeug logs
                return True
        return True


def get_log_level():
    """Determine log level based on environment variables"""
    # Check if LOG_LEVEL is explicitly set
    env_log_level = os.getenv('LOG_LEVEL')
    if env_log_level:
        # Convert to uppercase and get corresponding logging level
        try:
            return getattr(logging, env_log_level.upper())
        except AttributeError:
            # Fallback to INFO if invalid level specified
            return logging.INFO

    # If LOG_LEVEL not set, check ENVIRONMENT
    environment = os.getenv('ENVIRONMENT', 'production').lower()
    if environment == 'development':
        return logging.DEBUG

    # Default to INFO for production and any other environment
    return logging.INFO


def setup_system_logger(name):
    """Setup a system-level logger with consistent formatting"""
    logger = logging.getLogger(name)

    # Return existing logger if already configured
    if logger.hasHandlers():
        return logger

    # Remove any existing handlers to prevent duplicates
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)

    # Console handler with consistent formatting everywhere
    console_handler = logging.StreamHandler(sys.stdout)
    console_formatter = ColorPreservingFormatter(
        "[%(asctime)s] [%(name)s] [%(levelname)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S,%f"
    )
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)

    # Only attempt file logging if not in Kubernetes
    if not os.getenv('KUBERNETES_SERVICE_HOST'):
        log_dir = get_log_dir()
        if log_dir:
            try:
                file_handler = RotatingFileHandler(
                    os.path.join(log_dir, f"{name}.log"),
                    maxBytes=1024 * 1024,
                    backupCount=5,
                )
                file_formatter = ColorPreservingFormatter(
                    "[%(asctime)s] [%(name)s] [%(levelname)s] %(message)s",
                    datefmt="%Y-%m-%d %H:%M:%S,%f"
                )
                file_handler.setFormatter(file_formatter)
                logger.addHandler(file_handler)
            except (OSError, PermissionError):
                pass

    # Prevent propagation to root logger
    logger.propagate = False
    logger.setLevel(get_log_level())

    # Force flush after each log in Kubernetes
    if os.getenv('KUBERNETES_SERVICE_HOST'):
        logger.handlers[0].flush = lambda: sys.stdout.flush()

    return logger


def create_logger_system():
    """Create and configure all system loggers"""
    log_level = get_log_level()

    loggers = {
        'system': setup_system_logger("system"),
        'database': setup_system_logger("database"),
        'backup': setup_system_logger("backup"),
        'ai': setup_system_logger("ai"),
        'api': setup_system_logger("api"),
    }

    # Configure Flask's default logger
    flask_logger = logging.getLogger("flask.app")
    flask_logger.handlers = loggers['system'].handlers
    flask_logger.setLevel(log_level)

    # Configure Werkzeug logger with more detailed settings
    werkzeug_logger = logging.getLogger("werkzeug")
    werkzeug_logger.handlers = []
    werkzeug_logger.addFilter(WerkzeugFilter())
    werkzeug_logger.setLevel(log_level)

    # Add handler for Werkzeug with detailed formatting
    werkzeug_handler = logging.StreamHandler(sys.stdout)
    werkzeug_formatter = ColorPreservingFormatter(
        "[%(asctime)s] [%(name)s] [%(levelname)s] %(message)s\n"
        "Path: %(path)s\n"
        "Status: %(status)s\n"
        "IP: %(remote_addr)s\n"
        "%(error_info)s",
        datefmt="%Y-%m-%d %H:%M:%S,%f"
    )
    werkzeug_handler.setFormatter(werkzeug_formatter)
    werkzeug_logger.addHandler(werkzeug_handler)
    werkzeug_logger.propagate = False  # Prevent double logging

    # Configure httpx logger
    httpx_logger = logging.getLogger("httpx")
    httpx_logger.setLevel(log_level)

    # Configure urllib3 logger
    urllib3_logger = logging.getLogger("urllib3")
    urllib3_logger.setLevel(log_level)

    # Configure root logger
    root_logger = logging.getLogger()
    if root_logger.handlers:
        root_logger.handlers = []
    root_logger.handlers = loggers['system'].handlers
    root_logger.setLevel(log_level)

    return loggers


def get_standalone_logger(name):
    """Create a standalone logger that doesn't depend on Flask's app context"""
    return setup_system_logger(f"standalone.{name}")

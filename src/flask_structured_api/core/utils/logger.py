from functools import wraps
from logging.handlers import RotatingFileHandler, MemoryHandler
import logging
import sys
import os
from time import time
from werkzeug.serving import WSGIRequestHandler
import click
from datetime import datetime
import re
from pathlib import Path


def get_log_dir():
    """Get log directory from environment or use sensible defaults"""
    log_dir = os.getenv('FLASK_LOG_DIR')
    if log_dir:
        try:
            os.makedirs(log_dir, exist_ok=True)
            return log_dir
        except (OSError, PermissionError):
            pass

    # Try current directory first
    cwd_logs = os.path.join(os.getcwd(), 'logs')
    try:
        os.makedirs(cwd_logs, exist_ok=True)
        return cwd_logs
    except (OSError, PermissionError):
        pass

    # Fallback to temp directory
    import tempfile
    tmp_dir = os.path.join(tempfile.gettempdir(), 'flask-api-logs')
    try:
        os.makedirs(tmp_dir, exist_ok=True)
        return tmp_dir
    except (OSError, PermissionError):
        return None


class ColorPreservingFormatter(logging.Formatter):
    def format(self, record):
        # Preserve any ANSI color codes in the message
        if hasattr(record, 'msg_with_colors'):
            original_msg = record.msg
            record.msg = record.msg_with_colors
            formatted = super().format(record)
            record.msg = original_msg
            return formatted
        return super().format(record)


class WerkzeugFilter(logging.Filter):
    def filter(self, record):
        if hasattr(record, 'name') and record.name == 'werkzeug':
            if hasattr(record, 'msg') and isinstance(record.msg, str):
                if '"GET ' in record.msg or '"POST ' in record.msg or \
                   '"PUT ' in record.msg or '"DELETE ' in record.msg:
                    return False
        return True


def setup_system_logger(name, log_level=logging.INFO):
    """Setup a system-level logger with consistent formatting"""
    logger = logging.getLogger(name)

    if logger.handlers:
        return logger

    # Console handler with color preservation
    console_handler = logging.StreamHandler(sys.stdout)
    console_formatter = ColorPreservingFormatter(
        '[%(asctime)s] %(levelname)s: %(message)s'
    )
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)

    # Try to set up file logging
    log_dir = get_log_dir()
    if log_dir:
        try:
            file_handler = RotatingFileHandler(
                os.path.join(log_dir, f"{name}.log"),
                maxBytes=1024 * 1024,
                backupCount=5
            )
            file_formatter = ColorPreservingFormatter(
                '[%(asctime)s] [%(name)s] [%(levelname)s] %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S,%f'
            )
            file_handler.setFormatter(file_formatter)
            logger.addHandler(file_handler)
        except (OSError, PermissionError):
            # Fallback to memory handler if file logging fails
            memory_handler = MemoryHandler(1024 * 1024)
            memory_handler.setFormatter(file_formatter)
            logger.addHandler(memory_handler)

    logger.setLevel(log_level)
    return logger


# Initialize loggers
system_logger = setup_system_logger('system')
db_logger = setup_system_logger('database')
backup_logger = setup_system_logger('backup')

# Configure Flask's default logger
flask_logger = logging.getLogger('flask.app')
flask_logger.handlers = system_logger.handlers
flask_logger.setLevel(logging.INFO)

# Configure Werkzeug logger
werkzeug_logger = logging.getLogger('werkzeug')
werkzeug_logger.handlers = []
werkzeug_logger.addFilter(WerkzeugFilter())
werkzeug_logger.setLevel(logging.INFO)

# Configure root logger
root_logger = logging.getLogger()
if root_logger.handlers:
    root_logger.handlers = []
root_logger.handlers = system_logger.handlers
root_logger.setLevel(logging.INFO)

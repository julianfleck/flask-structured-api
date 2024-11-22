from functools import wraps
from logging.handlers import RotatingFileHandler
import logging
import sys
import os
from time import time
from werkzeug.serving import WSGIRequestHandler
import click
from datetime import datetime
import re


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
        # Only filter out Werkzeug's access logs that duplicate our middleware logs
        if hasattr(record, 'name') and record.name == 'werkzeug':
            if hasattr(record, 'msg') and isinstance(record.msg, str):
                # Filter out the standard Werkzeug access log format
                if '"GET ' in record.msg or '"POST ' in record.msg or \
                   '"PUT ' in record.msg or '"DELETE ' in record.msg:
                    return False
        return True


def setup_system_logger(name, log_level=logging.INFO):
    """Setup a system-level logger with consistent formatting"""
    logger = logging.getLogger(name)

    if not logger.handlers:
        # Simplified console format
        console_handler = logging.StreamHandler(sys.stdout)
        console_formatter = logging.Formatter(
            '[%(asctime)s] %(levelname)s: %(message)s'
        )
        console_handler.setFormatter(console_formatter)
        logger.addHandler(console_handler)

        # Keep detailed format for file logs
        log_dir = "/var/log/flask-api"
        os.makedirs(log_dir, exist_ok=True)
        file_handler = RotatingFileHandler(
            "{}/{}.log".format(log_dir, name),
            maxBytes=1024 * 1024,
            backupCount=10
        )
        file_formatter = logging.Formatter(
            '[%(asctime)s] [%(name)s] [%(levelname)s] %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S,%f'
        )
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)

        logger.setLevel(log_level)

    return logger


# Create system loggers
db_logger = setup_system_logger('database')
system_logger = setup_system_logger('system')
backup_logger = setup_system_logger('backup')

# Configure Flask's default logger to use our format
flask_logger = logging.getLogger('flask.app')
flask_logger.handlers = system_logger.handlers
flask_logger.setLevel(logging.INFO)

# Configure Werkzeug logger
werkzeug_logger = logging.getLogger('werkzeug')
werkzeug_logger.handlers = []  # Clear existing handlers
werkzeug_logger.addFilter(WerkzeugFilter())
werkzeug_logger.setLevel(logging.INFO)

# Configure root logger to use our format
root_logger = logging.getLogger()  # Root logger
if root_logger.handlers:  # Clear existing handlers
    root_logger.handlers = []
root_logger.handlers = system_logger.handlers
root_logger.setLevel(logging.INFO)

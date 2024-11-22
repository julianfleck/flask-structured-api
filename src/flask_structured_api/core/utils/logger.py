from functools import wraps
from logging.handlers import RotatingFileHandler
import logging
import sys
import os
from time import time

# Configure system-level logger


def setup_system_logger(name, log_level=logging.INFO):
    """Setup a system-level logger with consistent formatting"""
    logger = logging.getLogger(name)

    if not logger.handlers:
        # Console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        console_handler.setFormatter(console_formatter)
        logger.addHandler(console_handler)

        # File handler for system logs
        log_dir = "/var/log/flask-api"
        os.makedirs(log_dir, exist_ok=True)
        file_handler = RotatingFileHandler(
            f"{log_dir}/{name}.log",
            maxBytes=1024 * 1024,  # 1MB
            backupCount=10
        )
        file_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)

        logger.setLevel(log_level)

    return logger


# Create system loggers
db_logger = setup_system_logger('database')
system_logger = setup_system_logger('system')
backup_logger = setup_system_logger('backup')


def log_function(name=None):
    """Decorator to log function entry/exit with timing"""
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            logger = system_logger
            func_name = name or f.__name__
            start_time = time()

            logger.debug("Entering {}".format(func_name))
            try:
                result = f(*args, **kwargs)
                duration = time() - start_time
                logger.debug("Exiting {} ({:.2f}s)".format(
                    func_name, duration))
                return result
            except Exception as e:
                duration = time() - start_time
                logger.error("Error in {}: {} ({:.2f}s)".format(
                    func_name, str(e), duration), exc_info=True)
                raise
        return wrapper
    return decorator

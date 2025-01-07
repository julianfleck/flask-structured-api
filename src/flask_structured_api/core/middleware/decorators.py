from functools import wraps
from time import time

from flask import current_app, g, request


def log_function_call(func):
    """Decorator to log function entry and exit with timing"""

    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time()
        current_app.logger.debug(
            f"Entering {func.__name__}",
            extra={
                "function": func.__name__,
                "module": func.__module__,
                "request_id": getattr(g, "request_id", None),
            },
        )

        try:
            result = func(*args, **kwargs)
            duration = time() - start_time

            current_app.logger.debug(
                f"Exiting {func.__name__} ({duration:.2f}s)",
                extra={
                    "function": func.__name__,
                    "duration": duration,
                    "success": True,
                },
            )
            return result

        except Exception as e:
            duration = time() - start_time
            current_app.logger.error(
                f"Error in {func.__name__}: {str(e)} ({duration:.2f}s)",
                extra={
                    "function": func.__name__,
                    "duration": duration,
                    "error": str(e),
                    "success": False,
                },
                exc_info=True,
            )
            raise

    return wrapper

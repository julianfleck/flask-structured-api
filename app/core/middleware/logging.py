from functools import wraps
from flask import current_app, g, request
from time import time


def setup_request_logging():
    """Setup initial request logging"""
    g.request_start_time = time()
    current_app.logger.info(
        f"Request {g.request_id}: {request.method} {request.path}",
        extra={
            "request_id": g.request_id,
            "method": request.method,
            "path": request.path,
            "remote_addr": request.remote_addr
        }
    )


def setup_response_logging(response):
    """Setup response logging"""
    duration = time() - g.request_start_time
    current_app.logger.info(
        f"Response {g.request_id}: {response.status_code} ({duration:.2f}s)",
        extra={
            "request_id": g.request_id,
            "status_code": response.status_code,
            "duration": duration
        }
    )
    return response


def log_request(f):
    """Decorator to log incoming requests"""
    @wraps(f)
    def decorated(*args, **kwargs):
        setup_request_logging()
        return f(*args, **kwargs)
    return decorated


def log_response(f):
    """Decorator to log outgoing responses"""
    @wraps(f)
    def decorated(*args, **kwargs):
        response = f(*args, **kwargs)
        return setup_response_logging(response)
    return decorated


def log_function(f):
    """Decorator to log function entry/exit with timing"""
    @wraps(f)
    def wrapper(*args, **kwargs):
        start_time = time()
        current_app.logger.debug(
            f"Entering {f.__name__}",
            extra={
                "function": f.__name__,
                "module": f.__module__,
                "request_id": getattr(g, 'request_id', None)
            }
        )

        try:
            result = f(*args, **kwargs)
            duration = time() - start_time
            current_app.logger.debug(
                f"Exiting {f.__name__} ({duration:.2f}s)",
                extra={
                    "function": f.__name__,
                    "duration": duration,
                    "success": True
                }
            )
            return result
        except Exception as e:
            duration = time() - start_time
            current_app.logger.error(
                f"Error in {f.__name__}: {str(e)} ({duration:.2f}s)",
                extra={
                    "function": f.__name__,
                    "duration": duration,
                    "error": str(e),
                    "success": False
                },
                exc_info=True
            )
            raise
    return wrapper

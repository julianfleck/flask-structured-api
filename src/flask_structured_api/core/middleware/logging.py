from functools import wraps
from flask import current_app, g, request
from time import time
import click


def setup_request_logging():
    """Setup initial request logging"""
    g.request_start_time = time()
    current_app.logger.info(
        'Request: {} {}'.format(request.method, request.path),
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

    # Get status code safely
    if hasattr(response, 'status_code'):
        status = response.status_code
    elif hasattr(response, '_status_code'):
        status = response._status_code
    elif hasattr(response, '_status'):
        status = response._status
    else:
        status = 200

    # Color the entire log line based on status code
    if status >= 500:
        color = 'red'
        bold = True
    elif status >= 400:
        color = 'red'
        bold = False
    elif status >= 300:
        color = 'yellow'
        bold = False
    else:
        color = 'green'
        bold = False

    log_message = 'Response: {} {:.3f}s'.format(status, duration)
    colored_message = click.style(log_message, fg=color, bold=bold)

    current_app.logger.info(
        colored_message,
        extra={
            "request_id": g.request_id,
            "status_code": status,
            "duration": duration
        }
    )
    return response


# For use with @app.before_request
def before_request():
    setup_request_logging()


# For use with @app.after_request
def after_request(response):
    return setup_response_logging(response)


# For use as route decorators
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

from functools import wraps
from flask import request, make_response


def handle_options_requests(f):
    """Decorator to handle OPTIONS requests for CORS preflight"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if request.method == 'OPTIONS':
            response = make_response()
            response.headers.add('Access-Control-Allow-Origin',
                                 'https://oecd-stip-compass-prefill.vercel.app')
            response.headers.add('Access-Control-Allow-Headers',
                                 'Content-Type,Authorization')
            response.headers.add('Access-Control-Allow-Methods',
                                 'GET,PUT,POST,DELETE,OPTIONS')
            response.headers.add('Access-Control-Allow-Credentials', 'true')
            return response
        return f(*args, **kwargs)
    return decorated_function

import uuid
from flask import g, request


def setup_request_context(app):
    """Setup request context with unique ID and other request-scoped data"""
    @app.before_request
    def before_request():
        g.request_id = request.headers.get('X-Request-ID') or str(uuid.uuid4())
        g.request_start_time = request.environ.get('REQUEST_TIME', 0)

    @app.after_request
    def after_request(response):
        response.headers['X-Request-ID'] = g.request_id
        return response

    return app

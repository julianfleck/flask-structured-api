import uuid
from flask import g, request


def setup_request_context():
    """Setup request context with unique ID and other request-scoped data"""
    g.request_id = request.headers.get('X-Request-ID') or str(uuid.uuid4())

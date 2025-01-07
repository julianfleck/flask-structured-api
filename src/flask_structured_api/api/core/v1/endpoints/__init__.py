from flask import Blueprint
from .auth import auth_bp
from .health import health_bp
from .storage import storage_bp


def init_endpoints(app):
    """Initialize core v1 endpoints"""
    # Register core endpoints
    app.register_blueprint(auth_bp, url_prefix="/v1")
    app.register_blueprint(storage_bp, url_prefix="/v1")
    app.register_blueprint(health_bp, url_prefix="/v1")

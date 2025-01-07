from flask import Blueprint

from flask_structured_api.api.core.root import root_bp
from flask_structured_api.api.core.v1.endpoints import init_endpoints as init_core_endpoints
from flask_structured_api.api.custom.v1.endpoints import init_endpoints as init_custom_endpoints


def init_app(app):
    # Register root blueprint first (for /health)
    app.register_blueprint(root_bp)

    # Initialize core and custom endpoints
    init_core_endpoints(app)
    init_custom_endpoints(app)

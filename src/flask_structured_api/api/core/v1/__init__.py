from flask import Blueprint
from flask_structured_api.api.core.v1.endpoints.health import health_bp
from flask_structured_api.api.core.v1.endpoints.auth import auth_bp
from flask_structured_api.api.core.v1.endpoints.storage import storage_bp

core_api_v1 = Blueprint('core_api_v1', __name__, url_prefix='')
core_api_v1.register_blueprint(health_bp)
core_api_v1.register_blueprint(auth_bp, url_prefix='/auth')
core_api_v1.register_blueprint(storage_bp, url_prefix='/storage')

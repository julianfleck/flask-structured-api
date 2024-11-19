from flask import Blueprint
from app.api.core.v1.endpoints.health import health_bp
from app.api.core.v1.endpoints.auth import auth_bp
from app.api.core.v1.endpoints.storage import storage_bp

api_v1 = Blueprint('api_v1', __name__, url_prefix='/v1')
api_v1.register_blueprint(health_bp)
api_v1.register_blueprint(auth_bp, url_prefix='/auth')
api_v1.register_blueprint(storage_bp, url_prefix='/storage')

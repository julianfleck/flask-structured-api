from flask import Blueprint
from flask_structured_api.api.core.v1 import core_api_v1
from flask_structured_api.api.custom.v1 import custom_api_v1
from flask_structured_api.api.core.root import root_bp
from flask_structured_api.core.config import settings

# Create version-specific API blueprint
api = Blueprint('api', __name__, url_prefix=f'/{settings.API_VERSION_PREFIX}')
api.register_blueprint(core_api_v1)
api.register_blueprint(custom_api_v1)

# Register both blueprints


def init_app(app):
    app.register_blueprint(root_bp)
    app.register_blueprint(api)

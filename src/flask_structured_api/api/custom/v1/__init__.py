from flask import Blueprint
from flask_structured_api.api.custom.v1.endpoints.hello import hello_bp

custom_api_v1 = Blueprint('custom_api_v1', __name__, url_prefix='')
custom_api_v1.register_blueprint(hello_bp)

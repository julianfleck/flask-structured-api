from flask import Blueprint, current_app
from app.core.responses import SuccessResponse

root_bp = Blueprint('root', __name__)


@root_bp.route('/', methods=['GET'])
def welcome():
    """Welcome endpoint that lists all available routes"""
    endpoints = []

    for rule in current_app.url_map.iter_rules():
        if 'static' in rule.endpoint:
            continue

        methods = [m for m in rule.methods if m not in ['HEAD', 'OPTIONS']]
        endpoints.append({
            'path': rule.rule,
            'methods': methods,
            'name': rule.endpoint
        })

    return SuccessResponse(
        message=f"Welcome to {current_app.config['API_NAME']}",
        data={
            'name': current_app.config['API_NAME'],
            'version': current_app.config['API_VERSION'],
            'endpoints': sorted(endpoints, key=lambda x: x['path'])
        }
    ).dict()

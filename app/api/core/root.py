from flask import Blueprint, current_app, g
from app.models.responses import SuccessResponse
from app.utils.routes import get_endpoints_list
from app.core.auth import optional_auth

root_bp = Blueprint('root', __name__)


@root_bp.route('/', methods=['GET'])
@optional_auth
def welcome():
    """Welcome endpoint that lists all available routes"""
    is_authenticated = hasattr(g, 'user')

    if is_authenticated:
        message = "Welcome back {}! Here are your available endpoints:".format(
            g.user.full_name)
        endpoints = get_endpoints_list(check_auth=True)
    else:
        message = "Welcome! Please log in to access protected endpoints."
        # Only show public endpoints for unauthenticated users
        endpoints = get_endpoints_list(check_auth=False)

    return SuccessResponse(
        message=message,
        data={
            'name': current_app.config['API_NAME'],
            'version': current_app.config['API_VERSION'],
            'authenticated': is_authenticated,
            'endpoints': endpoints
        }
    ).dict()

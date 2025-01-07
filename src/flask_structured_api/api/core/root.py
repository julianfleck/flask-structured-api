from flask import Blueprint, current_app, g, request

from flask_structured_api.core.auth import optional_auth
from flask_structured_api.core.models.responses import SuccessResponse
from flask_structured_api.core.utils.routes import get_endpoints_list, get_filtered_routes
from flask_structured_api.api.core.v1.endpoints.health import health_bp

root_bp = Blueprint("root", __name__)

# Register health blueprint on root level
root_bp.register_blueprint(health_bp)


@root_bp.route("/", methods=["GET"])
@optional_auth
def welcome():
    """Welcome endpoint that lists all available routes"""
    is_authenticated = hasattr(g, "api_key") or hasattr(g, "user")

    if is_authenticated:
        user_name = getattr(g.user, "full_name", None) if hasattr(
            g, "user") else "API User"
        message = "Welcome back {}! Here are your available endpoints:".format(
            user_name)
        routes = get_filtered_routes(include_methods=True, check_auth=True)
    else:
        message = "Welcome! Please log in to access protected endpoints."
        routes = get_filtered_routes(include_methods=True, check_auth=False)

    endpoints = sorted(
        [
            {
                "path": path,
                "methods": data["methods"],
                "name": data["name"],
                "protected": data.get("protected", False),
                "description": data["description"]
            }
            for path, data in routes.items()
        ],
        key=lambda x: x["path"],
    )

    return SuccessResponse(
        message=message,
        data={
            "name": current_app.config["API_NAME"],
            "version": current_app.config["API_VERSION"],
            "authenticated": is_authenticated,
            "service": {
                "host": request.host,
                "url": request.url_root.rstrip('/'),
            },
            "endpoints": endpoints,  # Detailed endpoint list
        },
    ).dict()

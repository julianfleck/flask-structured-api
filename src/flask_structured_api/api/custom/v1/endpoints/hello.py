from flask import Blueprint, request, g
from flask_structured_api.core.models.responses import SuccessResponse
from flask_structured_api.core.storage.decorators import store_api_data
from flask_structured_api.core.enums import StorageType
from flask_structured_api.core.auth import require_auth
from flask_structured_api.core.middleware.logging import log_request, log_response, debug_request, debug_response
from datetime import datetime

hello_bp = Blueprint('hello', __name__)


@hello_bp.route('/hello', methods=['POST'])
@require_auth
@debug_response
@store_api_data(
    storage_type=StorageType.BOTH,
    ttl_days=1,
    metadata={"check_type": "hello"}
)
@debug_request
def hello():
    """Simple hello endpoint to test request/response storage"""
    data = request.get_json() or {}
    name = data.get('name', 'World')

    return SuccessResponse(
        message="Hello!",
        data={
            "greeting": f"Hello, {name}!",
            "timestamp": datetime.utcnow().isoformat()
        }
    ).dict()

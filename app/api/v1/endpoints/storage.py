from flask import Blueprint, request, g
from app.core.auth import require_auth, require_roles
from app.core.db import get_session
from app.services.storage import StorageService
from app.models.requests.storage import StorageQueryRequest, StorageDeleteRequest
from app.models.responses import SuccessResponse
from app.models.enums import UserRole

storage_bp = Blueprint('storage', __name__)


@storage_bp.route('/query', methods=['POST'])
@require_auth
def query_storage():
    """Query stored API data"""
    data = request.get_json()
    query = StorageQueryRequest(**data)

    db = next(get_session())
    storage_service = StorageService(db)

    result = storage_service.query_storage(
        user_id=g.user_id,
        **query.dict()
    )

    return SuccessResponse(
        message="Storage entries retrieved",
        data=result.dict()
    ).dict()


@storage_bp.route('/delete', methods=['POST'])
@require_auth
@require_roles(UserRole.ADMIN)  # Only admins can delete storage
def delete_storage():
    """Delete stored API data"""
    data = request.get_json()
    delete_request = StorageDeleteRequest(**data)

    db = next(get_session())
    storage_service = StorageService(db)

    deleted_count = storage_service.delete_storage(
        user_id=g.user_id,
        storage_ids=delete_request.storage_ids,
        force=delete_request.force
    )

    return SuccessResponse(
        message=f"Deleted {deleted_count} storage entries",
        data={"deleted_count": deleted_count}
    ).dict()

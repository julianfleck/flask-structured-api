from datetime import datetime

from flask import Blueprint, current_app, g, request
from pydantic import ValidationError

from flask_structured_api.core.auth import require_auth, require_roles
from flask_structured_api.core.db import get_session
from flask_structured_api.core.enums import (
    StorageType,
    UserRole,
    WarningCode,
    WarningSeverity,
)
from flask_structured_api.core.exceptions.validation import (
    ValidationError,
    ValidationErrorCode,
)
from flask_structured_api.core.models.errors import (
    ErrorDetail,
    ValidationErrorDetail,
    ValidationErrorItem,
)
from flask_structured_api.core.models.requests.storage import (
    SessionQueryParamsRequest,
    SessionQueryRequest,
    StorageDeleteRequest,
    StorageQueryRequest,
)
from flask_structured_api.core.models.responses import ErrorResponse, SuccessResponse
from flask_structured_api.core.models.responses.warnings import ResponseWarning
from flask_structured_api.core.services.storage import StorageService
from flask_structured_api.core.warnings import WarningCollector

storage_bp = Blueprint("storage", __name__)


def _convert_storage_type(data: dict) -> dict:
    """Convert storage_type/type string to StorageType enum in request data"""
    # Handle both 'storage_type' and 'type' fields
    storage_type_field = 'storage_type' if 'storage_type' in data else 'type'

    if storage_type_field in data:
        try:
            data[storage_type_field] = StorageType(data[storage_type_field].upper())
        except ValueError:
            raise ValidationError(
                message=f"Invalid {storage_type_field.replace('_', ' ')}",
                code=ValidationErrorCode.INVALID_FORMAT,
                field=storage_type_field,
                context={"valid_values": [t.value for t in StorageType]}
            )
    return data


@storage_bp.route("/storage/query", methods=["POST"])
@require_auth
def query_storage():
    """Query stored API data"""
    try:
        data = request.get_json()
        if not isinstance(data, dict):
            raise ValidationError(
                message="Request body must be a JSON object",
                code=ValidationErrorCode.INVALID_FORMAT,
                field="body",
            )

        data = _convert_storage_type(data)
        query = StorageQueryRequest(**data)

        db = next(get_session())
        storage_service = StorageService(db)

        result = storage_service.query_storage(user_id=g.user_id, **query.model_dump())

        return SuccessResponse(
            message="Storage entries retrieved",
            data=result.model_dump()
        ).model_dump()

    except ValidationError as e:
        raise e
    except Exception as e:
        current_app.logger.error(f"Query storage error: {str(e)}")
        raise ValidationError(
            message="Failed to process storage query",
            code=ValidationErrorCode.INVALID_FORMAT,
            field="request",
            context={"error": str(e)},
        )


@storage_bp.route("/storage/delete", methods=["POST"])
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
        force=delete_request.force,
    )

    return SuccessResponse(
        message=f"Deleted {deleted_count} storage entries",
        data={"deleted_count": deleted_count},
    ).model_dump()


@storage_bp.route("/storage/sessions", methods=["GET"])
@require_auth
def list_sessions():
    """List user's storage sessions (simplified)"""
    try:
        # Pass all query parameters to validation
        query_dict = dict(request.args)

        # Convert known parameters to correct types
        if "page" in query_dict:
            query_dict["page"] = int(query_dict["page"])
        if "page_size" in query_dict:
            query_dict["page_size"] = int(query_dict["page_size"])
        if "storage_type" in query_dict:
            query_dict["storage_type"] = StorageType(query_dict["storage_type"])

        params = SessionQueryParamsRequest(**query_dict)
        query = params.to_session_query()

        # Exclude metadata_filters from the parameters
        query_params = query.model_dump(exclude={"metadata_filters"})

        db = next(get_session())
        storage_service = StorageService(db)

        result = storage_service.list_user_sessions(user_id=g.user_id, **query_params)

        # The result should already be a dictionary with sessions, total, page, etc.
        return SuccessResponse(
            message="Storage sessions listed",
            data=result,  # result should already be a dict
        ).model_dump()
    except ValidationError as e:
        # Let the global error handler handle validation errors
        raise e


@storage_bp.route("/storage/sessions/query", methods=["POST"])
@require_auth
def query_sessions():
    """Query storage sessions"""
    try:
        data = request.get_json()
        if not isinstance(data, dict):
            raise ValidationError(
                message="Request body must be a JSON object",
                code=ValidationErrorCode.INVALID_FORMAT,
                field="body",
            )

        data = _convert_storage_type(data)
        query = SessionQueryRequest(**data)

        db = next(get_session())
        storage_service = StorageService(db)

        result = storage_service.get_user_sessions(
            user_id=g.user_id, **query.model_dump()
        )

        return SuccessResponse(message="Sessions retrieved", data=result).model_dump()

    except ValidationError as e:
        raise e
    except Exception as e:
        current_app.logger.error(f"Query sessions error: {str(e)}")
        raise ValidationError(
            message="Failed to process session query",
            code=ValidationErrorCode.INVALID_FORMAT,
            field="request",
            context={"error": str(e)},
        )


@storage_bp.route("/storage/sessions/list", methods=["POST"])
@require_auth
def list_sessions_post():
    """List user's storage sessions with POST filters (simplified)"""
    data = request.get_json()
    query = SessionQueryRequest(**data)

    db = next(get_session())
    storage_service = StorageService(db)

    result = storage_service.list_user_sessions(user_id=g.user_id, **query.model_dump())

    return SuccessResponse(message="Storage sessions listed", data=result).model_dump()

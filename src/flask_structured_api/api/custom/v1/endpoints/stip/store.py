from flask import Blueprint, request, current_app, g
from flask_structured_api.core.auth import require_auth
from flask_structured_api.core.middleware.logging import debug_request, debug_response
from flask_structured_api.core.models.responses import SuccessResponse, ErrorResponse
from flask_structured_api.core.exceptions.validation import (
    ValidationError,
    ValidationErrorCode,
)
from flask_structured_api.core.enums import ErrorCode
from flask_structured_api.core.enums import StorageType
from flask_structured_api.core.models.errors import ErrorDetail
from flask_structured_api.core.models.requests import StorageQueryRequest
from flask_structured_api.core.services.storage import StorageService, StorageEntryResponse
from flask_structured_api.core.db import get_session
from flask_structured_api.core.models.requests.storage import StoreDataRequest, DataQueryRequest, DataQueryParamsRequest
from flask_structured_api.core.models.domain.storage import APIStorage
import json
from sqlalchemy import select

from flask_structured_api.core.storage.decorators import store_api_data

bp = Blueprint("stip_storage", __name__)

# Note: These endpoints don't have an associated service because it's using the
# storage decorators directly in order to store data in the database.


@bp.route("/<country_code>/data/store", methods=["POST"])
@require_auth
def store_data(country_code: str):
    """Store data for a given country code."""
    try:
        data = request.get_json()
        if not data:
            return ErrorResponse(
                message="No data provided",
                error=ErrorDetail(
                    code=ErrorCode.VALIDATION_ERROR,
                    details={"error": "Request body is empty"}
                )
            ).to_response(status_code=400)

        storage_service = StorageService(next(get_session()))

        # Store the data and refresh to ensure we have the latest state
        stored_data = storage_service.store_data(
            user_id=g.user_id,
            data=data,
            metadata={"country_code": country_code}
        )
        storage_service.db.refresh(stored_data)  # Refresh from DB instead of new query

        # Convert to response model and then to dict
        response_data = StorageEntryResponse(
            id=stored_data.id,
            created_at=stored_data.created_at,
            type=stored_data.storage_type,
            endpoint=stored_data.endpoint,
            ttl=stored_data.ttl,
            storage_info=stored_data.storage_metadata,
            data=json.loads(
                stored_data.response_data) if stored_data.response_data else None
        ).model_dump()  # Convert to dict using Pydantic's model_dump()

        # Return success response with stored data
        return SuccessResponse(
            message="Data stored successfully",
            data=response_data
        ).to_response(status_code=200)

    except Exception as e:
        current_app.logger.error(f"Failed to store data: {str(e)}", exc_info=True)
        return ErrorResponse(
            message="Failed to store data",
            error=ErrorDetail(
                code=ErrorCode.STORAGE_ERROR,
                details={"error": str(e)}
            )
        ).to_response(status_code=500)


@bp.route("/<country_code>/data/list", methods=["GET", "POST"])
@require_auth
def list_arbitrary_data(country_code: str):
    """
    List stored data for a given country code.

    This endpoint supports both GET and POST requests to retrieve stored data.
    The data can be filtered by date range, metadata, and pagination parameters.

    Args:
        country_code (str): The country code for which the data is being listed.

    Returns:
        JSON response with the list of stored data or an error message.
    """
    try:
        if request.method == "POST":
            query_request = DataQueryRequest(**request.get_json())
        else:
            query_request = DataQueryParamsRequest(**request.args).to_query_request()

        storage_service = StorageService(next(get_session()))

        # Get the raw result from storage service
        result = storage_service.list_data(
            user_id=g.user_id,
            start_date=query_request.start_date,
            end_date=query_request.end_date,
            metadata_filters=query_request.metadata_filters,
            page=query_request.page,
            page_size=query_request.page_size
        )

        # Transform items to only include metadata
        simplified_items = [
            {
                "id": item.id,
                "initiative_name": item.data.get("data").get("data").get("initiative_name"),
                "created_at": item.created_at,
                "country_code": item.storage_info.get("country_code"),
                "session_id": item.storage_info.get("session_id")
            }
            for item in result.items
        ]

        # Create new response with simplified items
        simplified_result = {
            "has_more": result.has_more,
            "items": simplified_items,
            "page": result.page,
            "page_size": result.page_size,
            "total": result.total
        }

        response = SuccessResponse(
            message="Data listed successfully",
            data=simplified_result
        ).to_response(status_code=200)
        return response

    except ValidationError as e:
        current_app.logger.error("Validation error: {}".format(str(e)))
        response = ErrorResponse(
            message="Invalid query format",
            error=ErrorDetail(
                code=e.code,
                details={
                    "context": e.context if hasattr(e, 'context') else {},
                    "field": e.field if hasattr(e, 'field') else None,
                    "error": str(e)
                }
            )
        ).to_response(status_code=400)
        return response
    except Exception as e:
        current_app.logger.error("Unexpected error in list_arbitrary_data: {}".format(
            str(e)), exc_info=True)
        response = ErrorResponse(
            message="Failed to list data",
            error=ErrorDetail(
                code="LIST_ERROR",
                details={"error": str(e)}
            )
        ).to_response(status_code=500)
        return response


@bp.route("/<country_code>/data/<int:storage_id>", methods=["GET"])
@require_auth
async def get_arbitrary_data(country_code: str, storage_id: int):
    """
    Retrieve specific stored data by storage ID for a given country code.

    This endpoint accepts a GET request to fetch data associated with a specific storage ID.

    Args:
        country_code (str): The country code for which the data is being retrieved.
        storage_id (int): The ID of the stored data to retrieve.

    Returns:
        JSON response with the retrieved data or an error message if not found.
    """
    try:
        storage_service = StorageService(next(get_session()))
        data = storage_service.get_data(user_id=g.user_id, storage_id=storage_id)

        if data is None:
            response = ErrorResponse(
                message="Data not found",
                error=ErrorDetail(
                    code=ErrorCode.DATA_NOT_FOUND,
                    details={"storage_id": storage_id}
                )
            ).to_response(status_code=404)
            return response

        response = SuccessResponse(
            message="Data retrieved successfully",
            data=data
        ).to_response(status_code=200)
        return response

    except Exception as e:
        current_app.logger.error("Unexpected error in get_arbitrary_data: {}".format(
            str(e)), exc_info=True)
        response = ErrorResponse(
            message="Failed to retrieve data",
            error=ErrorDetail(
                code=ErrorCode.RETRIEVE_ERROR,
                details={"error": str(e)}
            )
        ).to_response(status_code=500)
        return response


@bp.route("/<country_code>/data/delete/<identifier>", methods=["DELETE"])
@require_auth
def delete_data(country_code: str, identifier: str):
    """
    Delete stored data by storage ID or session ID for a given country code.
    """
    try:
        storage_service = StorageService(next(get_session()))

        # First check if data exists before attempting deletion
        if identifier.isdigit():
            # Check if storage_id exists
            data = storage_service.get_data(
                user_id=g.user_id, storage_id=int(identifier))
            if not data:
                return ErrorResponse(
                    message="Data not found",
                    error=ErrorDetail(
                        code=ErrorCode.DATA_NOT_FOUND,
                        details={"storage_id": identifier}
                    )
                ).to_response(status_code=404)

            # If exists, delete it
            storage_service.delete_storage(
                user_id=g.user_id,
                storage_ids=[int(identifier)],
                force=True
            )
        else:
            # Check if session exists by querying storage
            query_result = storage_service.query_storage(
                user_id=g.user_id,
                metadata_filters={"session_id": identifier}
            )

            if not query_result.items:
                return ErrorResponse(
                    message="Session not found",
                    error=ErrorDetail(
                        code=ErrorCode.DATA_NOT_FOUND,
                        details={"session_id": identifier}
                    )
                ).to_response(status_code=404)

            # If session exists, delete all associated entries
            storage_ids = [item.id for item in query_result.items]
            storage_service.delete_storage(
                user_id=g.user_id,
                storage_ids=storage_ids,
                force=True
            )

        return SuccessResponse(
            message="Data deleted successfully",
            data={"identifier": identifier}
        ).to_response(status_code=200)

    except Exception as e:
        current_app.logger.error(f"Unexpected error in delete_data: {str(e)}",
                                 exc_info=True)
        return ErrorResponse(
            message="Failed to delete data",
            error=ErrorDetail(
                code=ErrorCode.DELETE_ERROR,
                details={"error": str(e)}
            )
        ).to_response(status_code=500)

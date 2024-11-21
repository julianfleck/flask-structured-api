from flask import current_app, Response, make_response, request
from werkzeug.exceptions import HTTPException
from flask_structured_api.core.models.responses import ErrorResponse
from flask_structured_api.core.models.errors import ErrorDetail, HTTPErrorDetail
from flask_structured_api.core.exceptions import APIError


def handle_generic_error(error: Exception) -> Response:
    """Handle all unhandled exceptions"""
    if isinstance(error, APIError):
        return handle_api_error(error)

    error_context = {"error": str(error)}

    if current_app.debug:
        import traceback
        error_context.update({
            "error_type": error.__class__.__name__,
            "error_module": error.__class__.__module__,
            "traceback": traceback.format_exc(),
            "function": traceback.extract_tb(error.__traceback__)[-1].name
        })

    error_detail = ErrorDetail(
        code="INTERNAL_SERVER_ERROR",
        details=error_context
    )

    message = "An unexpected error occurred"
    if current_app.debug:
        message = "Error in {}.{}: {}".format(
            error.__class__.__module__,
            error.__class__.__name__,
            str(error)
        )

    response = ErrorResponse(
        success=False,
        error=error_detail,
        message=message
    )

    return make_response(response.model_dump(), 500)


def handle_api_error(error: APIError) -> Response:
    """Handle custom API errors"""
    from flask import request

    if isinstance(error, HTTPException):
        error_detail = HTTPErrorDetail(
            code=error.code,
            status=error.code,
            method=request.method,
            path=request.path
        )
    else:
        error_detail = ErrorDetail(
            code=error.code,
            details=error.details
        )

    response = ErrorResponse(
        success=False,
        error=error_detail,
        message=error.message
    )

    return make_response(response.dict(), getattr(error, 'status_code', 400))

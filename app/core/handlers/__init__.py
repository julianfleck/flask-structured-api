from flask import Flask, request, current_app, Response, make_response
from werkzeug.exceptions import HTTPException, BadRequest, Unauthorized, Forbidden, NotFound
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from jwt.exceptions import PyJWTError
from pydantic import ValidationError

from app.models.responses import ErrorResponse
from app.models.errors import HTTPErrorDetail, DatabaseErrorDetail, ValidationErrorItem, ValidationErrorDetail, ErrorDetail
from app.core.exceptions import APIError
from app.core.warnings import WarningCollector
from app.core.exceptions.validation import ValidationErrorCode


def register_error_handlers(app: Flask):
    """Register all error handlers"""

    @app.errorhandler(HTTPException)
    def handle_http_error(error):
        return ErrorResponse(
            message=str(error),
            error=HTTPErrorDetail(
                code=error.__class__.__name__.upper(),
                status=error.code,
                details={
                    "method": request.method,
                    "path": request.path
                }
            ).dict(),
            status=error.code
        ).dict(), error.code

    @app.errorhandler(SQLAlchemyError)
    def handle_db_error(error):
        """Handle database errors"""
        error_msg = str(error)
        error_details = {
            "error_type": error.__class__.__name__,
            "statement": getattr(error, 'statement', None),
        }

        if current_app.debug:
            # add more details in debug mode
            error_details.update({
                "full_error": str(error.__dict__),
                "params": getattr(error, 'params', None),
                "orig": str(getattr(error, 'orig', None))
            })

        detail = DatabaseErrorDetail(
            code="DB_ERROR",
            operation="query",
            message=error_msg,
            details=error_details
        )

        debug_msg = "Database error: {0}".format(error_msg)
        return ErrorResponse(
            success=False,
            message=debug_msg if current_app.debug else "Database error occurred",
            error=detail.dict(),
            status=500
        ).dict(), 500

    @app.errorhandler(Exception)
    def handle_generic_error(error: Exception) -> Response:
        """Handle all unhandled exceptions"""
        if isinstance(error, APIError):
            return handle_api_error(error)

        # Basic error info always included
        error_context = {
            "error": str(error)
        }

        # Add detailed context only in development mode
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

        # Use detailed message only in development mode
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

    @app.errorhandler(APIError)
    def handle_api_error(error: APIError) -> Response:
        """Handle custom API errors"""
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

    @app.errorhandler(ValidationError)
    def handle_validation_error(error):
        """Handle both custom and Pydantic validation errors"""
        # Handle Pydantic ValidationError
        if hasattr(error, 'errors'):
            validation_errors = []
            for err in error.errors():
                # Map Pydantic error types to our ValidationErrorCode
                error_type = err["type"]
                if "datetime" in error_type:
                    code = ValidationErrorCode.INVALID_FORMAT
                elif "missing" in error_type:
                    code = ValidationErrorCode.MISSING_FIELD
                else:
                    code = ValidationErrorCode.CONSTRAINT_VIOLATION

                field_path = " -> ".join(str(loc) for loc in err["loc"])
                validation_errors.append(
                    ValidationErrorItem(
                        field=field_path,
                        message=err["msg"],
                        type=code.value  # Use our semantic error codes
                    )
                )
        # Handle our custom ValidationError
        else:
            validation_errors = [
                ValidationErrorItem(
                    field=error.details["field"],
                    message=error.message,
                    type=error.code  # Already using our semantic codes
                )
            ]

        error_detail = ValidationErrorDetail(
            # Use the first error's code as main code
            code=validation_errors[0].type,
            errors=validation_errors,
            details={
                "total_errors": len(validation_errors),
                "validation_context": "request_payload",
                "validation_errors": [e.model_dump() for e in validation_errors]
            }
        )

        response = ErrorResponse(
            message=error.message if hasattr(
                error, 'message') else "Validation failed for request",
            error=error_detail,
            status=422
        )

        return response.model_dump(), 422

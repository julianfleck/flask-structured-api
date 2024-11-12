from flask import Flask, request, current_app
from werkzeug.exceptions import HTTPException, BadRequest, Unauthorized, Forbidden, NotFound
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from jwt.exceptions import PyJWTError
from pydantic import ValidationError

from app.models.responses import ErrorResponse
from app.models.errors import HTTPErrorDetail, DatabaseErrorDetail, ValidationErrorItem, ValidationErrorDetail, ErrorDetail
from app.core.exceptions import APIError


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

    @app.errorhandler(APIError)
    def handle_api_error(error):
        return ErrorResponse(
            message=error.message,
            error=ErrorDetail(
                code=error.code,
                details=error.details
            ),
            status=error.status_code
        ).dict(), error.status_code

    @app.errorhandler(ValidationError)
    def handle_validation_error(error):
        return ErrorResponse(
            message="Validation error",
            error=ValidationErrorDetail(
                code="VALIDATION_ERROR",
                errors=[
                    ValidationErrorItem(
                        field=e["loc"][-1],
                        message=e["msg"],
                        type=e["type"]
                    ) for e in error.errors()
                ]
            ).dict(),
            status=422
        ).dict(), 422

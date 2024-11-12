from flask import Flask, request
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
        if isinstance(error, IntegrityError):
            return ErrorResponse(
                message="Database constraint violation",
                error=DatabaseErrorDetail(
                    code="DB_INTEGRITY_ERROR",
                    operation=error.__class__.__name__,
                    constraint=str(error.orig)
                ),
                status=409
            ).dict(), 409

        return ErrorResponse(
            message="Database error occurred",
            error=DatabaseErrorDetail(
                code="DATABASE_ERROR",
                operation=error.__class__.__name__
            ),
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

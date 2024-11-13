from flask import Flask, request, current_app, Response, make_response
from werkzeug.exceptions import HTTPException, BadRequest, Unauthorized, Forbidden, NotFound
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from jwt.exceptions import PyJWTError
from pydantic import ValidationError

from app.models.responses import ErrorResponse
from app.models.errors import HTTPErrorDetail, DatabaseErrorDetail, ValidationErrorItem, ValidationErrorDetail, ErrorDetail
from app.core.exceptions import APIError
from app.core.warnings import WarningCollector


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
    def handle_api_error(error: APIError) -> Response:
        if isinstance(error, HTTPException):
            error_detail = HTTPErrorDetail(
                code=error.code,
                status=error.code,
                method=error.get_response().status,
                path=error.description
            )
        else:
            error_detail = ErrorDetail(
                code=error.code,
                details=error.details
            )

        # Get any collected warnings
        warning_collector = WarningCollector()
        warnings = [
            f"{w.code}: {w.message} (Severity: {w.severity})"
            for w in warning_collector.get_warnings()
        ]

        response = ErrorResponse(
            success=False,
            error=error_detail,
            message=error.message,
            warnings=warnings  # Include warnings in response
        )

        # Clear warnings after adding them to response
        warning_collector.clear_warnings()

        return make_response(response.model_dump(), getattr(error, 'status_code', 400))

    @app.errorhandler(ValidationError)
    def handle_validation_error(error):
        validation_errors = []

        # Get the model name from the error context
        model_name = None
        if hasattr(error, 'model'):
            model_name = error.model.__name__
        elif hasattr(error, '_model'):
            model_name = error._model.__name__
        elif hasattr(error, 'raw_errors') and error.raw_errors:  # Pydantic v2
            model_ctx = getattr(error.raw_errors[0], 'loc', None)
            if model_ctx:
                model_name = model_ctx[0]

        # Extract validation errors
        raw_errors = error.errors() if hasattr(error, 'errors') else [
            {'loc': ['unknown'], 'msg': str(error), 'type': 'validation_error'}]

        for e in raw_errors:
            field_path = " -> ".join(str(loc) for loc in e["loc"])
            validation_errors.append(
                ValidationErrorItem(
                    field=field_path,
                    message=e["msg"],
                    type=e["type"]
                )
            )

        # Get required fields from validation errors
        required_fields = [
            e.field for e in validation_errors
            if e.type == "value_error.missing"
        ]

        error_detail = ValidationErrorDetail(
            code="VALIDATION_ERROR",
            errors=validation_errors,
            required_fields=required_fields,
            details={
                "total_errors": len(validation_errors),
                "schema": model_name,
                "validation_context": "request_payload",
                "validation_errors": [e.model_dump() for e in validation_errors]
            }
        )

        model_str = model_name or 'request'
        message = f"Validation failed for {model_str}"

        response = ErrorResponse(
            message=message,
            error=error_detail,
            status=422
        )

        return response.model_dump(), 422

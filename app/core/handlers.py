from flask import Flask
from werkzeug.exceptions import BadRequest, NotFound, MethodNotAllowed
from sqlalchemy.exc import SQLAlchemyError
import jwt
from json.decoder import JSONDecodeError
from pydantic import ValidationError

from app.models.responses import ErrorResponse
from app.core.exceptions import APIError


def register_error_handlers(app: Flask):
    """Register all error handlers"""

    @app.errorhandler(APIError)
    def handle_api_error(error):
        return ErrorResponse(
            message=error.message,
            error={"code": error.code, "details": error.details},
            status=error.status_code
        ).dict(), error.status_code

    @app.errorhandler(ValidationError)
    def handle_validation_error(error):
        return ErrorResponse(
            message="Validation error",
            error={
                "code": "VALIDATION_ERROR",
                "details": {
                    "errors": [
                        {
                            "field": e["loc"][-1],
                            "message": e["msg"],
                            "type": e["type"]
                        } for e in error.errors()
                    ]
                }
            },
            status=422
        ).dict(), 422

    @app.errorhandler(BadRequest)
    def handle_bad_request(error):
        if "Failed to decode JSON" in str(error):
            return ErrorResponse(
                message="Invalid JSON format",
                error={
                    "code": "INVALID_JSON",
                    "details": {
                        "error": str(error).split(": ", 1)[1]
                    }
                },
                status=400
            ).dict(), 400
        return ErrorResponse(
            message=str(error),
            error={"code": "BAD_REQUEST"},
            status=400
        ).dict(), 400

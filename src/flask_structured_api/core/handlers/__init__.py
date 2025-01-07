from flask import Flask
from sqlalchemy.exc import SQLAlchemyError
from werkzeug.exceptions import HTTPException

from flask_structured_api.core.exceptions import APIError
from flask_structured_api.core.exceptions.validation import ValidationError

from .database import handle_db_error
from .generic import handle_api_error, handle_generic_error
from .http import handle_http_error
from .validation import handle_validation_error


def register_error_handlers(app: Flask):
    """Register all error handlers"""
    app.errorhandler(HTTPException)(handle_http_error)
    app.errorhandler(SQLAlchemyError)(handle_db_error)
    app.errorhandler(ValidationError)(handle_validation_error)
    app.errorhandler(Exception)(handle_generic_error)
    app.errorhandler(APIError)(handle_api_error)

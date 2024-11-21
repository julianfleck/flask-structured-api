from flask import Flask
from werkzeug.exceptions import HTTPException
from sqlalchemy.exc import SQLAlchemyError
from flask_structured_api.core.exceptions import APIError
from flask_structured_api.core.exceptions.validation import ValidationError

from .http import handle_http_error
from .database import handle_db_error
from .validation import handle_validation_error
from .generic import handle_generic_error, handle_api_error


def register_error_handlers(app: Flask):
    """Register all error handlers"""
    app.errorhandler(HTTPException)(handle_http_error)
    app.errorhandler(SQLAlchemyError)(handle_db_error)
    app.errorhandler(ValidationError)(handle_validation_error)
    app.errorhandler(Exception)(handle_generic_error)
    app.errorhandler(APIError)(handle_api_error)

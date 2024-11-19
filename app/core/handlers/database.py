from flask import current_app
from sqlalchemy.exc import SQLAlchemyError
from app.core.models.responses import ErrorResponse
from app.core.models.errors import DatabaseErrorDetail


def handle_db_error(error: SQLAlchemyError):
    """Handle database errors"""
    error_msg = str(error)
    error_details = {
        "error_type": error.__class__.__name__,
        "statement": getattr(error, 'statement', None),
    }

    if current_app.debug:
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

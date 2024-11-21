from pydantic import ValidationError
from flask_structured_api.core.models.responses import ErrorResponse
from flask_structured_api.core.models.errors import ValidationErrorDetail, ValidationErrorItem
from flask_structured_api.core.exceptions.validation import ValidationErrorCode


def handle_validation_error(error):
    """Handle both custom and Pydantic validation errors"""
    if hasattr(error, 'errors'):
        validation_errors = []
        for err in error.errors():
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
                    type=code.value
                )
            )
    else:
        validation_errors = [
            ValidationErrorItem(
                field=error.details["field"],
                message=error.message,
                type=error.code
            )
        ]

    error_detail = ValidationErrorDetail(
        code=validation_errors[0].type,
        errors=validation_errors,
        details={
            "total_errors": len(validation_errors),
            "validation_context": "request_payload",
            "validation_errors": [e.model_dump() for e in validation_errors]
        }
    )

    return ErrorResponse(
        message=error.message if hasattr(
            error, 'message') else "Validation failed for request",
        error=error_detail,
        status=422
    ).model_dump(), 422

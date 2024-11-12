# app/core/exceptions.py
from typing import Any, Dict


class APIError(Exception):
    """Base API error"""

    def __init__(self, message: str, code: str = None, details: dict = None):
        self.message = message
        self.code = code or self.__class__.__name__
        self.details = details or {}


class ValidationError(APIError):
    """Data validation error"""

    def __init__(self, message: str, field: str = None):
        super().__init__(
            message=message,
            code="validation_error",
            details={"field": field}
        )


class AIServiceError(APIError):
    """AI service error"""

    def __init__(self, message: str, details: dict = None):
        super().__init__(
            message=message,
            code="ai_service_error",
            details=details
        )


class AIResponseValidationError(APIError):
    """AI response validation error"""

    def __init__(self, message: str, validation_errors: Any = None):
        super().__init__(
            message=message,
            code="AI_INVALID_RESPONSE",
            details={"validation_errors": validation_errors}
        )

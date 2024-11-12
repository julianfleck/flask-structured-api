from typing import Any
from .base import APIError


class AIServiceError(APIError):
    """AI service error"""

    def __init__(self, message: str, details: dict = None):
        super().__init__(
            message=message,
            code="AI_SERVICE_ERROR",
            details=details,
            status_code=503
        )


class AIResponseValidationError(APIError):
    """AI response validation error"""

    def __init__(self, message: str, validation_errors: Any = None):
        super().__init__(
            message=message,
            code="AI_INVALID_RESPONSE",
            details={"validation_errors": validation_errors},
            status_code=422
        )

from typing import Any, Optional
from ..enums import AIErrorCode
from .base import APIError


class AIServiceError(APIError):
    """AI service error"""

    def __init__(self, message: str, code: AIErrorCode, details: dict = None):
        super().__init__(
            message=message,
            code=code,
            details=details,
            status_code=503
        )


class AIResponseValidationError(APIError):
    """AI response validation error"""

    def __init__(self, message: str, validation_errors: Any = None, raw_response: Any = None, confidence: float = None):
        details = {
            "validation_errors": validation_errors,
            "raw_response": raw_response,
            "confidence": confidence
        }
        super().__init__(
            message=message,
            code=AIErrorCode.INVALID_RESPONSE,
            details=details,
            status_code=422,
        )


class LengthFinishReasonError(AIServiceError):
    """Error raised when response is truncated due to length limits"""

    def __init__(self, message: str, completion: Optional[Any] = None):
        super().__init__(
            message=message,
            code=AIErrorCode.LENGTH_LIMIT_EXCEEDED,
            details={
                "completion": completion
            }
        )

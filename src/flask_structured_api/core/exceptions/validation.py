from enum import Enum
from typing import Any, Dict, Optional

from .base import APIError


class ValidationErrorCode(str, Enum):
    INVALID_FORMAT = "VAL_INVALID_FORMAT"
    MISSING_FIELD = "VAL_MISSING_FIELD"
    CONSTRAINT_VIOLATION = "VAL_CONSTRAINT_VIOLATION"
    FUTURE_DATE = "VAL_FUTURE_DATE"
    TYPE_ERROR = "VAL_TYPE_ERROR"
    RANGE_ERROR = "VAL_RANGE_ERROR"
    LENGTH_ERROR = "VAL_LENGTH_ERROR"
    REGEX_ERROR = "VAL_REGEX_ERROR"
    UNIQUE_ERROR = "VAL_UNIQUE_ERROR"


class ValidationError(APIError):
    """Data validation error"""

    def __init__(
        self,
        message: str,
        code: ValidationErrorCode,
        field: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(
            message=message,
            code=code.value,
            details={"field": field, "context": context or {}},
            status_code=422,
        )

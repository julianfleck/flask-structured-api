from .base import APIError


class ValidationError(APIError):
    """Data validation error"""

    def __init__(self, message: str, field: str = None):
        super().__init__(
            message=message,
            code="VALIDATION_ERROR",
            details={"field": field},
            status_code=422
        )

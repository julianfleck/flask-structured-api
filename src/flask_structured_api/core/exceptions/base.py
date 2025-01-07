from typing import Any, Dict, TYPE_CHECKING
from flask_structured_api.core.enums import ErrorCode, WarningCode, WarningSeverity
from flask_structured_api.core.models.errors import ErrorDetail
from flask_structured_api.core.warnings import WarningCollector

if TYPE_CHECKING:
    from flask_structured_api.core.models.responses.base import ErrorResponse


class APIError(Exception):
    """Base API error"""

    def __init__(
        self,
        message: str,
        code: ErrorCode = ErrorCode.INTERNAL_SERVER_ERROR,
        details: Dict[str, Any] = None,
        status_code: int = 400,
        **kwargs,  # Accept additional kwargs
    ):
        self.message = message
        self.code = code
        self.details = details or {}
        self.status_code = status_code

        # Collect unexpected parameters as warnings
        if kwargs:
            warning_collector = WarningCollector()
            unexpected_params = ", ".join(kwargs.keys())
            warning_collector.add_warning(
                message="Unexpected parameters in error construction: "
                + unexpected_params,
                code=WarningCode.UNEXPECTED_PARAM,
                severity=WarningSeverity.LOW,
            )

    def to_response(self) -> 'ErrorResponse':
        """Convert to proper API error response"""
        from flask_structured_api.core.models.responses.base import ErrorResponse
        return ErrorResponse(
            success=False,
            message=self.message,
            error=ErrorDetail(
                code=self.code,
                message=self.message,
                details=self.details,
            ),
            metadata=None,
        )

    def __str__(self):
        return self.message

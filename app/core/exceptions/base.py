from typing import Dict, Any
from app.core.warnings import WarningCollector
from app.models.enums import WarningCode, WarningSeverity


class APIError(Exception):
    """Base API error"""

    def __init__(
        self,
        message: str,
        code: str = None,
        details: Dict[str, Any] = None,
        status_code: int = 400,
        **kwargs  # Accept additional kwargs
    ):
        self.message = message
        self.code = code or self.__class__.__name__
        self.details = details or {}
        self.status_code = status_code

        # Collect unexpected parameters as warnings
        if kwargs:
            warning_collector = WarningCollector()
            unexpected_params = ", ".join(kwargs.keys())
            warning_collector.add_warning(
                message="Unexpected parameters in error construction: " + unexpected_params,
                code=WarningCode.UNEXPECTED_PARAM,
                severity=WarningSeverity.LOW
            )

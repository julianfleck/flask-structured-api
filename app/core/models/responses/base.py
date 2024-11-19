from typing import Optional, Dict, List, Any
from pydantic import BaseModel
from app.core.models.errors import ErrorDetail
from app.core.warnings import WarningCollector
from app.core.models.responses.warnings import ResponseWarning


class APIResponse(BaseModel):
    """Base response model for all API responses"""
    success: bool
    message: Optional[str] = None
    data: Optional[Dict[str, Any]] = None
    warnings: List[ResponseWarning] = []


class SuccessResponse(APIResponse):
    """Success response model for API responses"""
    success: bool = True

    def dict(self, *args, **kwargs):
        return self.model_dump(*args, **kwargs)

    def model_dump(self, *args, **kwargs):
        data = super().model_dump(*args, **kwargs)
        warning_collector = WarningCollector()

        data['warnings'] = [
            ResponseWarning(
                code=w.code,
                message=w.message,
                severity=w.severity
            ).model_dump()
            for w in warning_collector.get_warnings()
        ]

        return data


class ErrorResponse(APIResponse):
    """Error response model for API errors"""
    success: bool = False
    error: ErrorDetail

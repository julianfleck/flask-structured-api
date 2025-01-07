from typing import Any, Dict, List, Optional
from flask import jsonify, current_app
from pydantic import BaseModel

from flask_structured_api.core.models.errors import ErrorDetail
from flask_structured_api.core.models.responses.warnings import ResponseWarning
from flask_structured_api.core.warnings import WarningCollector
from flask_structured_api.core.middleware.cors import CORSMiddleware

cors = CORSMiddleware()


class APIResponse(BaseModel):
    """Base response model for all API responses"""

    success: bool
    message: Optional[str] = None
    data: Optional[Dict[str, Any]] = None
    warnings: List[ResponseWarning] = []
    metadata: Optional[Dict[str, Any]] = None


class SuccessResponse(APIResponse):
    """Success response model for API responses"""

    success: bool = True
    data: Dict[str, Any] = {}

    def dict(self, *args, **kwargs):
        return self.model_dump(*args, **kwargs)

    def model_dump(self, *args, **kwargs):
        data = super().model_dump(*args, **kwargs)
        warning_collector = WarningCollector()

        data["warnings"] = [
            ResponseWarning(
                code=w.code, message=w.message, severity=w.severity
            ).model_dump()
            for w in warning_collector.get_warnings()
        ]

        return data

    def to_response(self, status_code: int = 200):
        """Convert success to Flask response"""
        warning_collector = current_app.warning_collector
        response_data = self.model_dump()
        response_data["warnings"] = [
            ResponseWarning(
                code=w.code, message=w.message, severity=w.severity
            ).model_dump()
            for w in warning_collector.get_warnings()
        ]
        response = jsonify(response_data)
        response.status_code = status_code
        return response


class ErrorResponse(APIResponse):
    """Error response model for API errors"""

    success: bool = False
    error: ErrorDetail

    def to_response(self, status_code: int = 500):
        """Convert error to Flask response with CORS headers"""
        response = jsonify(self.model_dump())
        response.status_code = status_code
        return cors.handle_cors(response)

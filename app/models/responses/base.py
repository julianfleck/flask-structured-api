from typing import Optional, Dict, List, Any
from pydantic import BaseModel
from app.models.errors import ErrorDetail


class APIResponse(BaseModel):
    """Base response model for all API responses"""
    success: bool
    message: Optional[str] = None
    data: Optional[Dict[str, Any]] = None
    warnings: List[str] = []


class SuccessResponse(APIResponse):
    """Success response model for API responses"""
    success: bool = True


class ErrorResponse(APIResponse):
    """Error response model for API errors"""
    success: bool = False
    error: ErrorDetail

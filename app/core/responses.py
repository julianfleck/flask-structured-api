from typing import Optional, Dict, List, Any
from pydantic import BaseModel


class ErrorDetail(BaseModel):
    """Error details model for API error responses"""
    code: str
    details: Optional[Dict[str, Any]] = None


class APIResponse(BaseModel):
    """Base response model for all API responses"""
    success: bool
    message: Optional[str] = None
    data: Optional[Dict[str, Any]] = None
    warnings: List[str] = []


class ErrorResponse(APIResponse):
    """Error response model for API errors"""
    success: bool = False
    error: ErrorDetail
    status: int


class SuccessResponse(APIResponse):
    """Success response model for API responses"""
    success: bool = True

from typing import Optional, Dict, Any, List
from pydantic import BaseModel


class ErrorDetail(BaseModel):
    """Base error detail model"""
    code: str
    details: Optional[Dict[str, Any]] = None


class ValidationErrorItem(BaseModel):
    """Validation error item"""
    field: str
    message: str
    type: str


class ValidationErrorDetail(ErrorDetail):
    """Validation error details"""
    errors: List[ValidationErrorItem]


class HTTPErrorDetail(ErrorDetail):
    """HTTP error details"""
    status: int
    method: Optional[str] = None
    path: Optional[str] = None


class DatabaseErrorDetail(ErrorDetail):
    """Database error details"""
    operation: str
    table: Optional[str] = None
    constraint: Optional[str] = None


class AuthErrorDetail(ErrorDetail):
    """Authentication error details"""
    reason: str
    required_permissions: Optional[List[str]] = None

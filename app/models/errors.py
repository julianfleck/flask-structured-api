from typing import Optional, Dict, Any, List
from pydantic import BaseModel


class ErrorDetail(BaseModel):
    """Error details model"""
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

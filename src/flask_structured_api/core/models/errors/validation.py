from typing import Any, Dict, List, Optional

from pydantic import BaseModel

from .base import ErrorDetail


class ValidationErrorItem(BaseModel):
    """Validation error item"""

    field: str
    message: str
    type: str


class ValidationErrorDetail(ErrorDetail):
    """Validation error details"""

    code: str
    errors: List[ValidationErrorItem]
    details: Optional[Dict[str, Any]] = None
    required_fields: Optional[List[str]] = None

from typing import Optional, Dict, Any
from pydantic import BaseModel


class ErrorDetail(BaseModel):
    """Base error detail model"""
    code: str
    details: Optional[Dict[str, Any]] = None

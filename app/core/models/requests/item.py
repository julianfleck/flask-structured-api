from typing import Optional, Dict, Any
from pydantic import Field
from app.core.models.requests.base import BaseRequestModel


class CreateItemRequest(BaseRequestModel):
    """Example request validation model"""
    name: str = Field(..., min_length=3, max_length=100)
    description: str = Field(..., max_length=500)
    properties: Dict[str, Any] = Field(default_factory=dict)


class UpdateItemRequest(BaseRequestModel):
    """Example update request model"""
    name: Optional[str] = Field(None, min_length=3, max_length=100)
    description: Optional[str] = None
    properties: Optional[Dict[str, Any]] = None

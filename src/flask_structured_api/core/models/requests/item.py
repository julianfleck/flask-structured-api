from typing import Any, Dict, Optional

from pydantic import Field

from flask_structured_api.core.models.requests.base import BaseRequestModel


class CreateItemRequest(BaseRequestModel):
    """Example request validation model"""

    name: str = Field(..., min_length=3, max_length=200)
    description: str = Field(..., max_length=500)
    properties: Dict[str, Any] = Field(default_factory=dict)


class UpdateItemRequest(BaseRequestModel):
    """Example update request model"""

    name: Optional[str] = Field(None, min_length=3, max_length=200)
    description: Optional[str] = None
    properties: Optional[Dict[str, Any]] = None

# app/models/responses/model.py
from datetime import datetime
from typing import Any, Dict, List, Optional

from flask_structured_api.core.models.responses.base_model import BaseResponseModel


class ItemResponse(BaseResponseModel):
    """Example response model"""

    id: int
    name: str
    description: str
    properties: Dict[str, Any]
    created_at: datetime


class ItemListResponse(BaseResponseModel):
    """Example paginated response"""

    items: List[ItemResponse]
    total: int
    page: int
    size: int
    has_more: bool

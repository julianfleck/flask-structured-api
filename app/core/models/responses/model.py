# app/models/responses/model.py
from typing import Optional, List, Dict, Any
from datetime import datetime
from app.core.models.responses.base_model import BaseResponseModel


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

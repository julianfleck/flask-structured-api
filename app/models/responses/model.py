# app/models/responses/model.py
from typing import Optional, List
from app.models.core.base import BaseResponseModel


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

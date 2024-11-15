from typing import List, Optional, Dict, Any, Literal
from datetime import datetime
from app.models.core.base import BaseResponseModel
from app.models.enums import StorageType
from pydantic import Field
import json
from flask import current_app


class StorageEntryResponse(BaseResponseModel):
    """Single storage entry response"""
    id: int
    type: StorageType
    endpoint: str
    created_at: datetime
    ttl: Optional[datetime]
    storage_info: Dict[str, Any] = Field(default_factory=dict)
    data: Optional[Any] = None

    class Config:
        from_attributes = True
        populate_by_name = True
        def alias_generator(x): return "storage_type" if x == "type" else x

    @classmethod
    def from_orm(cls, obj):
        data = super().from_orm(obj)
        data.storage_info = obj.storage_metadata or {}
        data.type = obj.storage_type

        source_data = obj.request_data if obj.storage_type == StorageType.REQUEST else obj.response_data
        if source_data:
            try:
                raw_data = obj.decompress_data(source_data) if obj.compressed \
                    else source_data.decode('utf-8')
                data.data = json.loads(raw_data) if raw_data else None
            except Exception as e:
                current_app.logger.warning(
                    f"Failed to decode {data.type} data: {e}")
                data.data = None

        return data


class StorageListResponse(BaseResponseModel):
    """Paginated storage entries response"""
    items: List[StorageEntryResponse]
    total: int
    page: int
    page_size: int
    has_more: bool


class SessionResponse(BaseResponseModel):
    """Session response model"""
    session_id: str
    created_at: datetime
    last_activity: datetime
    endpoints: List[str]
    entries: List[StorageEntryResponse]


class SessionListItemResponse(BaseResponseModel):
    """Simple session list item response"""
    session_id: str
    user_id: int
    created_at: datetime
    last_activity: datetime
    endpoints: List[str]


class SimpleSessionListResponse(BaseResponseModel):
    """Paginated simple session list response"""
    sessions: List[SessionListItemResponse]
    total: int
    page: int
    page_size: int
    has_more: bool

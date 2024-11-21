from typing import Optional, Dict, Any, List
from datetime import datetime, timezone
from pydantic import Field, field_validator
from flask_structured_api.core.models.requests.base import BaseRequestModel
from flask_structured_api.core.enums import StorageType


class StorageQueryRequest(BaseRequestModel):
    """Request model for querying stored data"""
    storage_type: Optional[StorageType] = Field(default=None, alias="type")
    endpoint: Optional[str] = None
    start_date: Optional[datetime] = Field(default=None)
    end_date: Optional[datetime] = Field(default=None)
    metadata_filters: Optional[Dict[str, Any]] = Field(default=None)
    session_id: Optional[str] = Field(default=None)  # Add this field
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=20, ge=1, le=100)


class SessionQueryRequest(BaseRequestModel):
    """Request model for querying sessions"""
    endpoint: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    session_id: Optional[str] = None
    storage_type: Optional[StorageType] = Field(default=None, alias="type")
    metadata_filters: Dict[str, Any] = Field(default_factory=dict)
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=20, ge=1, le=100)
    entries_per_session: Optional[int] = Field(default=20, ge=1)


class StorageDeleteRequest(BaseRequestModel):
    """Request model for deleting stored data"""
    storage_ids: List[int] = Field(..., min_items=1)
    # Force delete even if TTL hasn't expired
    force: bool = Field(default=False)


class SessionQueryParamsRequest(BaseRequestModel):
    """Request model for querying sessions via GET parameters"""
    endpoint: Optional[str] = Field(default=None)
    start_date: Optional[datetime] = Field(default=None)
    end_date: Optional[datetime] = Field(default=None)
    session_id: Optional[str] = Field(default=None)
    storage_type: Optional[StorageType] = Field(default=None)
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=20, ge=1, le=100)

    def to_session_query(self) -> SessionQueryRequest:
        """Convert to SessionQueryRequest"""
        data = self.model_dump()
        return SessionQueryRequest(
            endpoint=self.endpoint.strip('/') if self.endpoint else None,
            start_date=data['start_date'],
            end_date=data['end_date'],
            session_id=self.session_id,
            storage_type=self.storage_type,
            page=self.page,
            page_size=self.page_size
        )

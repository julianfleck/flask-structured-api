from typing import List, Optional, Dict, Any
from datetime import datetime
from flask_structured_api.core.models.responses.base_model import BaseResponseModel
from flask_structured_api.core.enums import StorageType
from pydantic import Field
import json
from flask import current_app


class StorageEntryResponse(BaseResponseModel):
    """
    Response model for a single storage entry.

    Attributes:
        id: Unique identifier of the storage entry
        type: Type of storage (request/response)
        endpoint: API endpoint that generated this entry
        created_at: Timestamp when the entry was created
        ttl: Time-to-live timestamp after which the entry may be deleted
        storage_info: Additional metadata about the storage entry
        data: The actual stored data
    """
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
        """
        Custom ORM conversion that handles data decompression and JSON parsing.

        Args:
            obj: The ORM model instance

        Returns:
            StorageEntryResponse: Converted response model
        """
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


class SessionListItemResponse(BaseResponseModel):
    """
    Response model for a session list item without entries.

    Attributes:
        session_id: Unique identifier of the session
        user_id: ID of the user who owns this session
        created_at: Timestamp when the session was created
        last_activity: Timestamp of the last activity in this session
        endpoints: List of endpoints accessed in this session
        total_entries: Total number of entries in this session
        entries_shown: Number of entries included in this response
        has_more_entries: Whether there are more entries available
    """
    session_id: str
    user_id: int
    created_at: datetime
    last_activity: datetime
    endpoints: List[str]
    total_entries: int
    entries_shown: int
    has_more_entries: bool = False

    class Config:
        from_attributes = True


class SessionWithEntriesResponse(SessionListItemResponse):
    """
    Response model for a session including its entries.
    Extends SessionListItemResponse to include the actual entries.

    Additional Attributes:
        entries: List of storage entries belonging to this session
    """
    entries: List[StorageEntryResponse]


class SimpleSessionListResponse(BaseResponseModel):
    """
    Response model for paginated list of sessions without their entries.

    Attributes:
        sessions: List of sessions with basic information
        total: Total number of sessions matching the query
        page: Current page number
        page_size: Number of sessions per page
        has_more: Whether there are more pages available
    """
    sessions: List[SessionListItemResponse]
    total: int
    page: int
    page_size: int
    has_more: bool


class DetailedSessionListResponse(BaseResponseModel):
    """
    Response model for paginated list of sessions including their entries.

    Attributes:
        sessions: List of sessions with their entries
        total: Total number of sessions matching the query
        page: Current page number
        page_size: Number of sessions per page
        has_more: Whether there are more pages available
    """
    sessions: List[SessionWithEntriesResponse]
    total: int
    page: int
    page_size: int
    has_more: bool


class StorageListResponse(BaseResponseModel):
    """
    Response model for paginated list of storage entries.

    Attributes:
        items: List of storage entries
        total: Total number of entries matching the query
        page: Current page number
        page_size: Number of entries per page
        has_more: Whether there are more pages available
    """
    items: List[StorageEntryResponse]
    total: int
    page: int
    page_size: int
    has_more: bool

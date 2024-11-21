from sqlmodel import SQLModel, Field, Relationship
from datetime import datetime
from typing import Optional, Dict, Any
from sqlalchemy import JSON, ForeignKey
from flask_structured_api.core.models.domain.base import CoreModel
from flask_structured_api.core.models.domain.user import User
from flask_structured_api.core.enums import StorageType
import json
import zlib


class StorageBase(CoreModel):
    """Base model for all storage types"""
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(index=True)
    endpoint: str = Field(index=True)
    ttl: Optional[datetime] = Field(default=None, index=True)
    compressed: bool = Field(default=False)
    storage_metadata: Dict[str, Any] = Field(sa_type=JSON)

    model_config = {
        "json_schema_extra": {
            "storage_metadata": {}
        }
    }

    def compress_data(self, data: Dict) -> bytes:
        """Compress JSON data"""
        if not self.compressed:
            return json.dumps(data).encode()
        return zlib.compress(json.dumps(data).encode())

    def decompress_data(self, data: bytes) -> Dict:
        """Decompress stored data"""
        if not self.compressed:
            return json.loads(data.decode())
        return json.loads(zlib.decompress(data).decode())


class APIStorage(StorageBase, table=True):
    """Storage model for API requests/responses"""
    __tablename__ = "api_storage"

    model_config = {
        "arbitrary_types_allowed": True,
        "json_schema_extra": {
            "storage_metadata": {}
        }
    }

    storage_type: StorageType = Field(index=True)
    request_data: Optional[bytes] = Field(default=None)
    response_data: Optional[bytes] = Field(default=None)
    user_id: Optional[int] = Field(default=None, foreign_key="users.id")
    user: Optional["User"] = Relationship(back_populates="storage_entries")

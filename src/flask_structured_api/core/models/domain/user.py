from datetime import datetime
from typing import Any, Dict, List, Optional

from sqlalchemy import JSON
from sqlmodel import Field, Relationship

from flask_structured_api.core.enums import UserRole
from flask_structured_api.core.models.domain.base import CoreModel


class User(CoreModel, table=True):
    """User model with enhanced tracking fields"""

    __tablename__ = "users"

    # Primary key
    id: Optional[int] = Field(default=None, primary_key=True)

    # Required fields
    email: str = Field(unique=True, index=True)
    hashed_password: str
    full_name: str

    # Optional fields with proper types
    role: UserRole = Field(default=UserRole.USER)
    is_active: bool = Field(default=True)
    last_login_at: Optional[datetime] = Field(default=None, nullable=True)
    login_count: int = Field(default=0)

    # JSON fields with defaults
    preferences: Dict[str, Any] = Field(default={}, sa_type=JSON)
    permissions: List[str] = Field(default=[], sa_type=JSON)

    # Relationships
    api_keys: List["APIKey"] = Relationship(
        back_populates="user", sa_relationship_kwargs={"lazy": "selectin"}
    )
    storage_entries: List["APIStorage"] = Relationship(
        back_populates="user", sa_relationship_kwargs={"lazy": "selectin"}
    )

    model_config = {"json_schema_extra": {"preferences": {}, "permissions": []}}

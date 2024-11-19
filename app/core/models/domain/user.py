from typing import Optional, Dict, Any, List
from sqlmodel import Field, Relationship
from datetime import datetime
from sqlalchemy import JSON

from app.core.models.domain.base import CoreModel
from app.core.enums import UserRole


class User(CoreModel, table=True):
    """User model with enhanced tracking fields"""
    __tablename__ = "users"

    model_config = {
        "arbitrary_types_allowed": True
    }

    email: str = Field(unique=True, index=True)
    hashed_password: str
    full_name: str
    role: str = Field(default=UserRole.USER)
    is_active: bool = Field(default=True)
    last_login_at: Optional[datetime] = Field(default=None)
    login_count: int = Field(default=0)
    preferences: Dict[str, Any] = Field(default_factory=dict, sa_type=JSON)
    permissions: List[str] = Field(default_factory=list, sa_type=JSON)

    # Relationships using forward references
    api_keys: List["APIKey"] = Relationship(back_populates="user")
    storage_entries: List["APIStorage"] = Relationship(back_populates="user")

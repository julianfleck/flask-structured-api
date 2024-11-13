from typing import Optional, Dict, Any, List
from sqlmodel import Field, Relationship
from datetime import datetime
from sqlalchemy import JSON

from app.models.core.base import CoreModel
from app.models.enums import UserRole


class User(CoreModel, table=True):
    """User model with enhanced tracking fields"""
    __tablename__ = "users"

    email: str = Field(unique=True, index=True)
    hashed_password: str
    full_name: str
    role: str = Field(default=UserRole.USER)
    is_active: bool = Field(default=True)
    last_login_at: Optional[datetime] = Field(default=None)
    login_count: int = Field(default=0)
    preferences: Dict[str, Any] = Field(default_factory=dict, sa_type=JSON)
    permissions: List[str] = Field(default_factory=list, sa_type=JSON)

    # Relationships
    items: List["Item"] = Relationship(back_populates="user")

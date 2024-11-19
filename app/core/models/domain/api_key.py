from datetime import datetime
from typing import Optional, List
from sqlmodel import Field, Relationship
from sqlalchemy import JSON
from app.core.models.domain.base import CoreModel


class APIKey(CoreModel, table=True):
    """API Key model for tracking active keys"""
    __tablename__ = "api_keys"

    key_hash: str = Field(index=True)
    user_id: int = Field(foreign_key="users.id", index=True)
    name: str
    last_used_at: Optional[datetime] = Field(default=None)
    expires_at: Optional[datetime] = Field(default=None)
    is_active: bool = Field(default=True)
    scopes: List[str] = Field(default_factory=list, sa_type=JSON)

    # Add relationship
    user: Optional["User"] = Relationship(back_populates="api_keys")

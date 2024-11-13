from sqlmodel import Field, Relationship
from app.models.core.base import CoreModel
from typing import Dict, Any
from sqlalchemy import JSON


class Item(CoreModel, table=True):
    """Example domain model"""
    __tablename__ = "items"

    name: str = Field(index=True)
    description: str
    properties: Dict[str, Any] = Field(default_factory=dict, sa_type=JSON)
    user_id: int = Field(foreign_key="users.id")

    # Relationships
    user: "User" = Relationship(back_populates="items")

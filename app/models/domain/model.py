from sqlmodel import Field, Relationship
from app.models.core.base import CoreModel


class Item(CoreModel, table=True):
    """Example domain model"""
    name: str = Field(index=True)
    description: str
    properties: Dict[str, Any]
    user_id: int = Field(foreign_key="user.id")

    # Relationships
    user: "User" = Relationship(back_populates="items")

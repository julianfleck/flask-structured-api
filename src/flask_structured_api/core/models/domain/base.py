from datetime import datetime
from typing import Any, Dict, Optional

from sqlalchemy import JSON
from sqlmodel import Field, Relationship, SQLModel


class CoreModel(SQLModel):
    """Base model with common fields"""

    id: Optional[int] = None
    created_at: datetime = None
    updated_at: datetime = None

    model_config = {
        "arbitrary_types_allowed": True,
        "from_attributes": True,
        "validate_assignment": True,
        "populate_by_name": True,
        "extra": "allow",
    }

    def __init__(self, **data):
        # Initialize with empty values first
        data.setdefault("created_at", datetime.utcnow())
        data.setdefault("updated_at", datetime.utcnow())
        super().__init__(**data)

from datetime import datetime
from typing import Optional
from sqlmodel import SQLModel, Field


class CoreModel(SQLModel):
    """Base model for all database models"""
    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(
        default_factory=datetime.utcnow,
        sa_column_kwargs={"onupdate": datetime.utcnow}
    )

# Base models for different concerns


class BaseRequestModel(SQLModel):
    """Base model for API requests"""
    class Config:
        extra = "forbid"  # Prevent additional properties


class BaseResponseModel(SQLModel):
    """Base model for API responses"""
    class Config:
        from_attributes = True


class BaseAIValidationModel(SQLModel):
    """Base model for AI response validation"""
    class Config:
        extra = "forbid"
        strict = True  # Strict type checking for AI responses

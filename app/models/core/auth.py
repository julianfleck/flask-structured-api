from enum import Enum
from typing import Optional
from sqlmodel import Field
from app.models.core.base import CoreModel


class UserRole(str, Enum):
    ADMIN = "admin"
    USER = "user"
    READONLY = "readonly"


class User(CoreModel, table=True):
    """Core user model"""
    email: str = Field(unique=True, index=True)
    hashed_password: str
    full_name: str
    role: UserRole = Field(default=UserRole.USER)
    is_active: bool = Field(default=True)

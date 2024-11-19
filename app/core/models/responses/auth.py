from app.models.core.base import BaseResponseModel
from typing import Dict, Any, List, Optional
from datetime import datetime
from pydantic import Field


class TokenResponse(BaseResponseModel):
    """Authentication token response"""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int


class UserResponse(BaseResponseModel):
    """User data response with detailed user information"""
    id: int
    email: str
    full_name: str
    role: str
    is_active: bool
    created_at: datetime
    updated_at: datetime
    last_login_at: Optional[datetime] = None
    login_count: int = 0
    preferences: Dict[str, Any] = Field(default_factory=dict)
    permissions: List[str] = Field(default_factory=list)

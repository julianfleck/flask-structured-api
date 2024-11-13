# app/models/requests/auth.py
from pydantic import EmailStr, Field
from app.models.core.base import BaseRequestModel
from typing import List, Optional


class RegisterRequest(BaseRequestModel):
    """User registration request"""
    email: EmailStr
    password: str = Field(..., min_length=8)
    full_name: str = Field(..., min_length=2)


class LoginRequest(BaseRequestModel):
    """Login request"""
    email: EmailStr
    password: str


class RefreshTokenRequest(BaseRequestModel):
    """Refresh token request"""
    refresh_token: str


class APIKeyRequest(BaseRequestModel):
    """API key creation request"""
    name: str = Field(..., min_length=1, max_length=100)
    scopes: List[str] = Field(default_factory=list)
    expires_in_days: Optional[int] = None  # Optional expiration

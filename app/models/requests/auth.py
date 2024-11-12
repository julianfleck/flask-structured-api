# app/models/requests/auth.py
from pydantic import EmailStr, Field
from app.models.core.base import BaseRequestModel


class RegisterRequest(BaseRequestModel):
    """User registration request"""
    email: EmailStr
    password: str = Field(..., min_length=8)
    full_name: str = Field(..., min_length=2)


class LoginRequest(BaseRequestModel):
    """Login request"""
    email: EmailStr
    password: str

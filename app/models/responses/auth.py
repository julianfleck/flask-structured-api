from app.models.core.base import BaseResponseModel


class TokenResponse(BaseResponseModel):
    """Authentication token response"""
    access_token: str
    token_type: str = "bearer"
    expires_in: int


class UserResponse(BaseResponseModel):
    """User data response"""
    id: int
    email: str
    full_name: str
    role: str
    is_active: bool

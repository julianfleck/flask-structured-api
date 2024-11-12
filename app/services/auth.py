from typing import Optional
from sqlmodel import Session, select

from app.core.auth import Auth
from app.core.exceptions import APIError
from app.models.core.auth import User, UserRole
from app.models.requests.auth import RegisterRequest, LoginRequest
from app.models.responses.auth import TokenResponse, UserResponse


class AuthService:
    """Service for handling authentication and user management"""

    def __init__(self, db: Session):
        self.db = db
        self.auth = Auth()

    def register_user(self, request: RegisterRequest) -> UserResponse:
        """Register a new user"""
        # Check if user exists
        if self.get_user_by_email(request.email):
            raise APIError(
                message="User already exists",
                code="AUTH_USER_EXISTS",
                status_code=400
            )

        # Create user
        user = User(
            email=request.email,
            hashed_password=Auth.generate_password_hash(request.password),
            full_name=request.full_name,
            role=UserRole.USER
        )

        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)

        return UserResponse.from_orm(user)

    def login(self, request: LoginRequest) -> TokenResponse:
        """Authenticate user and return tokens"""
        user = self.get_user_by_email(request.email)

        if not user or not Auth.verify_password(request.password, user.hashed_password):
            raise APIError(
                message="Invalid email or password",
                code="AUTH_INVALID_CREDENTIALS",
                status_code=401
            )

        if not user.is_active:
            raise APIError(
                message="User account is disabled",
                code="AUTH_ACCOUNT_DISABLED",
                status_code=401
            )

        return Auth.create_tokens(user.id)

    def get_user_by_email(self, email: str) -> Optional[User]:
        """Get user by email"""
        return self.db.exec(
            select(User).where(User.email == email)
        ).first()

    def get_user_by_id(self, user_id: int) -> Optional[User]:
        """Get user by ID"""
        return self.db.get(User, user_id)

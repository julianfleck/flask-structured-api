from typing import Optional
from sqlmodel import Session, select
import jwt
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash, check_password_hash

from app.core.exceptions.auth import InvalidCredentialsError, AuthenticationError
from app.models.user import User
from app.models.enums import UserRole
from app.models.requests.auth import RegisterRequest, LoginRequest
from app.models.responses.auth import TokenResponse, UserResponse
from app.core.config import settings
from app.core.exceptions import APIError


class Auth:
    @staticmethod
    def generate_password_hash(password: str) -> str:
        return generate_password_hash(password)

    @staticmethod
    def verify_password(password: str, hashed_password: str) -> bool:
        return check_password_hash(hashed_password, password)

    @staticmethod
    def create_tokens(user_id: int) -> TokenResponse:
        access_token = Auth._create_token(
            user_id,
            settings.ACCESS_TOKEN_EXPIRE_MINUTES,
            settings.JWT_SECRET_KEY
        )
        refresh_token = Auth._create_token(
            user_id,
            settings.REFRESH_TOKEN_EXPIRE_MINUTES,
            settings.JWT_REFRESH_SECRET_KEY,
            token_type='refresh'
        )
        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
        )

    @staticmethod
    def decode_token(token: str, refresh: bool = False) -> dict:
        try:
            secret = settings.JWT_REFRESH_SECRET_KEY if refresh else settings.JWT_SECRET_KEY
            return jwt.decode(token, secret, algorithms=["HS256"])
        except jwt.ExpiredSignatureError:
            raise APIError(
                message="Token has expired",
                code="AUTH_TOKEN_EXPIRED",
                status_code=401
            )
        except jwt.InvalidTokenError:
            raise APIError(
                message="Invalid token",
                code="AUTH_INVALID_TOKEN",
                status_code=401
            )

    @staticmethod
    def _create_token(user_id: int, expire_minutes: int, secret: str, token_type: str = 'access') -> str:
        expire = datetime.utcnow() + timedelta(minutes=expire_minutes)
        return jwt.encode(
            {"sub": str(user_id), "exp": expire, "type": token_type},
            secret,
            algorithm="HS256"
        )


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
        """Authenticate user and update login statistics"""
        user = self.get_user_by_email(request.email)

        if not user or not Auth.verify_password(request.password, user.hashed_password):
            raise InvalidCredentialsError()

        if not user.is_active:
            raise AuthenticationError(
                message="User account is disabled",
                code="AUTH_ACCOUNT_DISABLED"
            )

        # Update login statistics
        user.last_login_at = datetime.utcnow()
        user.login_count += 1
        self.db.commit()

        return Auth.create_tokens(user.id)

    def get_user_by_email(self, email: str) -> Optional[User]:
        """Get user by email"""
        return self.db.exec(
            select(User).where(User.email == email)
        ).first()

    def get_user_by_id(self, user_id: int) -> Optional[User]:
        """Get user by ID"""
        return self.db.get(User, user_id)

    def refresh_token(self, refresh_token: str) -> TokenResponse:
        """Refresh access token using refresh token"""
        try:
            # Decode and validate refresh token
            payload = Auth.decode_token(refresh_token)

            # Verify it's a refresh token
            if payload.get('type') != 'refresh':
                raise APIError(
                    message="Invalid token type",
                    code="AUTH_INVALID_TOKEN_TYPE",
                    status_code=401
                )

            user_id = int(payload['sub'])
            user = self.get_user_by_id(user_id)

            if not user or not user.is_active:
                raise APIError(
                    message="User not found or inactive",
                    code="AUTH_USER_INVALID",
                    status_code=401
                )

            # Create new access token
            access_token = Auth.create_token(user_id)

            return TokenResponse(
                access_token=access_token,
                refresh_token=refresh_token,  # Return same refresh token
                expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
            )

        except jwt.ExpiredSignatureError:
            raise APIError(
                message="Refresh token has expired",
                code="AUTH_REFRESH_TOKEN_EXPIRED",
                status_code=401
            )
        except jwt.InvalidTokenError:
            raise APIError(
                message="Invalid refresh token",
                code="AUTH_REFRESH_TOKEN_INVALID",
                status_code=401
            )

    def validate_token(self, token: str) -> User:
        """Validate token and return user"""
        try:
            payload = Auth.decode_token(token)
            user_id = int(payload['sub'])
            user = self.get_user_by_id(user_id)

            if not user or not user.is_active:
                raise APIError(
                    message="User not found or inactive",
                    code="AUTH_USER_INVALID",
                    status_code=401
                )

            return user

        except jwt.ExpiredSignatureError:
            raise APIError(
                message="Token has expired",
                code="AUTH_TOKEN_EXPIRED",
                status_code=401
            )
        except jwt.InvalidTokenError:
            raise APIError(
                message="Invalid token",
                code="AUTH_INVALID_TOKEN",
                status_code=401
            )

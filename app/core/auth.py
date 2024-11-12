from datetime import datetime, timedelta
from typing import Optional, List
from functools import wraps

import jwt
from flask import request, g, current_app
from werkzeug.security import generate_password_hash, check_password_hash

from app.core.exceptions import APIError
from app.models.responses.auth import TokenResponse
from app.core.config import settings


class Auth:
    @staticmethod
    def generate_password_hash(password: str) -> str:
        """Generate password hash using werkzeug security"""
        return generate_password_hash(password)

    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """Verify password against hash"""
        return check_password_hash(hashed_password, plain_password)

    @staticmethod
    def create_token(user_id: int, expires_delta: Optional[timedelta] = None) -> str:
        """Create JWT token for user"""
        if expires_delta is None:
            expires_delta = timedelta(
                minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

        expire = datetime.utcnow() + expires_delta
        to_encode = {
            'exp': expire,
            'sub': str(user_id),
            'iat': datetime.utcnow()
        }

        encoded_jwt = jwt.encode(
            to_encode,
            settings.JWT_SECRET_KEY,
            algorithm='HS256'
        )
        return encoded_jwt

    @staticmethod
    def decode_token(token: str) -> dict:
        """Decode and validate JWT token"""
        try:
            payload = jwt.decode(
                token,
                settings.JWT_SECRET_KEY,
                algorithms=['HS256']
            )
            return payload
        except jwt.ExpiredSignatureError:
            raise APIError(
                message="Token has expired",
                code="AUTH_TOKEN_EXPIRED",
                status=401
            )
        except jwt.InvalidTokenError:
            raise APIError(
                message="Invalid token",
                code="AUTH_TOKEN_INVALID",
                status=401
            )

    @staticmethod
    def create_refresh_token(user_id: int) -> str:
        """Create refresh token for user"""
        expires_delta = timedelta(days=30)  # Refresh tokens last 30 days
        expire = datetime.utcnow() + expires_delta

        to_encode = {
            'exp': expire,
            'sub': str(user_id),
            'iat': datetime.utcnow(),
            'type': 'refresh'  # Mark as refresh token
        }

        encoded_jwt = jwt.encode(
            to_encode,
            settings.JWT_SECRET_KEY,
            algorithm='HS256'
        )
        return encoded_jwt

    @staticmethod
    def create_tokens(user_id: int) -> TokenResponse:
        """Create both access and refresh tokens"""
        access_token = Auth.create_token(user_id)
        refresh_token = Auth.create_refresh_token(user_id)

        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
        )


def require_auth(f):
    """Decorator to require authentication"""
    @wraps(f)
    def decorated(*args, **kwargs):
        auth_header = request.headers.get('Authorization')
        if not auth_header:
            raise APIError(
                message="Missing authorization header",
                code="AUTH_MISSING_TOKEN",
                status_code=401
            )

        try:
            token_type, token = auth_header.split()
            if token_type.lower() != 'bearer':
                raise APIError(
                    message="Invalid token type",
                    code="AUTH_INVALID_TOKEN_TYPE",
                    status_code=401
                )

            payload = Auth.decode_token(token)
            g.user_id = int(payload['sub'])
            return f(*args, **kwargs)

        except ValueError:
            raise APIError(
                message="Invalid authorization header format",
                code="AUTH_INVALID_HEADER",
                status_code=401
            )

    return decorated


def require_roles(roles: List[str]):
    """Decorator to require specific roles"""
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            if not hasattr(g, 'user_id'):
                raise APIError(
                    message="Authentication required",
                    code="AUTH_REQUIRED",
                    status=401
                )

            # Get user from database
            from app.services.auth import AuthService
            from app.core.db import get_db

            db = next(get_db())
            auth_service = AuthService(db)
            user = auth_service.get_user_by_id(g.user_id)

            if not user:
                raise APIError(
                    message="User not found",
                    code="AUTH_USER_NOT_FOUND",
                    status=401
                )

            if not user.is_active:
                raise APIError(
                    message="User account is disabled",
                    code="AUTH_ACCOUNT_DISABLED",
                    status=401
                )

            if user.role.value not in roles:
                raise APIError(
                    message="Insufficient permissions",
                    code="AUTH_INSUFFICIENT_PERMISSIONS",
                    status=403
                )

            return f(*args, **kwargs)
        return decorated
    return decorator

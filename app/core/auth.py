from datetime import datetime, timedelta
from typing import Optional, List
from functools import wraps

import jwt
from flask import request, g, current_app
from werkzeug.security import generate_password_hash, check_password_hash

from app.core.exceptions import APIError


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
                minutes=current_app.config['ACCESS_TOKEN_EXPIRE_MINUTES'])

        expire = datetime.utcnow() + expires_delta
        to_encode = {
            'exp': expire,
            'sub': str(user_id),
            'iat': datetime.utcnow()
        }

        encoded_jwt = jwt.encode(
            to_encode,
            current_app.config['JWT_SECRET_KEY'],
            algorithm='HS256'
        )
        return encoded_jwt

    @staticmethod
    def decode_token(token: str) -> dict:
        """Decode and validate JWT token"""
        try:
            payload = jwt.decode(
                token,
                current_app.config['JWT_SECRET_KEY'],
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


def require_auth(f):
    """Decorator to require authentication"""
    @wraps(f)
    def decorated(*args, **kwargs):
        auth_header = request.headers.get('Authorization')
        if not auth_header:
            raise APIError(
                message="Missing authorization header",
                code="AUTH_MISSING_TOKEN",
                status=401
            )

        try:
            token_type, token = auth_header.split()
            if token_type.lower() != 'bearer':
                raise APIError(
                    message="Invalid token type",
                    code="AUTH_INVALID_TOKEN_TYPE",
                    status=401
                )

            payload = Auth.decode_token(token)
            g.user_id = int(payload['sub'])
            return f(*args, **kwargs)

        except ValueError:
            raise APIError(
                message="Invalid authorization header format",
                code="AUTH_INVALID_HEADER",
                status=401
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

            # Note: User roles should be fetched from database
            # This is a placeholder for the actual implementation
            user_roles = ['user']  # Replace with DB lookup

            if not any(role in roles for role in user_roles):
                raise APIError(
                    message="Insufficient permissions",
                    code="AUTH_INSUFFICIENT_PERMISSIONS",
                    status=403
                )

            return f(*args, **kwargs)
        return decorated
    return decorator

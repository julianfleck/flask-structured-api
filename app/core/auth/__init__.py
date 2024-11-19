from datetime import datetime, timedelta
from typing import Union, List, TYPE_CHECKING
from functools import wraps
import jwt
import logging
from flask import request, g
from werkzeug.security import generate_password_hash, check_password_hash

from app.core.exceptions import APIError
from app.models.responses.auth import TokenResponse
from app.core.config import settings
from app.models.enums import UserRole
from app.core.db import get_session
from app.services.auth import AuthService, Auth

logger = logging.getLogger(__name__)

if TYPE_CHECKING:
    from app.models.user import User  # Import User model for type checking only


def has_required_roles(user: 'User', required_roles: Union[List[str], str]) -> bool:
    """Check if user has any of the required roles"""
    if not required_roles:
        return True

    if isinstance(required_roles, str):
        required_roles = [required_roles]

    user_role = UserRole(user.role)  # Convert string to enum
    return any(user_role == UserRole(role) for role in required_roles)


def require_roles(*roles: UserRole):
    """Decorator to require specific roles"""
    def decorator(f):
        # Store required roles on the function
        f._roles = [role.value for role in roles]  # Store string values

        @wraps(f)
        def decorated(*args, **kwargs):
            if not hasattr(g, 'user') or not has_required_roles(g.user, f._roles):
                raise APIError(
                    message="Insufficient permissions",
                    code="AUTH_INSUFFICIENT_PERMISSIONS",
                    status_code=403
                )
            return f(*args, **kwargs)
        return decorated
    return decorator


def require_auth(f):
    """Decorator to require authentication"""
    @wraps(f)
    def decorated(*args, **kwargs):
        # Check Authorization header first
        auth_header = request.headers.get('Authorization')
        if auth_header:
            try:
                token_type, token = auth_header.split(' ', 1)
                token_type = token_type.lower()

                db = next(get_session())
                auth_service = AuthService(db)

                if token_type == 'bearer':
                    user = auth_service.validate_token(token)
                elif token_type == 'apikey':
                    user = auth_service.validate_api_key(token)
                    g.api_key = token
                else:
                    raise APIError(
                        message="Invalid token type",
                        code="AUTH_INVALID_TOKEN_TYPE",
                        status_code=401
                    )

                g.user = user
                g.user_id = user.id
                return f(*args, **kwargs)

            except ValueError as e:
                if "split" in str(e):
                    logger.error(f"Header parsing error: {str(e)}")
                    raise APIError(
                        message="Invalid authorization header format",
                        code="AUTH_INVALID_HEADER",
                        status_code=401
                    )
                raise

        # Fallback to X-API-Key header
        api_key = request.headers.get('X-API-Key')
        if api_key:
            db = next(get_session())
            auth_service = AuthService(db)
            user = auth_service.validate_api_key(api_key)
            g.user = user
            g.user_id = user.id
            g.api_key = api_key
            return f(*args, **kwargs)

        raise APIError(
            message="Missing authorization header",
            code="AUTH_MISSING_TOKEN",
            status_code=401
        )

    return decorated


def optional_auth(f):
    """Decorator that attempts to authenticate but doesn't require it"""
    @wraps(f)
    def decorated(*args, **kwargs):
        auth_header = request.headers.get('Authorization')
        if not auth_header:
            return f(*args, **kwargs)

        try:
            token_type, token = auth_header.split()
            token_type = token_type.lower()

            db = next(get_session())
            auth_service = AuthService(db)

            if token_type == 'bearer':
                user = auth_service.validate_token(token)
            elif token_type == 'apikey':
                user = auth_service.validate_api_key(token)
            else:
                return f(*args, **kwargs)

            g.user = user
            g.user_id = user.id
            g.api_key = token if token_type == 'apikey' else None

        except (ValueError, jwt.PyJWTError):
            pass  # Silently fail on auth errors

        return f(*args, **kwargs)
    return decorated

import logging
from datetime import datetime, timedelta
from functools import wraps
from typing import TYPE_CHECKING, List, Union

import jwt
import inspect
from flask import g, request, current_app, jsonify
from werkzeug.security import check_password_hash, generate_password_hash

from flask_structured_api.core.config import settings
from flask_structured_api.core.db import get_session
from flask_structured_api.core.enums import UserRole, ErrorCode
from flask_structured_api.core.exceptions import APIError
from flask_structured_api.core.models.responses import TokenResponse, ErrorResponse
from flask_structured_api.core.models.errors import ErrorDetail
from flask_structured_api.core.services.auth import Auth, AuthService

logger = logging.getLogger(__name__)

if TYPE_CHECKING:
    # Import User model for type checking only
    from flask_structured_api.core.models.domain import User


def has_required_roles(user: "User", required_roles: Union[List[str], str]) -> bool:
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
            if not hasattr(g, "user") or not has_required_roles(g.user, f._roles):
                response = jsonify(ErrorResponse(
                    message="Insufficient permissions",
                    error=ErrorDetail(
                        code=ErrorCode.AUTH_INSUFFICIENT_PERMISSIONS,
                        details={"required_roles": f._roles}
                    )
                ).model_dump())
                response.status_code = 403
                return response
            return f(*args, **kwargs)

        return decorated

    return decorator


def require_auth(f):
    """Decorator to require authentication"""

    @wraps(f)
    def decorated(*args, **kwargs):
        try:
            # Check Authorization header first
            auth_header = request.headers.get("Authorization")
            if auth_header:
                try:
                    token_type, token = auth_header.split(" ", 1)
                    token_type = token_type.lower()

                    db = next(get_session())
                    auth_service = AuthService(db)

                    if token_type == "bearer":
                        user = auth_service.validate_token(token)
                    elif token_type == "apikey":
                        user = auth_service.validate_api_key(token)
                        g.api_key = token
                    else:
                        return jsonify(ErrorResponse(
                            message="Invalid token type",
                            error=ErrorDetail(
                                code=ErrorCode.AUTH_INVALID_TOKEN_TYPE,
                                details={"token_type": token_type}
                            )
                        ).model_dump()), 401

                    g.user = user
                    g.user_id = user.id
                    return f(*args, **kwargs)

                except ValueError as e:
                    if "split" in str(e):
                        logger.error("Header parsing error: {}".format(str(e)))
                        return jsonify(ErrorResponse(
                            message="Invalid authorization header format",
                            error=ErrorDetail(
                                code=ErrorCode.AUTH_INVALID_HEADER,
                                details={"error": str(e)}
                            )
                        ).model_dump()), 401
                    raise

            # Fallback to X-API-Key header
            api_key = request.headers.get("X-API-Key")
            if api_key:
                db = next(get_session())
                auth_service = AuthService(db)
                user = auth_service.validate_api_key(api_key)
                g.user = user
                g.user_id = user.id
                g.api_key = api_key
                return f(*args, **kwargs)

            return jsonify(ErrorResponse(
                message="Missing authorization header",
                error=ErrorDetail(
                    code=ErrorCode.AUTH_MISSING_TOKEN,
                    details={"required_headers": ["Authorization", "X-API-Key"]}
                )
            ).model_dump()), 401

        except Exception as e:
            logger.error("Authentication error: {}".format(str(e)), exc_info=True)
            return jsonify(ErrorResponse(
                message=str(e),
                error=ErrorDetail(
                    code=ErrorCode.AUTH_ERROR,
                    details={"error": str(e)}
                )
            ).model_dump()), 401

    return decorated


def optional_auth(f):
    """Decorator that attempts to authenticate but doesn't require it"""

    @wraps(f)
    def decorated(*args, **kwargs):
        auth_header = request.headers.get("Authorization")
        api_key_header = request.headers.get("X-API-Key")

        if not auth_header and not api_key_header:
            return f(*args, **kwargs)

        try:
            if auth_header:
                token_type, token = auth_header.split()
                token_type = token_type.lower()

                db = next(get_session())
                auth_service = AuthService(db)

                if token_type == "bearer":
                    user = auth_service.validate_token(token)
                    g.user = user
                    g.user_id = user.id
                elif token_type == "apikey":
                    user = auth_service.validate_api_key(token)
                    g.user = user
                    g.user_id = user.id
                    g.api_key = token
                else:
                    return f(*args, **kwargs)
            elif api_key_header:
                db = next(get_session())
                auth_service = AuthService(db)
                user = auth_service.validate_api_key(api_key_header)
                g.user = user
                g.user_id = user.id
                g.api_key = api_key_header

        except Exception as e:
            if hasattr(g, 'user'):
                delattr(g, 'user')
            if hasattr(g, 'user_id'):
                delattr(g, 'user_id')
            if hasattr(g, 'api_key'):
                delattr(g, 'api_key')

        return f(*args, **kwargs)

    return decorated

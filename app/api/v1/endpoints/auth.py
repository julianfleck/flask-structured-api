from flask import Blueprint, request, g
from app.core.responses import SuccessResponse
from app.services.auth import AuthService
from app.models.requests.auth import RegisterRequest, LoginRequest
from app.models.responses.auth import TokenResponse, UserResponse
from app.core.db import get_session
from app.core.auth import require_auth
from app.core.exceptions import APIError

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/register', methods=['POST'])
def register():
    """Register a new user"""
    data = request.get_json()
    register_data = RegisterRequest(**data)

    db = next(get_session())
    auth_service = AuthService(db)

    user = auth_service.register_user(register_data)

    return SuccessResponse(
        message="User registered successfully",
        data=user.dict()
    ).dict(), 201


@auth_bp.route('/login', methods=['POST'])
def login():
    """Login user and return access token"""
    data = request.get_json()
    login_data = LoginRequest(**data)

    db = next(get_session())
    auth_service = AuthService(db)

    token = auth_service.login(login_data)

    return SuccessResponse(
        message="Login successful",
        data=token.dict()
    ).dict()


@auth_bp.route('/me', methods=['GET'])
@require_auth
def get_current_user():
    """Get current user information"""
    db = next(get_session())
    auth_service = AuthService(db)

    user = auth_service.get_user_by_id(g.user_id)
    if not user:
        raise APIError(
            message="User not found",
            code="AUTH_USER_NOT_FOUND",
            status_code=404
        )

    return SuccessResponse(
        message="Current user retrieved successfully",
        data=UserResponse.from_orm(user).dict()
    ).dict()

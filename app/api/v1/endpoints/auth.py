from flask import Blueprint, request
from app.core.responses import SuccessResponse
from app.services.auth import AuthService
from app.models.requests.auth import RegisterRequest
from app.core.db import get_session

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

from flask import Blueprint
from app.models.responses import SuccessResponse
from app.core.config import settings

health_bp = Blueprint('health', __name__)


@health_bp.route('/health', methods=['GET'])
def health_check():
    """Basic health check endpoint"""
    return SuccessResponse(
        message=f"{settings.API_NAME} is healthy",
        data={
            "status": "healthy",
            "name": settings.API_NAME,
            "version": settings.API_VERSION
        }
    ).dict()

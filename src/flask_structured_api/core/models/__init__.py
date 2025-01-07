from sqlmodel import SQLModel

from flask_structured_api.core.enums import (
    StorageType,
    UserRole,
    WarningCode,
    WarningSeverity,
)

from .domain.api_key import APIKey
from .domain.base import CoreModel
from .domain.storage import APIStorage, StorageBase

# Domain models
from .domain.user import User
from .errors import (
    AuthErrorDetail,
    DatabaseErrorDetail,
    ErrorDetail,
    HTTPErrorDetail,
    ValidationErrorDetail,
    ValidationErrorItem,
)

# Request models
from .requests.auth import (
    APIKeyRequest,
    LoginRequest,
    RefreshTokenRequest,
    RegisterRequest,
)
from .requests.base import BaseRequestModel
from .requests.storage import SessionQueryRequest, StorageQueryRequest

# Response models
from .responses import (
    AICompletionResponse,
    DetailedSessionListResponse,
    ErrorResponse,
    ItemListResponse,
    ItemResponse,
    SessionListItemResponse,
    SessionWithEntriesResponse,
    SimpleSessionListResponse,
    StorageEntryResponse,
    StorageListResponse,
    SuccessResponse,
    TokenResponse,
    UserResponse,
)
from .responses.base_model import BaseAIValidationModel, BaseResponseModel

__all__ = [
    # SQLAlchemy models
    "SQLModel",
    # Base models
    "CoreModel",
    "BaseRequestModel",
    "BaseResponseModel",
    "BaseAIValidationModel",
    # Enums
    "UserRole",
    "WarningCode",
    "WarningSeverity",
    "StorageType",
    # Error models
    "ErrorDetail",
    "ValidationErrorItem",
    "ValidationErrorDetail",
    "HTTPErrorDetail",
    "DatabaseErrorDetail",
    "AuthErrorDetail",
    # Domain models
    "User",
    "StorageBase",
    "APIStorage",
    "APIKey",
    # Request models
    "LoginRequest",
    "RegisterRequest",
    "RefreshTokenRequest",
    "APIKeyRequest",
    "StorageQueryRequest",
    "SessionQueryRequest",
    # Response models
    "ErrorResponse",
    "SuccessResponse",
    "StorageEntryResponse",
    "StorageListResponse",
    "SimpleSessionListResponse",
    "DetailedSessionListResponse",
    "SessionListItemResponse",
    "SessionWithEntriesResponse",
    "TokenResponse",
    "UserResponse",
    "ItemResponse",
    "ItemListResponse",
    "AICompletionResponse",
]

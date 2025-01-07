from enum import Enum


class UserRole(str, Enum):
    ADMIN = "admin"
    USER = "user"
    READONLY = "readonly"


class WarningCode(str, Enum):
    VALIDATION_WARNING = "validation_warning"
    RATE_LIMIT_WARNING = "rate_limit_warning"
    PERFORMANCE_WARNING = "performance_warning"
    UNEXPECTED_PARAM = "unexpected_param"
    NO_RESULTS_FOUND = "no_results_found"
    DEPRECATED_USAGE = "deprecated_usage"
    PARAMETER_PRECEDENCE = "parameter_precedence"
    ENDPOINT_NORMALIZED = "endpoint_normalized"
    FILE_TYPE_MISMATCH = "file_type_mismatch"

    # File related warnings
    FILE_NOT_FOUND = "file_not_found"
    FILE_EXPIRED = "file_expired"
    FILE_TOO_LARGE = "file_too_large"

    # Content related warnings
    CONTENT_TOO_SHORT = "content_too_short"
    CONTENT_TRUNCATED = "content_truncated"
    CONTENT_EXTRACTION_FAILED = "content_extraction_failed"

    # Processing related warnings
    PROCESSING_ERROR = "processing_error"
    TOKEN_LIMIT_EXCEEDED = "token_limit_exceeded"
    SUMMARIZATION_REQUIRED = "summarization_required"
    RETRY_EXHAUSTED = "retry_exhausted"
    MISSING_ENVELOPE = "missing_envelope"
    NESTED_DATA = "nested_data"

    # AI related warnings
    AI_PROVIDER_ERROR = "ai_provider_error"
    AI_RESPONSE_VALIDATION_FAILED = "ai_response_validation_failed"
    AI_COST_EXCEEDED = "ai_cost_exceeded"
    HIGH_TOKEN_USAGE = "high_token_usage"
    PROMPT_PROCESSING_ERROR = "prompt_processing_error"
    ESTIMATED_CONFIDENCE = "estimated_confidence"
    LOW_CONFIDENCE = "low_confidence"
    MISSING_CONFIDENCE = "missing_confidence"
    MISSING_FIELD = "missing_field"

    # Validation related warnings
    FIELD_TOO_LONG = "field_too_long"
    FIELD_TRUNCATED = "field_truncated"
    FIELD_VALIDATION_ERROR = "field_validation_error"


class WarningSeverity(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class StorageType(str, Enum):
    REQUEST = "REQUEST"
    RESPONSE = "RESPONSE"
    BOTH = "BOTH"
    DATA = "DATA"


class AIErrorCode(str, Enum):
    INVALID_RESPONSE = "AI_INVALID_RESPONSE"
    LENGTH_LIMIT_EXCEEDED = "AI_LENGTH_LIMIT_EXCEEDED"
    PROVIDER_ERROR = "AI_PROVIDER_ERROR"
    LOW_CONFIDENCE = "AI_LOW_CONFIDENCE"
    PARSING_ERROR = "AI_PARSING_ERROR"
    VALIDATION_ERROR = "AI_VALIDATION_ERROR"
    EMPTY_RESPONSE = "AI_EMPTY_RESPONSE"


class ErrorCode(str, Enum):
    # Auth related errors
    AUTH_MISSING_TOKEN = "AUTH_MISSING_TOKEN"
    AUTH_INVALID_TOKEN = "AUTH_INVALID_TOKEN"
    AUTH_EXPIRED_TOKEN = "AUTH_EXPIRED_TOKEN"
    AUTH_INVALID_HEADER = "AUTH_INVALID_HEADER"
    AUTH_INSUFFICIENT_PERMISSIONS = "AUTH_INSUFFICIENT_PERMISSIONS"
    AUTH_INVALID_TOKEN_TYPE = "AUTH_INVALID_TOKEN_TYPE"
    AUTH_ERROR = "AUTH_ERROR"

    # File related errors
    FILE_UPLOAD_ERROR = "FILE_UPLOAD_ERROR"
    FILE_NOT_FOUND = "FILE_NOT_FOUND"
    FILE_TOO_LARGE = "FILE_TOO_LARGE"

    # Processing related errors
    STIP_PROCESSING_ERROR = "STIP_PROCESSING_ERROR"
    INTERNAL_SERVER_ERROR = "INTERNAL_SERVER_ERROR"

    # Validation related errors
    VALIDATION_ERROR = "VALIDATION_ERROR"
    INVALID_COUNTRY_CODE = "INVALID_COUNTRY_CODE"

    # Storage related errors
    STORAGE_ERROR = "STORAGE_ERROR"
    DATA_NOT_FOUND = "DATA_NOT_FOUND"
    RETRIEVE_ERROR = "RETRIEVE_ERROR"
    DELETE_ERROR = "DELETE_ERROR"
    LIST_ERROR = "LIST_ERROR"

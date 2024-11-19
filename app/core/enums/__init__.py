from enum import Enum


class UserRole(str, Enum):
    ADMIN = "admin"
    USER = "user"
    READONLY = "readonly"


class WarningCode(str, Enum):
    LOW_CONFIDENCE = "low_confidence"
    HIGH_TOKEN_USAGE = "high_token_usage"
    VALIDATION_WARNING = "validation_warning"
    RATE_LIMIT_WARNING = "rate_limit_warning"
    PERFORMANCE_WARNING = "performance_warning"
    UNEXPECTED_PARAM = "unexpected_param"
    NO_RESULTS_FOUND = "no_results_found"
    DEPRECATED_USAGE = "deprecated_usage"
    PARAMETER_PRECEDENCE = "parameter_precedence"
    ENDPOINT_NORMALIZED = "endpoint_normalized"


class WarningSeverity(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class StorageType(str, Enum):
    REQUEST = "request"
    RESPONSE = "response"
    BOTH = "both"

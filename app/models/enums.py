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


class WarningSeverity(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"

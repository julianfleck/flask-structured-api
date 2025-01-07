from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field
from .base import ErrorDetail


class AILengthLimitErrorDetail(ErrorDetail):
    """Error details for length limit exceeded errors"""
    code: str = "LENGTH_LIMIT_EXCEEDED"
    completion_tokens: int
    prompt_tokens: int
    total_tokens: int
    max_tokens: int
    provider: Optional[str] = None


class AIErrorDetail(ErrorDetail):
    """Detailed error information for AI operations"""
    message: str
    code: str
    details: Optional[Dict[str, Any]] = None
    provider: Optional[str] = None


class AIResponseValidationError(ErrorDetail):
    """Validation error details for AI responses"""
    code: str = "AI_INVALID_RESPONSE"
    validation_errors: List[Dict[str, Any]]
    raw_response: Optional[Dict[str, Any]] = None
    provider: Optional[str] = None
    confidence: Optional[float] = None

# app/core/ai/base.py
from typing import Protocol, Type, TypeVar, Optional, Dict, Any, List
from datetime import datetime
from pydantic import BaseModel, Field
from app.models.core.ai import AICompletionRequest

T = TypeVar('T', bound=BaseModel)


class AIResponse(BaseModel):
    """Standardized AI response format"""
    content: str
    usage: Dict[str, int]
    model: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    warnings: List[str] = Field(default_factory=list)


class AIProvider(Protocol):
    """Protocol for AI service providers"""

    async def complete(
        self,
        request: AICompletionRequest,
        response_model: Optional[Type[T]] = None,
        max_retries: int = 3,
        initial_delay: float = 1.0
    ) -> T:
        """Generate completion with retry mechanism"""
        ...

    async def validate_response(
        self,
        response: str,
        schema: dict
    ) -> bool:
        """Validate response against schema"""
        ...

    def log_request(
        self,
        request: AICompletionRequest,
        context: Dict[str, Any] = None
    ) -> None:
        """Log request details for future logging implementation"""
        ...

    def log_response(
        self,
        response: AIResponse,
        duration_ms: int,
        context: Dict[str, Any] = None
    ) -> None:
        """Log response details for future logging implementation"""
        ...

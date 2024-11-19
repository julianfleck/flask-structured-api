# app/core/ai/base.py
from typing import Protocol, Type, TypeVar, Optional, Dict, Any, List
from datetime import datetime
from pydantic import BaseModel, Field
from app.core.ai.models import AICompletionRequest
from app.core.models.responses.ai import AIResponse

T = TypeVar('T', bound=BaseModel)


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

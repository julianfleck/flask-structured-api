from typing import Dict, Any, Optional
from app.core.models.responses.base_model import BaseResponseModel


class AIResponse(BaseResponseModel):
    """Response model for AI-related endpoints"""
    model: str
    response: str
    tokens_used: int
    metadata: Optional[Dict[str, Any]] = None
    raw_response: Optional[Dict[str, Any]] = None

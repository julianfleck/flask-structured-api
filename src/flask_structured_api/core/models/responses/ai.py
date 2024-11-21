from typing import Dict, Any, Optional
from flask_structured_api.core.models.responses.base_model import BaseResponseModel


class AIResponse(BaseResponseModel):
    """Response model for AI-related endpoints"""
    model: str
    response: str
    tokens_used: int
    ai_metadata: dict
    raw_response: Optional[Dict[str, Any]] = None

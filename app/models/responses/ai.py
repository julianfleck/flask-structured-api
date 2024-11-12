from typing import Dict, Any, List
from datetime import datetime
from pydantic import BaseModel, Field


class AIResponse(BaseModel):
    """Standardized AI response format"""
    content: str
    usage: Dict[str, int]
    model: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    warnings: List[str] = Field(default_factory=list)

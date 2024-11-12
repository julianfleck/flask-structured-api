# app/models/core/ai.py
from typing import List, Optional, Any
from pydantic import BaseModel, Field


class AIMessage(BaseModel):
    """Standard AI message format"""
    role: str = Field(..., regex="^(system|user|assistant)$")
    content: str = Field(..., min_length=1)


class AICompletionRequest(BaseModel):
    """Standard completion request"""
    messages: List[AIMessage]
    temperature: float = Field(default=0.7, ge=0, le=2.0)
    max_tokens: Optional[int] = None
    response_schema: Optional[dict] = None


class AICompletionResponse(BaseModel):
    """Standard completion response"""
    content: str
    role: str = "assistant"
    finish_reason: str
    usage: dict
    warnings: List[str] = []

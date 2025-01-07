from typing import List, Optional, Dict, Any, Union
from pydantic import BaseModel, Field


class AIMessage(BaseModel):
    """Message format for AI requests"""
    role: str = Field(..., pattern="^(system|user|assistant)$")
    content: str = Field(..., min_length=1)


class AICompletionRequest(BaseModel):
    """Request model for AI completions"""
    messages: List[AIMessage]
    response_schema: Optional[Union[Dict[str, Any], BaseModel]] = None
    temperature: float = Field(default=0.7, ge=0, le=2.0)
    max_tokens: Optional[int] = None

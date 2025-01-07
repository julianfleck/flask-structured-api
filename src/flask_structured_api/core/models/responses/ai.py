from typing import Any, List, Dict, Optional
from pydantic import BaseModel, Field


class AICompletionResponse(BaseModel):
    """Response model for AI completions"""
    content: Dict[str, Any] = Field(..., description="Response content with envelope")
    success: bool = Field(default=True)
    confidence: float = Field(default=1.0)
    role: str = "assistant"
    finish_reason: str = "stop"
    usage: Dict[str, int] = Field(default_factory=dict)
    warnings: List[str] = Field(default_factory=list)
    duration: float = Field(default=0.0, description="Request duration in seconds")
    schema_used: bool = Field(
        default=None, description="Whether a schema was used for validation")
    response_schema: Optional[Dict[str, Any]] = None

    def __init__(self, **data):
        super().__init__(**data)
        if self.schema_used is None:
            self.schema_used = self.response_schema is not None

    @property
    def metadata(self) -> Dict[str, Any]:
        """Structured metadata for the response"""
        return {
            "confidence": self.confidence,
            "performance": {
                "total_duration": self.duration,
                "tokens_per_second": (
                    self.usage.get("total_tokens", 0) / self.duration
                    if self.duration > 0 else 0
                )
            },
            "usage": self.usage,
            "schema": {
                "used": self.schema_used,
                "definition": self.response_schema
            }
        }

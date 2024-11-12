# app/models/ai/validation/base.py
from typing import Dict
from pydantic import Field, validator
from app.models.core.base import BaseAIValidationModel


class AIGenerationResponse(BaseAIValidationModel):
    """Example AI response validation model"""
    content: str = Field(..., min_length=10)
    metadata: Dict[str, Any] = Field(...)
    confidence: float = Field(..., ge=0, le=1)

    @validator('metadata')
    def validate_metadata(cls, v):
        """Ensure required metadata fields"""
        required_fields = ['category', 'quality_score']
        if not all(field in v for field in required_fields):
            raise ValueError(f"Missing required metadata fields: {
                             required_fields}")
        return v

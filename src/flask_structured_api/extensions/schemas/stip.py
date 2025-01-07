from datetime import datetime
from typing import Dict, List, Literal, Optional

from pydantic import BaseModel, Field, HttpUrl, constr
from flask_structured_api.extensions.prompts import (
    BudgetItem, EvaluationInfo, Objective, PolicyInstrument,
    StartDateInfo, TargetGroup, ThemeInfo
)


class InitiativeRequest(BaseModel):
    """Schema for initiative request validation."""

    initiative_name: constr(min_length=1, max_length=255)
    input_type: Literal["url", "text", "file"]
    content: str  # URL, text content, or file_token
    file_token: Optional[str] = None
    prompts: Optional[List[str]] = None


class ProcessInitiativesRequest(BaseModel):
    """Schema for processing multiple initiatives."""

    initiatives: List[InitiativeRequest]


class ProcessingResults(BaseModel):
    """Schema for structured processing results."""

    identification: int
    description: str
    objectives: List[Objective]
    start_date: StartDateInfo
    policy_instruments: List[PolicyInstrument]
    target_groups: TargetGroup
    themes: ThemeInfo
    budget: List[BudgetItem]
    evaluation: EvaluationInfo


class InitiativeResponse(BaseModel):
    """Schema for initiative processing response."""

    status: str
    results: ProcessingResults
    error: Optional[str] = None


class ProcessingResult(BaseModel):
    """Schema for final processing results."""

    status: str
    results: ProcessingResults
    cost_estimate: float


class PartialProcessingResults(BaseModel):
    """Schema for partial processing results when only specific prompts are requested."""
    identification: Optional[int] = None
    description: Optional[str] = None
    objectives: Optional[List[Objective]] = None
    start_date: Optional[StartDateInfo] = None
    policy_instruments: Optional[List[PolicyInstrument]] = None
    target_groups: Optional[TargetGroup] = None
    themes: Optional[ThemeInfo] = None
    budget: Optional[List[BudgetItem]] = None
    evaluation: Optional[EvaluationInfo] = None

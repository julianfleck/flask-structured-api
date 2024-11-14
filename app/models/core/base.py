from datetime import datetime, timezone
from typing import Optional, Dict, Any
from sqlmodel import SQLModel, Field
from pydantic import root_validator
from app.core.warnings import WarningCollector
from app.models.enums import WarningCode, WarningSeverity


class CoreModel(SQLModel):
    """Base model for all database models"""
    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(
        default_factory=datetime.utcnow,
        sa_column_kwargs={"onupdate": datetime.utcnow}
    )

# Base models for different concerns


class BaseRequestModel(SQLModel):
    """Base model for API requests"""

    @root_validator(pre=True)
    def parse_dates(cls, values: Dict[str, Any]) -> Dict[str, Any]:
        """Parse date fields and ensure timezone awareness"""
        for field_name, value in values.items():
            if isinstance(value, str) and ('date' in field_name.lower() or 'time' in field_name.lower()):
                try:
                    # Handle different date formats
                    if len(value) == 10:  # YYYY-MM-DD
                        value = f"{value}T00:00:00Z"
                    elif not value.endswith('Z'):
                        value = f"{value}Z"

                    # Parse and ensure UTC timezone
                    parsed_date = datetime.fromisoformat(
                        value.replace('Z', '+00:00'))

                    # Validate not in future
                    if parsed_date > datetime.now(timezone.utc):
                        raise ValueError(
                            f"{field_name} cannot be in the future")

                    values[field_name] = parsed_date
                except ValueError as e:
                    if "future" in str(e):
                        raise
                    raise ValueError(
                        f"Invalid date format for {field_name}. "
                        "Supported formats: YYYY-MM-DD, YYYY-MM-DDThh:mm:ss, YYYY-MM-DDThh:mm:ssZ"
                    )

        return values

    @root_validator(pre=True)
    def check_extra_fields(cls, values: Dict[str, Any]) -> Dict[str, Any]:
        """Collect extra fields as warnings instead of rejecting them"""
        model_fields = cls.__fields__.keys()
        extra_fields = [k for k in values.keys() if k not in model_fields]

        if extra_fields:
            warning_collector = WarningCollector()
            # Create a separate warning for each extra field
            for field in extra_fields:
                warning_collector.add_warning(
                    message="Unexpected field in request: {}".format(field),
                    code=WarningCode.UNEXPECTED_PARAM,
                    severity=WarningSeverity.LOW
                )
                values.pop(field)

        return values

    class Config:
        extra = "allow"  # Allow extra fields to reach our validator


class BaseResponseModel(SQLModel):
    """Base model for API responses"""
    class Config:
        from_attributes = True


class BaseAIValidationModel(SQLModel):
    """Base model for AI response validation"""
    class Config:
        extra = "forbid"
        strict = True  # Strict type checking for AI responses

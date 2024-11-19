from datetime import datetime, timezone
from typing import Optional, Dict, Any
from sqlmodel import SQLModel, Field
from pydantic import root_validator, ValidationError
from app.core.warnings import WarningCollector
from app.models.enums import WarningCode, WarningSeverity
from app.models.errors import ValidationErrorDetail, ValidationErrorItem
from app.core.exceptions.validation import ValidationError, ValidationErrorCode


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
    def validate_request(cls, values: Dict[str, Any]) -> Dict[str, Any]:
        """Validate request data and handle errors consistently"""
        for field_name, value in values.items():
            if isinstance(value, str) and ('date' in field_name.lower() or 'time' in field_name.lower()):
                try:
                    # Handle different date formats
                    if len(value) == 10:  # YYYY-MM-DD
                        value = "{}T00:00:00Z".format(value)
                    elif not value.endswith('Z'):
                        value = "{}Z".format(value)

                    # Parse and ensure UTC timezone
                    parsed_date = datetime.fromisoformat(
                        value.replace('Z', '+00:00'))

                    # Validate not in future
                    if parsed_date > datetime.now(timezone.utc):
                        raise ValidationError(
                            message=f"{field_name} cannot be in the future",
                            code=ValidationErrorCode.FUTURE_DATE,
                            field=field_name
                        )

                    values[field_name] = parsed_date
                except ValueError:
                    raise ValidationError(
                        message="Invalid date format. Expected: YYYY-MM-DD or YYYY-MM-DDThh:mm:ssZ",
                        code=ValidationErrorCode.INVALID_FORMAT,
                        field=field_name,
                        context={"allowed_formats": [
                            "YYYY-MM-DD", "YYYY-MM-DDThh:mm:ssZ"]}
                    )

        return values

    @root_validator(pre=True)
    def check_extra_fields(cls, values: Dict[str, Any]) -> Dict[str, Any]:
        """Collect extra fields as warnings instead of rejecting them"""
        model_fields = cls.__fields__.keys()
        # Get all field aliases
        field_aliases = {
            field.alias for field in cls.__fields__.values()
            if hasattr(field, 'alias') and field.alias
        }
        valid_names = set(model_fields) | field_aliases

        extra_fields = [k for k in values.keys() if k not in valid_names]

        if extra_fields:
            # Create a separate warning for each extra field
            for field in extra_fields:
                WarningCollector.add_warning(
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

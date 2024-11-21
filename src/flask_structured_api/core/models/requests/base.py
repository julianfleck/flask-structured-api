from datetime import datetime, timezone
from typing import Dict, Any
from sqlmodel import SQLModel
from pydantic import root_validator
from flask_structured_api.core.warnings import WarningCollector
from flask_structured_api.core.enums import WarningCode, WarningSeverity
from flask_structured_api.core.exceptions.validation import ValidationError, ValidationErrorCode


class BaseRequestModel(SQLModel):
    """Base model for API requests"""
    @root_validator(pre=True)
    def validate_request(cls, values: Dict[str, Any]) -> Dict[str, Any]:
        for field_name, value in values.items():
            if isinstance(value, str) and ('date' in field_name.lower() or 'time' in field_name.lower()):
                try:
                    if len(value) == 10:  # YYYY-MM-DD
                        value = "{}T00:00:00Z".format(value)
                    elif not value.endswith('Z'):
                        value = "{}Z".format(value)

                    parsed_date = datetime.fromisoformat(
                        value.replace('Z', '+00:00'))

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
        model_fields = cls.__fields__.keys()
        field_aliases = {
            field.alias for field in cls.__fields__.values()
            if hasattr(field, 'alias') and field.alias
        }
        valid_names = set(model_fields) | field_aliases

        extra_fields = [k for k in values.keys() if k not in valid_names]

        if extra_fields:
            for field in extra_fields:
                WarningCollector.add_warning(
                    message=f"Unexpected field in request: {field}",
                    code=WarningCode.UNEXPECTED_PARAM,
                    severity=WarningSeverity.LOW
                )
                values.pop(field)

        return values

    class Config:
        extra = "allow"

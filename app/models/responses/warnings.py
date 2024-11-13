from pydantic import BaseModel
from app.models.enums import WarningCode, WarningSeverity


class ResponseWarning(BaseModel):
    """Structured warning format for responses"""
    code: WarningCode
    message: str
    severity: WarningSeverity

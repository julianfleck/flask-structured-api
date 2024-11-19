from pydantic import BaseModel
from app.core.enums import WarningCode, WarningSeverity


class ResponseWarning(BaseModel):
    """Warning model for API responses"""
    code: WarningCode
    message: str
    severity: WarningSeverity = WarningSeverity.LOW

from pydantic import BaseModel

from flask_structured_api.core.enums import WarningCode, WarningSeverity


class ResponseWarning(BaseModel):
    """Warning model for API responses"""

    code: WarningCode
    message: str
    severity: WarningSeverity = WarningSeverity.LOW

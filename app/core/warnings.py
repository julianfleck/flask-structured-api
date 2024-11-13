# app/core/warnings.py
from dataclasses import dataclass, field
from typing import List
from datetime import datetime
from app.models.enums import WarningCode, WarningSeverity


@dataclass
class Warning:
    """Warning message structure"""
    message: str
    code: WarningCode
    timestamp: datetime = field(default_factory=datetime.utcnow)
    severity: WarningSeverity = WarningSeverity.MEDIUM


class WarningCollector:
    """Warning collection utility"""
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.warnings = []
        return cls._instance

    def add_warning(self, message: str, code: WarningCode, severity: WarningSeverity = WarningSeverity.MEDIUM):
        """Add new warning"""
        self.warnings.append(Warning(
            message=message,
            code=code,
            severity=severity
        ))

    def get_warnings(self) -> List[Warning]:
        """Get collected warnings"""
        return self.warnings

    def clear_warnings(self):
        """Clear all warnings"""
        self.warnings = []

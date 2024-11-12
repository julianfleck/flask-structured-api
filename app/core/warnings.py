# app/core/warnings.py
from dataclasses import dataclass, field
from typing import List, Dict, ClassVar
from datetime import datetime


@dataclass
class Warning:
    """Warning message structure"""
    message: str
    code: str
    timestamp: datetime = field(default_factory=datetime.utcnow)
    severity: str = "warning"

    # Standard warning codes
    CODES: ClassVar[Dict[str, str]] = {
        "low_confidence": "AI model confidence below threshold",
        "high_token_usage": "High token usage detected",
        "validation_warning": "Non-critical validation issue",
        "rate_limit_warning": "Approaching rate limit",
        "performance_warning": "Performance degradation detected"
    }


class WarningCollector:
    """Warning collection utility"""

    def __init__(self):
        self.warnings: List[Warning] = []

    def add_warning(self, message: str, code: str):
        """Add new warning"""
        self.warnings.append(Warning(message=message, code=code))

    def get_warnings(self) -> List[Warning]:
        """Get collected warnings"""
        return self.warnings

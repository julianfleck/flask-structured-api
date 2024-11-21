# app/core/warnings.py
from typing import List, Optional
from dataclasses import dataclass, field
from datetime import datetime

from flask_structured_api.core.enums import WarningCode, WarningSeverity


@dataclass
class Warning:
    """Warning message structure"""
    message: str
    code: WarningCode
    severity: WarningSeverity = WarningSeverity.MEDIUM
    timestamp: datetime = field(default_factory=datetime.utcnow)
    priority: int = 0  # Lower number = higher priority

    def __eq__(self, other):
        return self.code == other.code and self.message == other.message

    def __hash__(self):
        return hash((self.code, self.message))


class WarningCollector:
    """Warning collection utility"""
    _request_warnings = {}

    @classmethod
    def get_instance(cls):
        """Get request-scoped instance"""
        from flask import g
        request_id = g.request_id  # Use the existing request_id from Flask's g object
        if request_id not in cls._request_warnings:
            cls._request_warnings[request_id] = []
        return cls._request_warnings[request_id]

    @classmethod
    def add_warning(cls, message: str, code: WarningCode, severity: WarningSeverity = WarningSeverity.MEDIUM, priority: int = 0):
        """Add new warning"""
        warnings = cls.get_instance()
        warnings.append(Warning(
            message=message,
            code=code,
            severity=severity,
            priority=priority
        ))

    @classmethod
    def get_warnings(cls) -> List[Warning]:
        """Get collected warnings with deduplication and priority sorting"""
        warnings = cls.get_instance()

        # Group warnings by code
        warnings_by_code = {}
        for warning in warnings:
            if warning.code not in warnings_by_code:
                warnings_by_code[warning.code] = set()
            warnings_by_code[warning.code].add(warning)

        # Process warnings based on code
        final_warnings = []
        for code, code_warnings in warnings_by_code.items():
            if code == WarningCode.NO_RESULTS_FOUND:
                # For NO_RESULTS_FOUND, only keep the most specific warning
                highest_priority = min(w.priority for w in code_warnings)
                final_warnings.extend(
                    w for w in code_warnings if w.priority == highest_priority
                )
            else:
                # For other codes like UNEXPECTED_PARAM, keep all warnings
                final_warnings.extend(code_warnings)

        # Sort by priority (higher priority first) then timestamp
        return sorted(final_warnings, key=lambda w: (w.priority, w.timestamp))

    @classmethod
    def clear_warnings(cls):
        """Clear all warnings"""
        from flask import request
        request_id = request.environ.get('REQUEST_ID', 'default')
        cls._request_warnings[request_id] = []

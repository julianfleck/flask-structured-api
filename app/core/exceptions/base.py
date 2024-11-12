from typing import Dict, Any


class APIError(Exception):
    """Base API error"""

    def __init__(self, message: str, code: str = None, details: Dict[str, Any] = None, status_code: int = 400):
        self.message = message
        self.code = code or self.__class__.__name__
        self.details = details or {}
        self.status_code = status_code

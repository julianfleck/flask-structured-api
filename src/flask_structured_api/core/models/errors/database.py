from typing import Optional

from .base import ErrorDetail


class DatabaseErrorDetail(ErrorDetail):
    """Database error details"""

    operation: str
    table: Optional[str] = None
    constraint: Optional[str] = None

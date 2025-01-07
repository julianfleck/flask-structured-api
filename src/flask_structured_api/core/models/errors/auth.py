from typing import List, Optional

from .base import ErrorDetail


class AuthErrorDetail(ErrorDetail):
    """Authentication error details"""

    reason: str
    required_permissions: Optional[List[str]] = None

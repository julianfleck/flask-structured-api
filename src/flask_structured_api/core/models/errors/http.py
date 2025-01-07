from typing import Optional

from .base import ErrorDetail


class HTTPErrorDetail(ErrorDetail):
    """HTTP error details"""

    status: int
    method: Optional[str] = None
    path: Optional[str] = None

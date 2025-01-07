from typing import Any, Dict, Optional

from pydantic import BaseModel


class ErrorDetail(BaseModel):
    """Base error detail model"""

    code: str
    details: Optional[Dict[str, Any]] = None

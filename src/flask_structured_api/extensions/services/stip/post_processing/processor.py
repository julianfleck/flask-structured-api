from typing import Dict, Any, Optional, Union
from flask_structured_api.core.models.responses import SuccessResponse, ErrorResponse
from flask_structured_api.extensions.schemas.stip import ProcessingResults, PartialProcessingResults


class ResponseProcessor:
    """Handles post-processing of AI response data"""

    def process_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Process response data and return cleaned/formatted data"""
        # For now just pass through, but we can add data cleanup here later
        return data

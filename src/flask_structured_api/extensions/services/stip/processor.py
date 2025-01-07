from typing import Dict, Any, Optional, Union, List
from flask import request, current_app
from flask_structured_api.core.warnings import WarningCollector
from flask_structured_api.core.models.responses import ErrorResponse, SuccessResponse
from flask_structured_api.core.models.errors import ErrorDetail
from .extraction.scraping import extract_from_url
from .extraction.document import extract_from_file
from .extraction.cleaning import clean_text
from .ai_processing.processor import AIProcessor
from .post_processing.processor import ResponseProcessor


class STIPProcessor:
    def __init__(self, file_store=None, prompt_path: Optional[str] = None):
        self.file_store = file_store
        self.warning_collector = WarningCollector()
        self.ai_processor = AIProcessor(prompt_path)
        self.response_processor = ResponseProcessor()

    async def process_initiative(
        self,
        content: str,
        initiative_name: str,
        input_type: str = "url",
        prompts: Optional[Union[str, List[str]]] = None,
        file_token: Optional[str] = None,
        country_code: Optional[str] = None,
        one_shot: bool = False
    ) -> Dict[str, Any]:
        """Main orchestration method"""
        try:
            # Extract text based on input type
            text = self._extract_content(content, input_type, file_token, country_code)
            current_app.logger.debug("Text extracted successfully")

            # Clean the extracted text
            text = clean_text(text)
            current_app.logger.debug("Text cleaned successfully")

            # Process with AI based on one_shot flag
            if one_shot:
                ai_response = await self.ai_processor.process_one_shot(
                    prompt_types=prompts or [],
                    text=text,
                    initiative_name=initiative_name
                )
            else:
                ai_response = await self._process_with_ai(text, initiative_name, prompts)

            if isinstance(ai_response, ErrorResponse):
                return ai_response

            # Post-process only the data portion
            processed_data = self.response_processor.process_data(ai_response.data)

            # Create final response with processed data
            return SuccessResponse(
                data=processed_data,
                message=ai_response.message,
                metadata=ai_response.metadata,
                warnings=ai_response.warnings
            )

        except Exception as e:
            current_app.logger.error(
                "Error in process_initiative",
                extra={
                    "error": str(e),
                    "error_type": type(e).__name__,
                    "initiative_name": initiative_name,
                    "input_type": input_type,
                    "country_code": country_code,
                    "one_shot": one_shot
                },
                exc_info=True
            )
            self.warning_collector.add_warning(
                code="STIP_PROCESSING_ERROR",
                message=str(e),
                severity="HIGH"
            )
            return ErrorResponse(
                message="Failed to process initiative",
                error=ErrorDetail(
                    code="STIP_PROCESSING_ERROR",
                    details={
                        "error": str(e),
                        "error_type": type(e).__name__
                    }
                )
            )

    def _extract_content(self, content: str, input_type: str, file_token: Optional[str] = None, country_code: Optional[str] = None) -> str:
        """Extract content based on input type"""
        if input_type == "url":
            return extract_from_url(content)
        elif input_type == "file":
            token = file_token or content
            return self._handle_file_extraction(token, country_code)
        return content

    def _handle_file_extraction(self, file_token: str, country_code: Optional[str] = None) -> str:
        """Handle file extraction with proper error handling"""
        country = country_code or "default"
        try:
            file_type = self.file_store.get_file_type(file_token, country)
            content = self.file_store.get_file(file_token, country)
            return extract_from_file(content, file_type)
        except FileNotFoundError as e:
            self.warning_collector.add_warning(
                code="FILE_NOT_FOUND",
                message=str(e),
                severity="HIGH"
            )
            raise
        except ValueError as e:
            self.warning_collector.add_warning(
                code="FILE_PROCESSING_ERROR",
                message=str(e),
                severity="HIGH"
            )
            raise

    async def _process_with_ai(self, text: str, initiative_name: str, prompts: Optional[Union[str, List[str]]] = None) -> Union[ErrorResponse, SuccessResponse]:
        """Process text with AI and return the response"""
        current_app.logger.info("Processing AI request")
        current_app.logger.debug(
            "AI request details:",
            extra={
                "initiative_name": initiative_name,
                "prompts": prompts,
                "text_length": len(text)
            }
        )

        if prompts:
            if isinstance(prompts, str):
                current_app.logger.debug("Processing single prompt")
                ai_response = await self.ai_processor.process_prompt(
                    prompts, text, initiative_name)
            else:
                current_app.logger.debug("Processing selected prompts")
                ai_response = await self.ai_processor.process_selected_prompts(
                    prompts, text, initiative_name)
        else:
            current_app.logger.debug("Processing all prompts")
            ai_response = await self.ai_processor.process_all_prompts(text, initiative_name)

        current_app.logger.debug(
            "AI Response received",
            extra={
                "success": not isinstance(ai_response, ErrorResponse),
                "response_type": type(ai_response).__name__
            }
        )

        if isinstance(ai_response, ErrorResponse):
            return ai_response

        return SuccessResponse(
            data=ai_response.data,
            message=ai_response.message,
            metadata=ai_response.metadata,
            warnings=ai_response.warnings
        )

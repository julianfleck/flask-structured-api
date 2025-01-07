import json
import re
from typing import Optional, Dict, Any, Type, List, Union
from pydantic import BaseModel, ValidationError
from time import time

from flask import current_app
from flask_structured_api.core.utils.logger import get_standalone_logger

from flask_structured_api.core.ai.providers.base import BaseProvider
from flask_structured_api.core.models.requests.ai import AICompletionRequest, AIMessage
from flask_structured_api.core.models.responses.ai import AICompletionResponse
from flask_structured_api.core.models.errors.ai import AIErrorDetail
from flask_structured_api.core.exceptions.ai import AIServiceError, AIResponseValidationError
from flask_structured_api.core.enums import WarningCode, WarningSeverity, AIErrorCode
from flask_structured_api.core.config import settings

# Create standalone logger for AI service
logger = get_standalone_logger("ai.service")


class AIService:
    def __init__(self, provider: BaseProvider):
        self.provider = provider
        self._json_pattern = re.compile(r"```json\n(.*?)\n```", re.DOTALL)

    def _wrap_schema(self, schema: Dict[str, Any]) -> Dict[str, Any]:
        """Wrap schema in standard envelope"""
        return {
            "$schema": "http://json-schema.org/draft-07/schema#",
            "type": "object",
            "properties": {
                "success": {"type": "boolean", "description": "Whether the generation was successful"},
                "confidence": {"type": "number", "minimum": 0, "maximum": 1, "description": "Confidence score of the generation"},
                "data": schema
            },
            "required": ["success", "confidence", "data"],
            "additionalProperties": False
        }

    def _parse_content(self, content: Union[str, Dict]) -> Dict:
        """Parse and normalize AI response content"""
        try:
            # First parse if it's a string
            parsed = content if isinstance(content, dict) else json.loads(content)

            # Extract fields from our schema wrapper if present
            data = parsed.get("data")

            # If data contains nested data/success structure, extract the inner data
            if data and isinstance(data, dict) and all(k in data for k in ["data", "success"]):
                inner_data = data.get("data", {})
                confidence = data.get("confidence", 1.0)
                success = bool(inner_data)  # Success depends on having actual data

                return {
                    "success": success,
                    "confidence": confidence,
                    "data": inner_data
                }

            # Otherwise, wrap the original data
            confidence = parsed.get("confidence", 1.0)
            success = bool(data)  # Success depends on having data

            return {
                "success": success,
                "confidence": confidence,
                "data": data if data is not None else parsed
            }

        except (json.JSONDecodeError, TypeError) as e:
            raise AIServiceError(
                message="Failed to parse AI response: {}".format(str(e)),
                code=AIErrorCode.PARSING_ERROR,
                details={"content": content}
            )

    async def complete(self, request: AICompletionRequest, response_schema: Optional[Dict] = None) -> AICompletionResponse:
        """Handle simple text completion"""
        start_time = time()
        try:
            # Apply default settings if not specified
            if not request.temperature:
                request.temperature = settings.AI_TEMPERATURE
            if not request.max_tokens:
                request.max_tokens = settings.AI_MAX_TOKENS

            # Get raw LangChain response
            if response_schema:
                wrapped_schema = self._wrap_schema(response_schema)
                logger.debug("Using schema", extra={"schema": wrapped_schema})
                raw_response = await self.provider.complete(request, wrapped_schema)
            else:
                raw_response = await self.provider.complete(request)

            # Log raw response before processing
            logger.debug(
                "Raw AI response",
                extra={
                    "raw_response": raw_response.model_dump(),
                    "request_id": getattr(request, 'request_id', None),
                    "schema_used": bool(response_schema)
                }
            )

            # Extract and parse content
            content = self._parse_content(raw_response.content)
            logger.debug(
                "Normalized response content",
                extra={
                    "content": content,
                    "request_id": getattr(request, 'request_id', None)
                }
            )

            # Check confidence threshold
            confidence = content.get("confidence", 1.0)
            if confidence < 0.7:
                if current_app and hasattr(current_app, 'warning_collector'):
                    current_app.warning_collector.add_warning(
                        message="Response below confidence threshold (0.7)",
                        code=WarningCode.LOW_CONFIDENCE,
                        severity=WarningSeverity.MEDIUM,
                        details={"confidence": confidence}
                    )

            # Get warnings from collector
            warnings = []
            if current_app and hasattr(current_app, 'warning_collector'):
                warnings = current_app.warning_collector.get_warnings()

            duration = time() - start_time

            response = AICompletionResponse(
                content=content,
                role="assistant",
                finish_reason=raw_response.finish_reason,
                usage=raw_response.usage or {},
                warnings=[w.message for w in warnings] if warnings else [],
                duration=duration,
                metadata=raw_response.metadata,
                response_schema=response_schema
            )

            logger.debug("AICompletionResponse: {}".format(response))

            return response

        except KeyError as e:
            missing_field = str(e).strip("'")
            logger.error("Missing required field in response", extra={
                "field": missing_field,
                "content": content if 'content' in locals() else None,
                "request_id": getattr(request, 'request_id', None)
            })

            error_detail = {
                "field": missing_field,
                "raw_response": raw_response.model_dump() if 'raw_response' in locals() else None,
                "message": "Response is missing required field: {}".format(missing_field)
            }

            raise AIServiceError(
                message="Invalid AI response: missing required field '{}'".format(
                    missing_field),
                code=AIErrorCode.MISSING_FIELD,
                details=error_detail
            )
        except Exception as e:
            logger.error("Error in AI service", exc_info=True, extra={
                "error": str(e),
                "request": request.model_dump(),
                "schema": response_schema
            })
            raise AIServiceError(
                message="Failed to complete AI request: {}".format(str(e)),
                code=AIErrorCode.PROVIDER_ERROR,
                details={"error": str(e)}
            )

    async def complete_with_schema(
        self,
        request: AICompletionRequest,
        validation_model: Optional[Type[BaseModel]] = None
    ) -> AICompletionResponse:
        """Handle schema-based completion"""
        start_time = time()
        try:
            schema = (
                validation_model.model_json_schema()
                if validation_model
                else request.response_schema
            )

            wrapped_schema = self._wrap_schema(schema)
            response = await self.provider.complete(request, wrapped_schema)
            duration = time() - start_time

            try:
                content = self._parse_content(response.content)
            except (ValueError, KeyError) as e:
                logger.error("Failed to parse response: {}".format(str(e)))
                raise AIServiceError(
                    message="Invalid or empty response",
                    details={
                        "error": str(e),
                        "original_response": response.model_dump()
                    }
                )

            if validation_model:
                try:
                    validation_model(**content["data"])
                except ValidationError as e:
                    logger.error("Validation error: {}".format(str(e)))
                    raise AIResponseValidationError(
                        message="Response validation failed",
                        validation_errors=e.errors(),
                        raw_response=response.content,
                        confidence=content.get("confidence", 0)
                    )

            # Get warnings from collector
            warnings = []
            if current_app and hasattr(current_app, 'warning_collector'):
                warnings = current_app.warning_collector.get_warnings()

            return AICompletionResponse(
                content=content,
                finish_reason=response.finish_reason,
                usage=response.usage,
                warnings=[w.message for w in warnings] if warnings else [],
                duration=duration
            )

        except Exception as e:
            if isinstance(e, (AIResponseValidationError, AIServiceError)):
                raise e
            logger.error("Error in AI service", exc_info=True, extra={
                "error": str(e),
                "request": request.model_dump(),
                "schema": schema if 'schema' in locals() else None
            })
            raise AIServiceError(
                message="Failed to complete AI request: {}".format(str(e)),
                details={"error": str(e)}
            )

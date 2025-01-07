from abc import ABC, abstractmethod
from typing import Optional, Dict, Any, List, Type, TypeVar, Generic
from langchain.chat_models.base import BaseChatModel
from langchain.schema import BaseMessage, HumanMessage, SystemMessage, AIMessage, Generation
from langchain_core.output_parsers import JsonOutputParser
from langchain.output_parsers import OutputFixingParser
from pydantic import BaseModel, Field
from openai import LengthFinishReasonError
import json

from flask_structured_api.core import settings
from flask_structured_api.core.models.requests.ai import AICompletionRequest, AIMessage as APIMessage
from flask_structured_api.core.models.responses.ai import AICompletionResponse
from flask_structured_api.core.exceptions.ai import AIServiceError
from flask_structured_api.core.models.errors.ai import AILengthLimitErrorDetail
from flask_structured_api.core.utils.logger import get_standalone_logger

logger = get_standalone_logger("ai.provider")

T = TypeVar('T')  # For the data field type


class ResponseEnvelope(BaseModel, Generic[T]):
    """Standard response envelope"""
    data: T = Field(description="The main response content")
    success: bool = Field(description="Whether the generation was successful")
    message: str = Field(description="A descriptive message about the response")


class BaseProvider(ABC):
    def __init__(self, model: BaseChatModel):
        self.model = model
        self.default_max_tokens = getattr(settings, "AI_MAX_TOKENS", 3000)
        self.min_tokens = 5

        # Initialize parser with our envelope
        self.parser = OutputFixingParser.from_llm(
            parser=JsonOutputParser(pydantic_object=ResponseEnvelope[Dict[str, Any]]),
            llm=model
        )

    def get_max_tokens(self, requested_tokens: Optional[int] = None) -> int:
        """Get max tokens with safety margin for JSON responses"""
        max_tokens = requested_tokens or self.default_max_tokens
        return max(self.min_tokens, int(max_tokens * 1.2))

    def prepare_messages(self, messages: List[APIMessage], response_schema: Optional[Dict] = None) -> List[BaseMessage]:
        """Prepare messages with JSON instruction and schema if needed"""
        converted = self._convert_messages(messages)

        # Add format instructions from the parser
        format_instructions = self.parser.get_format_instructions()

        if response_schema:
            # Wrap user schema in our envelope
            wrapped_schema = {
                "type": "object",
                "properties": {
                    "data": response_schema,
                    "success": {"type": "boolean"},
                    "message": {"type": "string"}
                },
                "required": ["data", "success", "message"]
            }
            format_instructions += "\n\nThe data field must conform to:\n{}".format(
                json.dumps(wrapped_schema, indent=2))

        # Add instructions to system message or create new one
        return self._add_instruction(converted, format_instructions)

    def _unnest_data(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """Unnest multiply nested data fields"""
        result = content
        while isinstance(result.get("data"), dict):
            result = result["data"]
        return result

    def process_response(self, response, response_schema: Optional[Dict] = None) -> AICompletionResponse:
        """Process raw LangChain response into standardized format"""
        if not response.generations:
            raise AIServiceError("Empty response from model", code="EMPTY_RESPONSE")

        generation: Generation = response.generations[0][0]

        try:
            # Use the parser instead of manual JSON parsing
            parsed_content = self.parser.parse(generation.text)

            # If it's not already a ResponseEnvelope, wrap it
            if not isinstance(parsed_content, ResponseEnvelope):
                parsed_content = ResponseEnvelope(
                    data=parsed_content,
                    success=True,
                    message="Response generated successfully"
                )

            # Unnest multiply nested data fields
            content = self._unnest_data(parsed_content.model_dump())

            # Extract token usage
            token_usage = response.llm_output.get("token_usage", {})
            usage = {
                "completion_tokens": token_usage.get("completion_tokens", 0),
                "prompt_tokens": token_usage.get("prompt_tokens", 0),
                "total_tokens": token_usage.get("total_tokens", 0)
            }

            metadata = {
                "confidence": getattr(generation, "confidence", 1.0),
                "performance": {
                    "total_duration": response.llm_output.get("duration", 0),
                    "tokens_per_second": response.llm_output.get("tokens_per_second", 0)
                }
            }

            # Add schema to metadata if provided
            if response_schema:
                metadata["response_schema"] = response_schema

            return AICompletionResponse(
                content=content,
                finish_reason=generation.generation_info.get("finish_reason"),
                usage=usage,
                metadata=metadata,
                response_schema=response_schema
            )

        except Exception as e:
            raise AIServiceError(
                message="Failed to parse AI response: {}".format(str(e)),
                code="PARSING_ERROR",
                details={
                    "error": str(e),
                    "raw_response": generation.text,
                    "parsed_content": parsed_content.model_dump() if 'parsed_content' in locals() else None
                }
            )

    def _convert_messages(self, messages: List[APIMessage]) -> List[BaseMessage]:
        """Convert API messages to LangChain format"""
        mapping = {
            "system": SystemMessage,
            "user": HumanMessage,
            "assistant": AIMessage
        }
        return [mapping[msg.role](content=msg.content) for msg in messages]

    def _add_instruction(self, messages: List[BaseMessage], instruction: str) -> List[BaseMessage]:
        """Add instruction to system message or create new one"""
        for msg in messages:
            if isinstance(msg, SystemMessage):
                msg.content = "{}\n\n{}".format(msg.content, instruction)
                return messages
        return [SystemMessage(content=instruction)] + messages

    @abstractmethod
    async def _complete_internal(
        self,
        request: AICompletionRequest,
        response_schema: Optional[Dict[str, Any]] = None
    ) -> AICompletionResponse:
        """Provider-specific completion implementation"""
        pass

    async def complete(self, request: AICompletionRequest, response_schema: Optional[Dict] = None) -> AICompletionResponse:
        """Generate completion with automatic token limit handling and retries"""
        max_retries = 3
        current_retry = 0
        last_error = None
        original_max_tokens = request.max_tokens

        while current_retry < max_retries:
            try:
                response = await self._complete_internal(request, response_schema)

                # Reset max_tokens if successful after retry
                if current_retry > 0:
                    request.max_tokens = original_max_tokens

                return response

            except Exception as e:
                current_retry += 1
                last_error = e

                # Only retry on length-related errors
                if not isinstance(e, LengthFinishReasonError):
                    raise AIServiceError(
                        message="AI provider error: {}".format(str(e)),
                        code="PROVIDER_ERROR",
                        details={
                            "error": str(e),
                            "error_type": type(e).__name__,
                            "provider": self.__class__.__name__,
                            "attempt": current_retry
                        }
                    )

                # Extract usage info for better retry handling
                usage = getattr(e.completion, 'usage', None)
                if usage:
                    # Double tokens for schema responses, increase by 20% for others
                    new_max_tokens = int(
                        usage.completion_tokens * 2) if response_schema else int(usage.completion_tokens * 1.2)
                else:
                    # Fallback if we can't get usage info
                    new_max_tokens = int(request.max_tokens * 1.5)

                logger.warning(
                    "Response truncated due to length limit (attempt {}/{})".format(
                        current_retry, max_retries
                    ),
                    extra={
                        "error": str(e),
                        "current_max_tokens": request.max_tokens,
                        "new_max_tokens": new_max_tokens,
                        "has_schema": bool(response_schema)
                    }
                )

                request.max_tokens = new_max_tokens

        # If we exhausted retries
        error_detail = AILengthLimitErrorDetail(
            code="LENGTH_LIMIT_EXCEEDED",
            completion_tokens=getattr(
                last_error.completion.usage, 'completion_tokens', 0),
            prompt_tokens=getattr(last_error.completion.usage, 'prompt_tokens', 0),
            total_tokens=getattr(last_error.completion.usage, 'total_tokens', 0),
            max_tokens=request.max_tokens,
            provider=self.__class__.__name__
        )

        raise AIServiceError(
            message="Failed to generate response after {} attempts".format(max_retries),
            code="MAX_RETRIES_EXCEEDED",
            details=error_detail.model_dump()
        )

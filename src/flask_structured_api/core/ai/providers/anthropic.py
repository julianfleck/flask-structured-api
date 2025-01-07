from typing import Optional, Dict, Any
from langchain_anthropic import ChatAnthropic
from langchain.schema import SystemMessage
from flask import current_app

from flask_structured_api.core.ai.providers.base import BaseProvider
from flask_structured_api.core.models.requests.ai import AICompletionRequest
from flask_structured_api.core.models.responses.ai import AICompletionResponse
from flask_structured_api.core.config import settings


class AnthropicProvider(BaseProvider):
    def __init__(self):
        api_key = getattr(settings, "AI_ANTHROPIC_API_KEY", None) or settings.AI_API_KEY
        if not api_key:
            raise ValueError(
                "No API key found. Please set either AI_ANTHROPIC_API_KEY or AI_API_KEY")

        model = getattr(settings, "AI_ANTHROPIC_MODEL", None) or settings.AI_MODEL

        current_app.ai_logger.info(
            f"Initializing Anthropic provider with model: {model}")

        super().__init__(
            ChatAnthropic(
                anthropic_api_key=api_key,
                model=model,
                temperature=settings.AI_TEMPERATURE,
                max_retries=3,
                model_kwargs={"response_format": {"type": "json_object"}}
            )
        )

    async def _complete_internal(
        self,
        request: AICompletionRequest,
        response_schema: Optional[Dict[str, Any]] = None
    ) -> AICompletionResponse:
        messages = self._convert_messages(request.messages)
        current_app.ai_logger.debug("Processing request with Anthropic", extra={
            "message_count": len(messages),
            "has_schema": bool(response_schema)
        })

        if response_schema:
            system_msg = next(
                (msg for msg in messages if isinstance(msg, SystemMessage)), None)
            schema_instruction = "\n\nRespond in the following JSON format:\n{}".format(
                response_schema)

            if system_msg:
                system_msg.content += schema_instruction
            else:
                messages.insert(0, SystemMessage(content=schema_instruction))

        response = await self.model.agenerate(
            [messages],
            temperature=request.temperature,
            max_tokens=self._get_max_tokens(request.max_tokens)
        )

        current_app.ai_logger.debug("Received response from Anthropic", extra={
            "finish_reason": response.generations[0][0].finish_reason,
            "usage": response.usage
        })

        return AICompletionResponse(
            content=response.generations[0][0].text,
            finish_reason=response.generations[0][0].finish_reason,
            usage=response.usage or {}
        )

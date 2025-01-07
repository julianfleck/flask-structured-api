from typing import Optional, Dict, Any
from langchain_openai import ChatOpenAI
from flask_structured_api.core.ai.providers.base import BaseProvider
from flask_structured_api.core.models.requests.ai import AICompletionRequest
from flask_structured_api.core.models.responses.ai import AICompletionResponse
from flask_structured_api.core.config import settings
from flask_structured_api.core.utils.logger import get_standalone_logger
from flask_structured_api.core.exceptions.ai import AIServiceError

logger = get_standalone_logger("ai.provider.openai")


class OpenAIProvider(BaseProvider):
    def __init__(self):
        api_key = getattr(settings, "AI_OPENAI_API_KEY", None) or settings.AI_API_KEY
        if not api_key:
            raise ValueError(
                "No API key found. Please set either AI_OPENAI_API_KEY or AI_API_KEY")

        model = getattr(settings, "AI_OPENAI_MODEL", None) or settings.AI_MODEL

        logger.info("Initializing OpenAI provider with model: {}".format(model))

        super().__init__(
            ChatOpenAI(
                openai_api_key=api_key,
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
        try:
            response = await self.model.agenerate(
                [self.prepare_messages(request.messages, response_schema)],
                temperature=request.temperature,
                max_tokens=self.get_max_tokens(request.max_tokens)
            )
            return self.process_response(response)

        except Exception as e:
            logger.error("OpenAI provider error", exc_info=True, extra={
                "error": str(e),
                "error_type": type(e).__name__
            })
            raise AIServiceError(
                message="OpenAI provider error: {}".format(str(e)),
                code="OPENAI_ERROR",
                details={
                    "error": str(e),
                    "error_type": type(e).__name__,
                    "provider": self.__class__.__name__,
                    "raw_response": getattr(e, 'response', None)
                }
            )

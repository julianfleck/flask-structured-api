# app/core/ai/service.py
from typing import Tuple, Any, List, Optional, Type
import asyncio
from pydantic import BaseModel, ValidationError
import time
import random


class AIService:
    def __init__(self, provider: AIProvider):
        self.provider = provider
        self.warning_collector = WarningCollector()

    async def complete_with_validation(
        self,
        request: AICompletionRequest,
        validation_model: Type[BaseModel],
        max_retries: int = 3,
        initial_delay: float = 1.0
    ) -> Tuple[Any, List[str]]:
        """Generate and validate completion with retry mechanism"""
        attempt = 0
        last_exception = None

        while attempt < max_retries:
            try:
                # Log request
                self.provider.log_request(request)
                start_time = time.time()

                # Generate completion
                response = await self.provider.complete(request)

                # Log response
                duration_ms = int((time.time() - start_time) * 1000)
                self.provider.log_response(response, duration_ms)

                # Quality checks
                if response.usage.get('total_tokens', 0) > 1000:
                    self.warning_collector.add_warning(
                        "High token usage detected",
                        "high_token_usage"
                    )

                # Schema validation
                validated_data = validation_model.parse_raw(response.content)
                return validated_data, response.warnings

            except Exception as e:
                last_exception = e
                attempt += 1
                if attempt < max_retries:
                    # Exponential backoff with jitter
                    delay = initial_delay * (2 ** (attempt - 1))
                    jitter = random.uniform(0, 0.1 * delay)
                    await asyncio.sleep(delay + jitter)
                else:
                    self.warning_collector.add_warning(
                        "Max retries exceeded",
                        "retry_exhausted"
                    )
                    raise AIResponseValidationError(
                        "Response validation failed after retries",
                        validation_errors=str(last_exception)
                    )

import json
from functools import wraps
from time import time
from typing import Any, Callable

from flask import g, current_app


def log_ai_request(f: Callable[..., Any]) -> Callable[..., Any]:
    """Decorator to log AI model requests with detailed information"""
    @wraps(f)
    async def decorated(*args, **kwargs):
        start_time = time()

        # Extract request details from kwargs
        request = kwargs.get('request', None)
        if not request:
            request = args[1] if len(args) > 1 else None

        if request:
            debug_info = {
                "provider": args[0].__class__.__name__ if args else "unknown",
                "messages": [msg.model_dump() for msg in request.messages],
                "temperature": request.temperature,
                "max_tokens": request.max_tokens,
                "response_schema": kwargs.get('response_schema', None),
                "request_id": getattr(g, "request_id", None),
                "timestamp": start_time
            }

            logger = current_app.ai_logger
            logger.debug(
                "AI Request Details:\n" + json.dumps(debug_info, indent=2),
                extra={"ai_request": debug_info}
            )

        try:
            result = await f(*args, **kwargs)
            return result
        except Exception as e:
            logger = current_app.ai_logger
            logger.error(
                "AI Request Failed: {}".format(str(e)),
                extra={
                    "error": str(e),
                    "request_details": debug_info if request else None
                },
                exc_info=True
            )
            raise

    return decorated


def log_ai_response(f: Callable[..., Any]) -> Callable[..., Any]:
    """Decorator to log AI model responses with performance metrics"""
    @wraps(f)
    async def decorated(*args, **kwargs):
        start_time = time()

        try:
            result = await f(*args, **kwargs)
            duration = time() - start_time

            # Extract response details, handling nested structures
            if hasattr(result, 'model_dump'):
                response_dict = result.model_dump()
            else:
                response_dict = result if isinstance(result, dict) else {}

            debug_info = {
                "provider": args[0].__class__.__name__ if args else "unknown",
                "duration": f"{duration:.3f}s",
                "content": response_dict.get('content'),
                "finish_reason": response_dict.get('finish_reason'),
                "usage": response_dict.get('usage'),
                "request_id": getattr(g, "request_id", None),
                "timestamp": time(),
                "raw_response": response_dict,  # Include full response for debugging
                "performance": {
                    "total_duration": duration,
                    "tokens_per_second": (
                        response_dict.get('usage', {}).get("total_tokens", 0) / duration
                        if response_dict.get('usage') and duration > 0 else 0
                    )
                }
            }

            logger = current_app.ai_logger
            logger.debug(
                "AI Response Details:\n" + json.dumps(debug_info, indent=2),
                extra={"ai_response": debug_info}
            )

            return result
        except Exception as e:
            duration = time() - start_time
            logger = current_app.ai_logger
            logger.error(
                f"AI Response Failed after {duration:.3f}s: {str(e)}",
                extra={
                    "duration": f"{duration:.3f}s",
                    "error": str(e)
                },
                exc_info=True
            )
            raise

    return decorated

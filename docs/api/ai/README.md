# AI API Endpoints

This document details the AI-powered endpoints provided by the Flask API Boilerplate.

## Text Generation

### `POST /ai/generate`

Generates text using the configured AI provider.

```python
# Request
POST /api/v1/ai/generate
Content-Type: application/json
Authorization: Bearer <your_token>

{
    "prompt": "Write a story about a robot learning to paint",
    "max_tokens": 500,
    "temperature": 0.7,
    "model": "gpt-4",  // optional, defaults to config
    "stream": false    // optional, defaults to false
}
```

```python
# Response 200 OK
{
    "success": true,
    "data": {
        "text": "In a sunlit studio apartment, Robot Unit-7 held a paintbrush...",
        "usage": {
            "prompt_tokens": 10,
            "completion_tokens": 486,
            "total_tokens": 496
        },
        "model": "gpt-4"
    }
}
```

### Streaming Response

When `stream: true` is set, the endpoint returns a stream of Server-Sent Events:

```python
# Response 200 OK
event: completion
data: {"text": "In a sunlit ", "finish_reason": null}

event: completion
data: {"text": "studio apartment", "finish_reason": null}

event: completion
data: {"text": "...", "finish_reason": "stop"}

event: done
data: {"usage": {"prompt_tokens": 10, "completion_tokens": 486, "total_tokens": 496}}
```

## Rate Limits

| Endpoint | Free Tier | Pro Tier | Enterprise Tier |
|----------|-----------|-----------|-----------------|
| `/ai/generate` | 10/hour | 100/hour | Custom |

## Error Responses

```python
# 400 Bad Request - Invalid parameters
{
    "success": false,
    "error": {
        "code": "VAL_INVALID_FORMAT",
        "message": "Invalid request parameters",
        "details": {
            "max_tokens": "Must be between 1 and 4000"
        }
    }
}

# 402 Payment Required - Usage limit exceeded
{
    "success": false,
    "error": {
        "code": "AI_TOKEN_LIMIT",
        "message": "Monthly token limit exceeded",
        "details": {
            "limit": 100000,
            "used": 100250
        }
    }
}

# 503 Service Unavailable - AI provider error
{
    "success": false,
    "error": {
        "code": "AI_PROVIDER_ERROR",
        "message": "AI service temporarily unavailable",
        "details": {
            "provider": "openai",
            "status": 503
        }
    }
}
```

## Implementation Example

```python
import requests

API_URL = "http://localhost:5000/api/v1"
TOKEN = "your-token"

def generate_text(prompt: str, **kwargs):
    response = requests.post(
        f"{API_URL}/ai/generate",
        headers={
            "Authorization": f"Bearer {TOKEN}",
            "Content-Type": "application/json"
        },
        json={
            "prompt": prompt,
            "max_tokens": kwargs.get("max_tokens", 500),
            "temperature": kwargs.get("temperature", 0.7),
            "stream": kwargs.get("stream", False)
        }
    )
    
    if response.status_code == 200:
        return response.json()["data"]["text"]
    else:
        error = response.json()["error"]
        raise Exception(f"Generation failed: {error['message']}")
```

## Extending the AI API

To add custom AI endpoints, create new routes in `app/api/v1/endpoints/ai/`:

```python
# app/api/v1/endpoints/ai/custom.py
from flask import Blueprint
from app.core.responses import SuccessResponse
from app.core.auth import require_auth
from app.core.ai import ai_service

custom_ai_bp = Blueprint('custom_ai', __name__)

@custom_ai_bp.route('/analyze', methods=['POST'])
@require_auth
async def analyze_text():
    """Custom endpoint for text analysis"""
    text = request.json["text"]
    result = await ai_service.analyze(text)
    return SuccessResponse(data=result).dict()
```

For implementation details of the AI service, see:

````103:124:docs/architecture/README.md
## AI Service Integration

Modular AI service integration supporting multiple providers:
- Provider-agnostic interface
- Response validation
- Error handling
- Request/response logging

```python
# app/core/ai/base.py
class AIProvider(Protocol):
    """Base protocol for AI providers"""
    async def generate(self, prompt: str, **kwargs) -> str:
        """Generate text using AI model"""
        ...

# app/core/ai/providers/openai.py
class OpenAIProvider(AIProvider):
    """OpenAI implementation"""
    def __init__(self):
        self.client = OpenAI(api_key=settings.AI_API_KEY)
```
````


## Configuration

AI-specific environment variables:
```env
# AI Provider Settings
AI_PROVIDER=openai  # or 'azure', 'anthropic'
AI_API_KEY=your-api-key
AI_MODEL=gpt-4     # default model
AI_MAX_TOKENS=2000 # default max tokens
AI_TEMPERATURE=0.7 # default temperature

# Optional Provider-Specific Settings
AI_AZURE_ENDPOINT=https://your-azure-endpoint
AI_ANTHROPIC_VERSION=2023-06-01
```

For more details on AI integration, see the [Architecture Documentation](../architecture/README.md).
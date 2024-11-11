# API Documentation

Welcome to the API documentation for the Flask AI API Boilerplate. This guide covers all available endpoints, authentication, response formats, and best practices.

## Table of Contents

- [Authentication](#authentication)
- [Response Format](#response-format)
- [Rate Limiting](#rate-limiting)
- [API Versioning](#api-versioning)
- [Available Endpoints](#available-endpoints)

## Authentication

All protected endpoints require a Bearer token in the Authorization header:

```bash
Authorization: Bearer <your_token>
```

### Getting a Token

1. Create a new token using the CLI:
```bash
flask tokens create-token
```

2. Or use the authentication endpoint:
```bash
curl -X POST http://localhost:5000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com", "password": "your_password"}'
```

## Response Format

All API responses follow a standard format:

### Success Response
```json
{
    "success": true,
    "message": "Optional success message",
    "data": {
        // Response data
    },
    "warnings": []  // Optional warnings
}
```

### Error Response
```json
{
    "success": false,
    "message": "Error message",
    "error": {
        "code": "error_code",
        "details": {}  // Additional error details
    },
    "status": 400  // HTTP status code
}
```

## Rate Limiting

Endpoints are rate-limited based on the client's API key tier:

| Tier | Requests/Minute | Burst |
|------|----------------|--------|
| Free | 10 | 20 |
| Pro | 60 | 100 |
| Enterprise | 600 | 1000 |

Rate limit headers are included in all responses:
```
X-RateLimit-Limit: 60
X-RateLimit-Remaining: 59
X-RateLimit-Reset: 1699700000
```

## API Versioning

API versions are specified in the URL path:
```
/api/v1/endpoint  # Version 1
/api/v2/endpoint  # Version 2
```

The current stable version is `v1`. Version information is included in response headers:
```
X-API-Version: v1
X-API-Deprecated: false
```

## Available Endpoints

### Core API
- [Authentication](auth/README.md) - User authentication and management
  - Login
  - Token refresh
  - User registration
- [Core Endpoints](core/README.md) - Core functionality
  - Health check
  - Version info
  - Status

### AI Endpoints
- [AI Integration](ai/README.md) - AI-powered endpoints
  - Text generation
  - Content analysis
  - Embeddings

For detailed documentation of each endpoint group:
- [Authentication API →](auth/)
- [Core API →](core/)
- [AI API →](ai/)

## Using the API

### Basic Request

```python
import requests

# Configuration
API_URL = "http://localhost:5000/api/v1"
TOKEN = "your-token"

headers = {
    "Authorization": f"Bearer {TOKEN}",
    "Content-Type": "application/json"
}

# Make request
response = requests.get(
    f"{API_URL}/health",
    headers=headers
)

print(response.json())
```

### AI Request Example

```python
# Generate text using AI
response = requests.post(
    f"{API_URL}/ai/generate",
    headers=headers,
    json={
        "prompt": "Write a story about...",
        "max_tokens": 100,
        "temperature": 0.7
    }
)

print(response.json())
```

## Error Handling

Common error codes and their meanings:

| Code | Description |
|------|-------------|
| `unauthorized` | Missing or invalid authentication |
| `forbidden` | Insufficient permissions |
| `validation_error` | Invalid request data |
| `rate_limit_exceeded` | Too many requests |
| `ai_provider_error` | AI service error |

Example error handling:
```python
try:
    response = requests.post(f"{API_URL}/ai/generate", headers=headers, json=data)
    response.raise_for_status()
    result = response.json()
except requests.exceptions.HTTPError as e:
    error = e.response.json()
    print(f"Error: {error['message']} (Code: {error['error']['code']})")
```

## Testing Endpoints

Use the included Postman collection for testing:
```bash
docs/postman/Flask-AI-API.postman_collection.json
```

Or use the OpenAPI documentation interface:
```
http://localhost:5000/docs
```

## Best Practices

1. **Always Include Headers**
   ```python
   headers = {
       "Authorization": f"Bearer {TOKEN}",
       "Content-Type": "application/json",
       "Accept": "application/json"
   }
   ```

2. **Handle Rate Limits**
   ```python
   if response.status_code == 429:
       retry_after = int(response.headers.get('Retry-After', 60))
       time.sleep(retry_after)
   ```

3. **Validate Input**
   ```python
   # Use provided schemas
   from app.models.requests import GenerationRequest
   
   data = GenerationRequest(
       prompt="Your prompt",
       max_tokens=100
   ).dict()
   ```

## Additional Resources

- [API Examples](../getting-started/examples/)
- [Error Reference](errors.md)
- [Rate Limiting Guide](../guides/rate-limiting.md)
- [Authentication Guide](../guides/authentication.md)

## Getting Help

- [Open an Issue](https://github.com/julianfleck/flask-ai-api-boilerplate/issues)
- [View Examples](../getting-started/examples/)
<!-- - [Join Discord](https://discord.gg/your-server) -->
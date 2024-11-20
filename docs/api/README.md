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

### Authentication Flow

1. **Register a New User**
```bash
curl -X POST http://localhost:5000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "your_password",
    "full_name": "John Doe"
  }'
```

2. **Login to Get Tokens**
```bash
curl -X POST http://localhost:5000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "your_password"
  }'
```

The login response provides both access and refresh tokens:
```json
{
    "success": true,
    "data": {
        "access_token": "eyJhbG...",
        "refresh_token": "eyJhbG...",
        "token_type": "bearer",
        "expires_in": 3600
    }
}
```

### Token Management

- Access tokens expire after 60 minutes
- Refresh tokens are valid for 30 days
- Use `/auth/refresh` to get a new access token:
```bash
curl -X POST http://localhost:5000/api/v1/auth/refresh \
  -H "Content-Type: application/json" \
  -d '{
    "refresh_token": "your_refresh_token"
  }'
```

### Checking Authentication

Verify your authentication status using the `/auth/me` endpoint:
```bash
curl -X GET http://localhost:5000/api/v1/auth/me \
  -H "Authorization: Bearer your_access_token"
```

### Error Codes

| Code | Description |
|------|-------------|
| `AUTH_INVALID_CREDENTIALS` | Wrong email or password |
| `AUTH_TOKEN_EXPIRED` | Access token has expired |
| `AUTH_REFRESH_TOKEN_EXPIRED` | Refresh token has expired |
| `AUTH_USER_EXISTS` | Email already registered |
| `AUTH_ACCOUNT_DISABLED` | User account is inactive |

## API Versioning

We use URL-based versioning to ensure backward compatibility:

```bash
https://api.example.com/v1/users
https://api.example.com/v2/users
```

### Version Policy

- Major versions (v1, v2) for breaking changes
- Minor versions handled through response fields
- Minimum 6 months deprecation notice
- Multiple versions supported simultaneously

### Version Lifecycle

1. **Active**: Current recommended version
2. **Maintained**: Still supported, but deprecated
3. **Sunset**: Read-only mode, 30 days until EOL
4. **End-of-Life**: Version discontinued

### Version Headers

All responses include version information:
```json
{
    "success": true,
    "data": {},
    "api_version": "2.1",
    "deprecated": false
}
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

### Validation Error Response
```json
{
    "success": false,
    "message": "Validation failed for RegisterRequest",
    "error": {
        "code": "VALIDATION_ERROR",
        "errors": [
            {
                "field": "email",
                "message": "Invalid email address",
                "type": "value_error.email"
            }
        ]
    }
}
```

All request validation errors follow a consistent structure:

- message: A human-readable description of the validation failure
- error.code: Always "VALIDATION_ERROR" for validation failures
- error.errors: List of specific validation errors with field, message, and type
- error.required_fields: List of missing required fields (if any)
- error.details: Additional context including:
  - total_errors: Number of validation errors
  - schema: The request model that failed validation
  - validation_context: Where the validation failed (usually "request_payload")

This structure helps clients to:
- Identify which fields need correction
- Handle missing required fields specifically
- Understand the validation context
- Present user-friendly error messages

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
  - `POST` `/v1/auth/register` - User registration
  - `POST` `/v1/auth/login` - Login
  - `POST` `/v1/auth/token/refresh` - Token refresh
  - `GET` `/v1/auth/me` - Check authentication
  - `POST` `/v1/auth/logout` - Logout
  - `POST` `/v1/auth/token/revoke` - Revoke token
- Version and Status
  - `GET` `/v1/health` - Health check
  - `GET` `/v1/version` - Version info
  - `GET` `/v1/status` - Status
- [Storage](storage/README.md) - Data storage
  - `GET` `/v1/storage/sessions` - List sessions
  - `GET` `/v1/storage/session/create` - Create session
  - `POST` `/v1/storage/session/list` - List sessions (paginated with metadata filters)
  - `GET` `/v1/storage/session/<session_id>` - Get session data by ID
  - `POST` `/v1/storage/session/query` - Get session data (paginated with metadata filters)
  - `POST` `/v1/storage/upload` - Upload file
  - `GET` `/v1/storage/download` - Download file
  - `DELETE` `/v1/storage/delete` - Delete file


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
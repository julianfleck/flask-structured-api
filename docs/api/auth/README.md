Let me analyze the changes and suggest documentation updates.

The main changes I see in the auth implementation are:
1. Token refresh mechanism
2. Standardized error responses
3. Rate limiting details
4. More detailed authentication flow

Here are the necessary documentation updates:

1. Update auth API docs:
```markdown:docs/api/auth/README.md
# Authentication API

This document details the authentication endpoints for user management, login, and token operations.

## Rate Limits

| Endpoint | Rate Limit | Burst |
|----------|------------|--------|
| `/auth/login` | 5/minute | 10 |
| `/auth/refresh` | 10/minute | 20 |
| `/auth/register` | 3/minute | 5 |
| `/auth/me` | 30/minute | 50 |

## Authentication Flow

1. Register user via `/auth/register`
2. Login via `/auth/login` to get access and refresh tokens
3. Use access token for protected endpoints
4. When access token expires, use `/auth/refresh` with refresh token
5. Get current user info via `/auth/me`

## Endpoints

### `POST /auth/register`

Register a new user account.

```python
# Request
POST /api/v1/auth/register
Content-Type: application/json

{
    "email": "user@example.com",
    "password": "secure_password",  # Minimum 8 characters
    "full_name": "John Doe"
}
```

```python
# Response 201 Created
{
    "success": true,
    "message": "User registered successfully",
    "data": {
        "id": 123,
        "email": "user@example.com",
        "full_name": "John Doe",
        "role": "user",
        "is_active": true
    }
}
```

### `POST /auth/login`

Authenticate user and get access/refresh tokens.

```python
# Request
POST /api/v1/auth/login
Content-Type: application/json

{
    "email": "user@example.com",
    "password": "secure_password"
}
```

```python
# Response 200 OK
{
    "success": true,
    "message": "Login successful",
    "data": {
        "access_token": "eyJ0eXAiOiJKV1...",
        "refresh_token": "eyJ0eXAiOiJKV1...",
        "token_type": "bearer",
        "expires_in": 3600  # Seconds until access token expires
    }
}
```

### `POST /auth/refresh`

Get new access token using refresh token.

```python
# Request
POST /api/v1/auth/refresh
Content-Type: application/json

{
    "refresh_token": "eyJ0eXAiOiJKV1..."
}
```

```python
# Response 200 OK
{
    "success": true,
    "message": "Token refreshed successfully", 
    "data": {
        "access_token": "eyJ0eXAiOiJKV1...",
        "refresh_token": "eyJ0eXAiOiJKV1...",  # Same refresh token
        "token_type": "bearer",
        "expires_in": 3600
    }
}
```

### `GET /auth/me`

Get current authenticated user info.

```python
# Request
GET /api/v1/auth/me
Authorization: Bearer <access_token>
```

```python
# Response 200 OK
{
    "success": true,
    "message": "Current user retrieved successfully",
    "data": {
        "id": 123,
        "email": "user@example.com",
        "full_name": "John Doe",
        "role": "user",
        "is_active": true,
        "created_at": "2024-11-12T10:30:00Z",
        "updated_at": "2024-11-12T10:30:00Z",
        "last_login_at": "2024-11-12T10:30:00Z",
        "login_count": 42,
        "preferences": {
            "theme": "dark",
            "notifications": true
        },
        "permissions": ["read:posts", "write:comments"]
    }
}
```

---

# Not yet implemented

## Password Reset

### `POST /auth/password/reset-request`

Initiates a password reset process.

```python
# Request
POST /api/v1/auth/password/reset-request
Content-Type: application/json

{
    "email": "user@example.com"
}
```

```python
# Response 200 OK
{
    "success": true,
    "message": "Password reset instructions sent to email"
}
```

### `POST /auth/password/reset`

Resets the password using a reset token.

```python
# Request
POST /api/v1/auth/password/reset
Content-Type: application/json

{
    "token": "reset_token_from_email",
    "new_password": "new_secure_password"
}
```

```python
# Response 200 OK
{
    "success": true,
    "message": "Password reset successful"
}
```

## Error Responses

All authentication errors follow the standard error format:

```python
# Response 4xx
{
    "success": false,
    "message": "Error description",
    "error": {
        "code": "ERROR_CODE",
        "details": {}  # Optional error details
    }
}
```

Common error codes:
- `AUTH_INVALID_CREDENTIALS`: Invalid email/password
- `AUTH_TOKEN_EXPIRED`: Access/refresh token expired
- `AUTH_TOKEN_INVALID`: Invalid token format/signature
- `AUTH_USER_EXISTS`: Email already registered
- `AUTH_USER_NOT_FOUND`: User not found
- `AUTH_ACCOUNT_DISABLED`: User account is inactive

```python
# 401 Unauthorized
{
    "success": false,
    "error": {
        "code": "AUTH_INVALID_CREDENTIALS",
        "message": "Invalid email or password"
    }
}

# 403 Forbidden
{
    "success": false,
    "error": {
        "code": "AUTH_TOKEN_EXPIRED",
        "message": "Authentication token has expired"
    }
}
```

For a complete list of error codes, see the [Error Reference](../errors.md).

## Rate Limits

| Endpoint | Rate Limit | Burst |
|----------|------------|--------|
| `/auth/login` | 5/minute | 10 |
| `/auth/refresh` | 10/minute | 20 |
| `/auth/register` | 3/minute | 5 |
| `/auth/password/reset-request` | 3/minute | 5 |

## Implementation Example

```python
import requests

API_URL = "http://localhost:5000/api/v1"

def login(email: str, password: str) -> dict:
    response = requests.post(
        f"{API_URL}/auth/login",
        json={
            "email": email,
            "password": password
        }
    )
    
    if response.status_code == 200:
        tokens = response.json()["data"]
        return tokens
    else:
        error = response.json()["error"]
        raise Exception(f"Login failed: {error['message']}")
```

For more details on authentication and security, see the [Authentication Guide](../guides/authentication.md).
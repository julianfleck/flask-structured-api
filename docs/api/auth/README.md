# Authentication API

This document details the authentication endpoints for user management, login, and token operations.

## Login

### `POST /auth/login`

Authenticates a user and returns access and refresh tokens.

```python
# Request
POST /api/v1/auth/login
Content-Type: application/json

{
    "email": "user@example.com",
    "password": "your_password"
}
```

```python
# Response 200 OK
{
    "success": true,
    "data": {
        "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
        "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
        "token_type": "bearer",
        "expires_in": 3600
    }
}
```

## Token Refresh

### `POST /auth/refresh`

Gets a new access token using a refresh token.

```python
# Request
POST /api/v1/auth/refresh
Authorization: Bearer <refresh_token>
```

```python
# Response 200 OK
{
    "success": true,
    "data": {
        "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
        "token_type": "bearer",
        "expires_in": 3600
    }
}
```

## User Registration

### `POST /auth/register`

Creates a new user account.

```python
# Request
POST /api/v1/auth/register
Content-Type: application/json

{
    "email": "newuser@example.com",
    "password": "secure_password",
    "full_name": "John Doe"
}
```

```python
# Response 201 Created
{
    "success": true,
    "message": "User registered successfully",
    "data": {
        "user_id": 123,
        "email": "newuser@example.com",
        "full_name": "John Doe",
        "created_at": "2024-03-20T12:00:00Z"
    }
}
```

## Current User Info

### `GET /auth/me`

Returns information about the currently authenticated user.

```python
# Request
GET /api/v1/auth/me
Authorization: Bearer <access_token>
```

```python
# Response 200 OK
{
    "success": true,
    "data": {
        "user_id": 123,
        "email": "user@example.com",
        "full_name": "John Doe",
        "created_at": "2024-03-20T12:00:00Z",
        "roles": ["user"],
        "settings": {
            "notifications_enabled": true,
            "theme": "light"
        }
    }
}
```

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
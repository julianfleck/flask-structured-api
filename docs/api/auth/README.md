# Authentication API

This document details the authentication endpoints for user management, login, token operations, and API key management.

## Authentication Methods

### 1. JWT Tokens (Bearer Authentication)
- Access tokens for short-lived authentication
- Refresh tokens for obtaining new access tokens
- Used primarily for interactive sessions

### 2. API Keys
- Long-lived authentication tokens
- Suitable for automated systems and API integrations
- Support for multiple active keys per user
- Tracking of key usage and optional expiration

## Rate Limits

| Endpoint | Rate Limit | Burst |
|----------|------------|--------|
| `/auth/login` | 5/minute | 10 |
| `/auth/refresh` | 10/minute | 20 |
| `/auth/register` | 3/minute | 5 |
| `/auth/me` | 30/minute | 50 |

## Authentication Flow

### JWT Authentication
1. Register user via `/auth/register`
2. Login via `/auth/login` to get access and refresh tokens
3. Use access token for protected endpoints
4. When access token expires, use `/auth/refresh` with refresh token

### API Key Authentication
1. Create API key via `/auth/api-keys`
2. Use API key in requests either:
   - Header: `X-API-Key: sk_your_key_here`
   - Or: `Authorization: ApiKey sk_your_key_here`

## Using Authentication

### Protected Endpoint Example
```python
from flask_structured_api.core.auth import require_auth, require_roles
from app.models.enums import UserRole

@app.route('/api/v1/admin/users', methods=['GET'])
@require_auth  # Requires either JWT token or API key
@require_roles(UserRole.ADMIN)  # Only allows admin users
def list_users():
    """List all users (admin only)"""
    users = User.query.all()
    return jsonify(users)

@app.route('/api/v1/items', methods=['GET'])
@require_auth  # Supports both JWT tokens and API keys
def list_items():
    """List items for current user"""
    items = Item.query.filter_by(user_id=g.user_id).all()
    return jsonify(items)
```

### Client Usage Examples

#### Using JWT Token
```python
import requests

# Login to get tokens
response = requests.post('http://api.example.com/v1/auth/login', json={
    'email': 'user@example.com',
    'password': 'secure_password'
})
tokens = response.json()['data']

# Use access token
headers = {'Authorization': f"Bearer {tokens['access_token']}"}
response = requests.get('http://api.example.com/v1/items', headers=headers)
```

#### Using API Key
```python
import requests

# Create API key first via /auth/api-keys endpoint
API_KEY = 'sk_your_api_key_here'

# Method 1: X-API-Key header
headers = {'X-API-Key': API_KEY}
response = requests.get('http://api.example.com/v1/items', headers=headers)

# Method 2: Authorization header
headers = {'Authorization': f"ApiKey {API_KEY}"}
response = requests.get('http://api.example.com/v1/items', headers=headers)
```

## API Endpoints

### User Management

#### `POST /auth/register`
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

### API Key Management

#### `POST /auth/api-keys`
Create a new API key.

```python
# Request
POST /api/v1/auth/api-keys
Authorization: Bearer <access_token>
Content-Type: application/json

{
    "name": "Production API",
    "scopes": ["read:items", "write:items"]
}

# Response 201 Created
{
    "success": true,
    "message": "API key created successfully",
    "data": {
        "key": "sk_abc123...",  # Only shown once
        "name": "Production API",
        "scopes": ["read:items", "write:items"]
    }
}
```

#### `GET /auth/api-keys`
List all active API keys.

```python
# Request
GET /api/v1/auth/api-keys
Authorization: Bearer <access_token>

# Response 200 OK
{
    "success": true,
    "message": "API keys retrieved",
    "data": {
        "items": [
            {
                "id": 1,
                "name": "Production API",
                "last_used_at": "2024-03-15T10:30:00Z",
                "created_at": "2024-03-01T12:00:00Z"
            }
        ]
    }
}
```

#### `DELETE /auth/api-keys/<key_id>`
Revoke an API key. Note: Cannot revoke the key currently being used for authentication.

```python
# Request
DELETE /api/v1/auth/api-keys/123
Authorization: Bearer <access_token>

# Response 200 OK
{
    "success": true,
    "message": "API key revoked successfully"
}

# Error Response 400 Bad Request
{
    "success": false,
    "message": "Cannot revoke the API key that's currently being used",
    "error": {
        "code": "AUTH_CANNOT_REVOKE_CURRENT_KEY",
        "details": {}
    }
}
```

## Error Responses

All authentication errors follow this format:

```python
{
    "success": false,
    "message": "Error description",
    "error": {
        "code": "ERROR_CODE",
        "details": {}  # Optional error details
    }
}
```

### Common Error Codes
- `AUTH_INVALID_CREDENTIALS`: Invalid email/password
- `AUTH_TOKEN_EXPIRED`: Access/refresh token expired
- `AUTH_TOKEN_INVALID`: Invalid token format/signature
- `AUTH_USER_EXISTS`: Email already registered
- `AUTH_USER_NOT_FOUND`: User not found
- `AUTH_ACCOUNT_DISABLED`: User account is inactive
- `AUTH_INVALID_API_KEY`: Invalid or expired API key
- `AUTH_CANNOT_REVOKE_CURRENT_KEY`: Attempted to revoke currently used API key
- `AUTH_MAX_KEYS_REACHED`: Maximum number of API keys reached

## Implementation Details

### API Key Format
- Prefix: `sk_` (secret key)
- Length: 32 bytes of random data (urlsafe base64 encoded)
- Storage: Only SHA256 hash stored in database
- Metadata tracked:
  - Last used timestamp
  - Creation date
  - Optional expiration
  - Scopes (for future use)

For more details on authentication and security best practices, see the [Security Guide](../guides/security.md).
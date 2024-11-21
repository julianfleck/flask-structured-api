# Getting Started Guide

This guide will help you set up and run your first API using the Flask API Boilerplate with AI capabilities.

## Prerequisites

Before you begin, ensure you have:
- Python 3.10 or higher
- PostgreSQL 14 or higher
- Redis 6 or higher
- Docker and docker-compose (optional, but recommended)

## Installation

### Option 1: Using Docker (Recommended)

1. Clone the repository:
   ```bash
   git clone https://github.com/julianfleck/flask-ai-api-boilerplate.git
   cd flask-ai-api-boilerplate
   ```

2. Copy and configure environment variables:
   ```bash
   cp .env.example .env
   # Edit .env with your settings
   ```

3. Start the services:
   ```bash
   docker-compose up -d
   ```

4. Run database migrations:
   ```bash
   docker-compose exec api flask db upgrade
   ```

5. Create an admin user:
   ```bash
   docker-compose exec api flask users create-admin
   ```

### Option 2: Local Development

1. Clone the repository:
   ```bash
   git clone https://github.com/julianfleck/flask-ai-api-boilerplate.git
   cd flask-ai-api-boilerplate
   ```

2. Create and activate virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/macOS
   # or
   venv\Scripts\activate     # Windows
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Copy and configure environment variables:
   ```bash
   cp .env.example .env
   # Edit .env with your settings
   ```

5. Start PostgreSQL and Redis (if not using Docker)

6. Run database migrations:
   ```bash
   flask db upgrade
   ```

7. Create an admin user:
   ```bash
   flask users create-admin
   ```

## Configuration

Essential environment variables in your `.env` file:

```env
# API Settings
FLASK_APP=flask_structured_api.main:app
FLASK_ENV=development
API_DEBUG=True
API_HOST=0.0.0.0
API_PORT=5000

# Database
DATABASE_URL=postgresql://user:password@localhost:5432/dbname

# Redis
REDIS_URL=redis://localhost:6379/0

# Security
SECRET_KEY=your-secret-key-here
JWT_SECRET_KEY=your-jwt-secret-key-here

# AI Integration (optional)
AI_PROVIDER=openai  # or 'azure', 'anthropic'
AI_API_KEY=your-api-key-here
```

## Verifying Your Installation

1. Check the health endpoint:
   ```bash
   curl http://localhost:5000/health
   ```

   Expected response:
   ```json
   {
       "status": "healthy",
       "checks": {
           "database": "ok",
           "redis": "ok"
       },
       "version": "1.0.0",
       "timestamp": "2024-11-11T12:00:00.000Z"
   }
   ```

## Authentication Options

1. Using CLI Tools (recommended for development):
   ```bash
   # Create JWT token
   flask tokens create --email user@example.com --expires 60

   # Create API key
   flask api-keys create --email user@example.com --name "Dev API" --expires 30

   # List and manage API keys
   flask api-keys list --email user@example.com
   flask api-keys revoke --email user@example.com --key-id 123
   ```

2. Using HTTP Endpoints:
   ```bash
   # Login to get JWT tokens
   curl -X POST http://localhost:5000/api/v1/auth/login \
     -H "Content-Type: application/json" \
     -d '{
       "email": "user@example.com",
       "password": "your_password"
     }'

   # Create API key using JWT token
   curl -X POST http://localhost:5000/api/v1/auth/api-keys \
     -H "Authorization: Bearer your_access_token" \
     -H "Content-Type: application/json" \
     -d '{
       "name": "Production API",
       "scopes": ["read:items", "write:items"]
     }'
   ```

   Save any returned tokens or API keys securely - they won't be shown again!

## Creating Your First Endpoint

1. Create a new endpoint file in `app/api/custom/v1/hello.py`:
   ```python
   from flask import Blueprint
   from app.core.models.responses import SuccessResponse
   from app.core.auth import require_auth

   hello_bp = Blueprint('hello', __name__)

   @hello_bp.route('/hello', methods=['GET'])
   @require_auth
   def hello_world():
       return SuccessResponse(
           message="Hello from Flask API!",
           data={"version": "1.0.0"}
       ).dict()
   ```

2. Register the blueprint in `app/custom/init.py`:
   ```python
   from flask import Blueprint
   from app.api.custom.v1.hello import hello_bp

   api_v1 = Blueprint('api_v1', __name__, url_prefix='/api/v1')
   api_v1.register_blueprint(hello_bp, url_prefix='/hello')
   ```

3. Test your endpoint:
   ```bash
   # Using JWT token
   curl -H "Authorization: Bearer your-token" http://localhost:5000/api/v1/hello

   # Using API key
   curl -H "X-API-Key: your-api-key" http://localhost:5000/api/v1/hello
   ```
   
## Next Steps

- [Explore the Architecture](../architecture/README.md)
- [View API Documentation](../api/README.md)
- [Development Guide](../development/README.md)
- [Example Projects](examples/README.md)

## Common Issues

### Database Connection Failed
- Check if PostgreSQL is running
- Verify DATABASE_URL in .env
- Ensure database exists

### Redis Connection Failed
- Check if Redis is running
- Verify REDIS_URL in .env
- Check Redis port availability

### Token Issues
- Verify SECRET_KEY and JWT_SECRET_KEY are set
- Check token expiration
- Ensure proper Authorization header format

## Getting Help

- Check our [Troubleshooting Guide](../development/troubleshooting.md)
- Open an [Issue](https://github.com/julianfleck/flask-ai-api-boilerplate/issues)
- See [Examples](examples/README.md) for common use cases
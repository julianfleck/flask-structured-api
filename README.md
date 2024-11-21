# Flask Structured API

A production-ready Flask API framework with built-in storage, authentication, and AI capabilities. Designed for developers who need a robust foundation for building scalable APIs while following best practices.

## ✨ Core Features

### 🏗️ Model-First Architecture
- SQLModel + Pydantic for type-safe database operations
- Comprehensive validation with detailed error messages
- Clear separation between core and custom components
- Standardized response formats

### 🔐 Authentication & Security
- JWT token-based authentication
- API key management with scoping
- Role-based access control (RBAC)
- Request validation and sanitization
- Hash-based secure storage

### 📦 Storage System
- On-demand request/response storage
- Session-based data organization
- Compression for large payloads
- TTL-based expiration
- Flexible querying with metadata filters

### 🤖 AI Integration
- Provider-agnostic interface
- Response validation
- Automatic retry mechanisms
- Error handling with fallbacks

### 🔧 Developer Experience
- OpenAPI/Swagger documentation
- Remote debugging support
- Environment-based configuration
- Comprehensive error handling
- Warning collection system

## 🚀 Quick Start

### Using Docker (Recommended)
```bash
# Clone and setup
git clone https://github.com/julianfleck/flask-structured-api.git
cd flask-structured-api
cp .env.example .env

# Start services
docker-compose up -d

# Initialize database
docker-compose exec api flask db upgrade
docker-compose exec api flask users create-admin
```

### Local Development
```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/macOS
# or
venv\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt

# Setup pre-commit hooks
pre-commit install
```

## 📚 Documentation

- [Getting Started Guide](docs/getting-started/README.md)
- [Architecture Overview](docs/architecture/README.md)
- [API Documentation](docs/api/README.md)
- [Development Guide](docs/development/README.md)
- [Deployment Guide](docs/deployment/README.md)

## 💡 Example Usage

### Protected Endpoint
```python
from flask import Blueprint
from flask_structured_api.core.auth import require_auth
from flask_structured_api.models.responses import SuccessResponse

bp = Blueprint('example', __name__)

@bp.route('/hello', methods=['GET'])
@require_auth
def hello_world():
    return SuccessResponse(
        message="Hello, World!",
        data={"authenticated": True}
    ).dict()
```

### Storage Decorator
```python
from flask_structured_api.core.storage import store_api_data

@bp.route('/ai/generate', methods=['POST'])
@require_auth
@store_api_data()  # Automatically stores request/response
def generate():
    result = ai_service.generate(request.json)
    return SuccessResponse(data=result).dict()
```

## ⚙️ Configuration

Essential environment variables:
```env
# Required
FLASK_APP=flask_structured_api.main:app
DATABASE_URL=postgresql://user:password@localhost:5432/dbname
REDIS_URL=redis://localhost:6379/0
SECRET_KEY=your-secret-key

# Optional
AI_PROVIDER=openai
AI_API_KEY=your-api-key
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Submit a pull request

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## 📝 License

This project is licensed under the Apache License 2.0 - see [LICENSE](LICENSE) and [NOTICE](NOTICE) for details.

When using this project, please include the following attribution in your documentation:

```
Based on Flask Structured API (https://github.com/julianfleck/flask-structured-api)
Created by Julian Fleck and contributors
```
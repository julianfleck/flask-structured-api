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

## 🚀 Getting Started

### Option 1: Using PyPI Package (Simplest)
```bash
# Install the core package
pip install flask-structured-api

# Create new project
mkdir my-api && cd my-api

# Initialize basic structure
flask-api init

# Install dependencies
pip install -r requirements.txt
```

Note: When using the PyPI package, you'll need to set up your own PostgreSQL and Redis services.

### Option 2: Clean Initialize with Docker (Recommended)
For a fresh start with full Docker support:

```bash
# Create and enter project directory
mkdir my-api && cd my-api

# Initialize empty git repo
git init

# Add boilerplate as remote
git remote add boilerplate https://github.com/julianfleck/flask-structured-api.git

# Pull files without history
git pull boilerplate main --allow-unrelated-histories

# Make initial commit
git add .
git commit -m "Initial commit from boilerplate"

# Start services
docker-compose up -d
```

### Option 3: Direct Clone
If you want to preserve boilerplate history (not recommended for production):

```bash
# Clone the repo
git clone https://github.com/julianfleck/flask-structured-api.git my-api
cd my-api

# Start services
docker-compose up -d
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

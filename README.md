# Flask API Boilerplate with AI Integration

A production-ready Flask API boilerplate using SQLModel, PostgreSQL, Redis, and LLM integrations. Built for developers who need a robust foundation for building AI-powered APIs while following best practices.

## Author
[julianfleck](https://github.com/julianfleck)

## ✨ Features

- 🏗️ **Model-First Architecture**
  - Unified SQLModel + Pydantic models
  - Type-safe database operations
  - Clear separation of concerns
- 🤖 **AI Integration**
  - Flexible LLM provider interface
  - Response validation
  - Structured output parsing
  - Comprehensive error handling
- 🔐 **Security**
  - Role-based access control
  - JWT authentication
  - Request validation
  - Rate limiting
- 📦 **Production Ready**
  - Docker configuration
  - Monitoring setup
  - Auto-generated OpenAPI docs
  - Performance optimization

## 🚀 Quick Start

1. Clone the repository:
```bash
git clone https://github.com/julianfleck/flask-ai-api-boilerplate.git
cd flask-ai-api-boilerplate
```

2. Set up environment:
```bash
python -m venv venv
source venv/bin/activate  # Linux/macOS
# or
venv\Scripts\activate     # Windows

pip install -r requirements.txt
cp .env.example .env     # Edit with your settings
```

3. Run with Docker:
```bash
docker-compose up -d
docker-compose exec api flask db upgrade
docker-compose exec api flask users create-admin
```

## 🏗️ Project Structure

```
flask-ai-api-boilerplate/
├── app/ # Application package
│ ├── api/ # API endpoints
│ │ └── v1/ # API version 1
│ ├── core/ # Core functionality
│ │ └── ai/ # AI service components
│ ├── models/ # Database & schema models
│ └── services/ # Business logic
├── tests/ # Test suite
├── docker/ # Docker configurations
├── docs/ # Documentation
│ ├── architecture/ # Architecture docs
│ ├── guides/ # User guides
│ └── development/ # Development docs
└── CHANGELOG.md # Version history
```

## 💡 Example Usage

### Basic Endpoint
```python
from flask import Blueprint
from app.core.responses import SuccessResponse
from app.core.auth import require_auth

example_bp = Blueprint('example', __name__)

@example_bp.route('/', methods=['GET'])
@require_auth
def hello_world():
    return SuccessResponse(
        message="Hello from Flask API!",
        data={"version": "1.0.0"}
    ).dict()
```

### AI Integration
```python
from app.core.ai import AIService
from app.models.ai import CompletionRequest

@ai_bp.post('/generate')
@require_auth
async def generate_content():
    service = AIService()
    result = await service.complete(
        CompletionRequest(
            prompt="Your prompt here",
            max_tokens=100
        )
    )
    return SuccessResponse(data=result).dict()
```

## 📚 Documentation

- Full documentation: `/docs`
- OpenAPI specification: `/openapi.json`
- Health check: `/health`

## ⚙️ Configuration

Key environment variables:

```env
# API Settings
FLASK_APP=app.main:create_app
API_DEBUG=True

# Database
DATABASE_URL=postgresql://user:password@localhost:5432/dbname

# Security
SECRET_KEY=your-secret-key
JWT_SECRET_KEY=your-jwt-secret

# AI Provider (optional)
AI_PROVIDER=openai
AI_API_KEY=your-api-key
```

## 🧪 Testing

```bash
# Install development dependencies
pip install -r requirements-dev.txt

# Run tests
pytest

# Run with coverage
pytest --cov=app
```

## 🔧 Development

1. Install pre-commit hooks:
```bash
pre-commit install
```

2. Format code:
```bash
black app tests
isort app tests
```

3. Run type checking:
```bash
mypy app
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Run tests and linting
4. Submit a pull request

See [CONTRIBUTING.md](CONTRIBUTING.md) for detailed guidelines.

## 📝 License

This project is licensed under the MIT License - see [LICENSE](LICENSE) for details.

## 🙏 Acknowledgments

- Built with Flask and SQLModel
- AI integrations powered by LangChain
- Documentation using OpenAPI


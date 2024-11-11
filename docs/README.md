# Flask API Boilerplate Documentation

Welcome to the Flask API Boilerplate documentation. This documentation will help you get started with building production-ready APIs with AI capabilities.

## 📚 Documentation Sections

### [Getting Started](getting-started/README.md)
- Installation and setup
- Basic configuration
- First API endpoint
- Environment variables
- Quick start examples

### [Architecture](architecture/README.md)
- Model-first design
- Core components
  - [Database structure](architecture/README.md#database-structure)
  - [Caching strategy](architecture/README.md#caching)
  - [Rate limiting](architecture/README.md#rate-limiting)
  - [Authentication & Authorization](architecture/README.md#authentication)
- AI service integration
- Security model

### [API Reference](api/README.md)
- [Standard response formats](api/README.md#standard-response-format)
- [Error handling](api/README.md#error-handling)
- [Rate limiting configuration](api/README.md#rate-limiting)

#### [Core Endpoints](api/core/README.md) 
- `GET /health` - Health check
- `GET /version` - API version info
- `GET /status` - System status

#### [Authentication](api/auth/README.md)
- `POST /auth/login` - User login
- `POST /auth/refresh` - Refresh token
- `POST /auth/register` - User registration
- `GET /auth/me` - Current user info

#### [AI Integration](api/ai/README.md)
- `POST /ai/generate` - Text generation endpoint

Each API section includes:
- Detailed request/response formats
- Authentication requirements
- Example requests
- Error handling
- Rate limiting considerations

### [Development Guide](development/README.md)
- [Setting up development environment](development/README.md#setup)
- [Code style and standards](development/README.md#code-style)
- [Testing](development/README.md#testing)
- Pre-commit hooks
- Dependency management
- Type hints and validation
- [Database migrations](development/README.md#database-migrations)
- [CLI tools](development/README.md#cli-tools)

### [Deployment Guide](deployment/README.md)
- [Docker deployment](deployment/README.md#docker)
- [Environment configuration](deployment/README.md#configuration)
- [Production checklist](deployment/README.md#checklist)
- Monitoring setup
- Scaling strategies
- Backup procedures
- SSL/TLS configuration

## 🚀 Key Features

### [Model-First Architecture](architecture/README.md#model-first-design)
- Unified SQLModel + Pydantic models
- Type-safe database operations
- Clear separation of concerns

### [Core Infrastructure](architecture/README.md#core-components)
- Configurable rate limiting
- Redis caching
- Health monitoring
- Role-based access control

### [AI Integration](api/ai/README.md)
- Flexible LLM provider interface
- Response validation
- Structured output parsing
- Comprehensive error handling

### [Security](architecture/README.md#security)
- JWT authentication
- Request validation
- Environment-based configuration

### Production Ready
- [Docker configuration](deployment/README.md#docker)
- [Monitoring setup](deployment/README.md#monitoring)
- Auto-generated OpenAPI docs
- Performance optimization

## 📋 Quick Reference

### Environment Variables
```env
# Essential settings
FLASK_APP=app.main:create_app
DATABASE_URL=postgresql://user:password@localhost:5432/dbname
REDIS_URL=redis://localhost:6379/0
SECRET_KEY=your-secret-key-here

# Rate Limiting (optional)
RATE_LIMIT_ENABLED=true
RATE_LIMIT_DEFAULT=60
RATE_LIMIT_WINDOW=3600

# AI Integration
AI_PROVIDER=openai
AI_API_KEY=your-api-key-here
```

### Common Commands
```bash
# Development
flask run --debug

# Database
flask db upgrade

# Create admin user
flask users create-admin

# Docker
docker-compose up -d
```

### Basic Request Example
```python
import requests

headers = {
    "Authorization": f"Bearer {TOKEN}",
    "Content-Type": "application/json"
}

response = requests.post(
    "http://localhost:5000/api/v1/ai/generate",
    headers=headers,
    json={
        "prompt": "Your prompt here",
        "max_tokens": 100
    }
)
```

## 🔗 External Links

- [GitHub Repository](https://github.com/julianfleck/flask-ai-api-boilerplate)
- [Issue Tracker](https://github.com/julianfleck/flask-ai-api-boilerplate/issues)
- [Changelog](../CHANGELOG.md)

## 🤝 Contributing

See our [Contributing Guidelines](development/CONTRIBUTING.md) for details on:
- Code style
- Pull request process
- Development setup
- Testing requirements

## ❓ Getting Help

- Check the documentation sections above for detailed information
- Open an [issue](https://github.com/julianfleck/flask-ai-api-boilerplate/issues) for bugs
- See [examples](getting-started/examples/) for common use cases
- Review [troubleshooting](development/troubleshooting.md) for common issues

## 📝 License

This project is licensed under the XXX License - see the [LICENSE](../LICENSE) file for details.
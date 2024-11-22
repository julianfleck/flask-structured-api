# Flask Structured API Documentation

Welcome to the Flask Structured API documentation. This framework provides a robust foundation for building production-ready APIs with built-in storage, authentication, and AI capabilities.

## 🚀 Quick Start

For the fastest way to get up and running, see our [Getting Started Guide](getting-started/README.md).

Essential commands:
```bash
# Using Docker (Recommended)
docker-compose up -d
docker-compose --workdir /app/src exec api flask db upgrade
docker-compose --workdir /app/src exec api flask users create-admin

# Local Development
python -m venv venv
source venv/bin/activate  # Linux/macOS
pip install -r requirements.txt
```

## 📚 Core Documentation

### [Getting Started](getting-started/README.md)
- Installation and setup
- Basic configuration
- First API endpoint
- Environment variables
- Quick start examples

### [Architecture](architecture/README.md)
- Model-first design
- System components
- Database structure
- Authentication flow
- AI integration
- Storage system
- Background tasks

### [API Reference](api/README.md)
- Authentication & security
- Endpoints overview
- Response formats
- Error handling
- Rate limiting
- OpenAPI/Swagger docs

### [Development](development/README.md)
- Local setup
- Code style
- Testing
- CLI tools
- Debugging
- Type hints

### [Deployment](deployment/README.md)
- Docker deployment
- Environment configuration
- Production checklist
- Monitoring setup

## ⚙️ Essential Configuration

```env
# Required
FLASK_APP=flask_structured_api.main:app
DATABASE_URL=postgresql://user:password@localhost:5432/dbname
REDIS_URL=redis://localhost:6379/0
SECRET_KEY=your-secret-key-here

# Optional
RATE_LIMIT_ENABLED=true
AI_PROVIDER=openai
AI_API_KEY=your-api-key-here

# Background Tasks
CELERY_BROKER_URL=redis://localhost:6379/1
CELERY_RESULT_BACKEND=redis://localhost:6379/1
CELERY_TASK_DEFAULT_QUEUE=default
```

## 🔗 Additional Resources

- [GitHub Repository](https://github.com/julianfleck/flask-structured-api)
- [Issue Tracker](https://github.com/julianfleck/flask-structured-api/issues)
- [Changelog](../CHANGELOG.md)

## ❓ Getting Help

- See [examples](getting-started/examples/) for common use cases
- Review [Troubleshooting](development/README.md#troubleshooting)
- Open an [issue](https://github.com/julianfleck/flask-structured-api/issues) for bugs

## 📝 License

This project is licensed under the Apache License 2.0 - see the [LICENSE](../LICENSE) file for details.
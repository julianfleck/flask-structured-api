# Flask Structured API

A production-ready Flask API framework with built-in storage, authentication, and AI capabilities. Designed for developers who need a robust foundation for building scalable APIs while following best practices.

## 🚀 Getting Started

Choose your preferred installation method:

1. **PyPI Package** (Simplest)
   ```bash
   pip install flask-structured-api
   mkdir my-api && cd my-api
   flask-api init
   ```

2. **Docker Setup** (Recommended)
   ```bash
   mkdir my-api && cd my-api
   git init
   git remote add boilerplate https://github.com/julianfleck/flask-structured-api.git
   git pull boilerplate main --allow-unrelated-histories
   docker-compose up -d
   ```

See our [Getting Started Guide](docs/getting-started/README.md) for detailed setup instructions and configuration options.


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
# Flask API Boilerplate Documentation

Welcome to the Flask API Boilerplate documentation. This guide helps you build production-ready APIs with AI capabilities.

## 🚀 Quick Start

For the fastest way to get up and running, see our [Getting Started Guide](getting-started/README.md).

Essential commands:
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

## 📚 Core Documentation

### [Getting Started](getting-started/README.md)

- Installation and setup
- Basic configuration
- First API endpoint
- Environment variables
- Quick start examples

### [Architecture](architecture/README.md)
- System design and components
- Database structure
- Caching and rate limiting
- Background tasks & queues
- Warning collection system
- Authentication flow
- AI service integration

### [API Reference](api/README.md)
- Authentication
- Endpoints overview
- Response formats
- Error handling
- Rate limiting

### [Development](development/README.md)
- Local setup
- Code style
- Testing
- Database migrations
- CLI tools

### [Deployment](deployment/README.md)
- Docker deployment
- Environment configuration
- Production checklist
- Monitoring setup

## ⚙️ Essential Configuration

```env
# Required
FLASK_APP=app.main:create_app
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

- [GitHub Repository](https://github.com/julianfleck/flask-ai-api-boilerplate)
- [Issue Tracker](https://github.com/julianfleck/flask-ai-api-boilerplate/issues)
- [Changelog](../CHANGELOG.md)

## ❓ Getting Help

- See [examples](getting-started/examples/) for common use cases
- Review [Troubleshooting](development/README.md#troubleshooting)
- Open an [issue](https://github.com/julianfleck/flask-ai-api-boilerplate/issues) for bugs

## 📝 License

This project is licensed under the XXX License - see the [LICENSE](../LICENSE) file for details.
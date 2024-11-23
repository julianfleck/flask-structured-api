# Getting Started Guide

This guide will help you set up and run your first API using the Flask API Boilerplate with AI capabilities.

## Prerequisites

Before you begin, ensure you have:
- Python 3.10 or higher
- PostgreSQL 14 or higher
- Redis 6 or higher
- Docker and docker-compose (optional, but recommended)

## Installation Options

### Option 1: Using PyPI Package (Simplest)

1. Install the core package:
   ```bash
   pip install flask-structured-api
   ```

2. Create project structure:
   ```bash
   mkdir my-api && cd my-api
   flask-api init
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Set up required services:
   - PostgreSQL 14 or higher
   - Redis 6 or higher

5. Configure environment:
   ```bash
   cp .env.example .env
   # Edit .env with your database and Redis connection details
   ```

Note: When using the PyPI package, you'll need to set up your own PostgreSQL and Redis services.

### Option 2: Using Docker (Recommended)

1. Create and enter project directory:
   ```bash
   mkdir my-api && cd my-api
   ```

2. Initialize git and pull boilerplate:
   ```bash
   git init
   git remote add boilerplate https://github.com/julianfleck/flask-structured-api.git
   git pull boilerplate main --allow-unrelated-histories
   ```

3. Make initial commit:
   ```bash
   git add .
   git commit -m "Initial commit from boilerplate"
   ```

4. Configure environment:
   ```bash
   cp .env.example .env
   # Edit .env with your settings
   ```

5. Start services:
   ```bash
   docker-compose up -d
   ```

6. Run database migrations:
   ```bash
   docker-compose --workdir /app/src exec api flask db upgrade
   ```

7. Create an admin user:
   ```bash
   docker-compose --workdir /app/src exec api flask users create-admin
   ```

### Option 3: Local Development

1. Clone the repository:
   ```bash
   git clone https://github.com/julianfleck/flask-structured-api.git my-api
   cd my-api
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
- Open an [Issue](https://github.com/julianfleck/flask-structured-api/issues)
- See [Examples](examples/README.md) for common use cases
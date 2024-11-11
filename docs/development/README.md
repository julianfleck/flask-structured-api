

# Development Guide

This guide covers development practices, tools, and workflows for contributing to the Flask API Boilerplate.

## Development Setup

### Prerequisites


```7:11:docs/getting-started/README.md
Before you begin, ensure you have:
- Python 3.10 or higher
- PostgreSQL 14 or higher
- Redis 6 or higher
- Docker and docker-compose (optional, but recommended)
```


### Local Development Environment

1. Clone and setup:
```bash
git clone https://github.com/julianfleck/flask-ai-api-boilerplate.git
cd flask-ai-api-boilerplate

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/macOS
# or
venv\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt
```

2. Install pre-commit hooks:
```bash
pre-commit install
```

## Code Style

We use several tools to maintain code quality:

- Black for code formatting
- isort for import sorting
- flake8 for linting
- mypy for type checking

Configuration is in `pyproject.toml`:
```toml
[tool.black]
line-length = 88
target-version = ['py310']
include = '\.pyi?$'

[tool.isort]
profile = "black"
multi_line_output = 3
```

## Testing

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app

# Run specific test file
pytest tests/test_api/test_auth.py

# Run tests matching pattern
pytest -k "test_auth"
```

### Writing Tests

Example test structure:
```python
# tests/test_api/test_auth.py
import pytest
from app.models import User

@pytest.fixture
def test_user(db_session):
    user = User(
        email="test@example.com",
        hashed_password="hashed_pwd"
    )
    db_session.add(user)
    db_session.commit()
    return user

def test_login_success(client, test_user):
    response = client.post("/api/v1/auth/login", json={
        "email": "test@example.com",
        "password": "password123"
    })
    assert response.status_code == 200
    assert "access_token" in response.json["data"]
```

## Database Migrations

```bash
# Create new migration
flask db revision --autogenerate -m "description"

# Apply migrations
flask db upgrade

# Rollback migration
flask db downgrade
```

## OpenAPI Documentation

The API documentation is automatically generated using Flask-OpenAPI:

```python
# app/core/openapi.py
from flask_openapi3 import OpenAPI
from app.models.requests import UserCreateRequest
from app.models.responses import UserResponse

app = OpenAPI(__name__)

@app.post("/users", responses={"200": UserResponse})
def create_user(body: UserCreateRequest):
    """Create a new user"""
    return create_user_logic(body)
```

Access the documentation at `/docs` or `/redoc` when running the API.

## Development Tools

### CLI Commands


```121:131:docs/README.md
# Development
flask run --debug

# Database
flask db upgrade

# Create admin user
flask users create-admin

# Docker
docker-compose up -d
```


### Debugging

```python
# Set breakpoint in code
breakpoint()

# Or use VSCode debugger configuration
{
    "name": "Flask API",
    "type": "python",
    "request": "launch",
    "module": "flask",
    "env": {
        "FLASK_APP": "app.main:create_app",
        "FLASK_ENV": "development"
    },
    "args": [
        "run",
        "--debug"
    ]
}
```

## Type Hints

We use type hints throughout the codebase:
```python
from typing import Optional, List
from app.models import User

def get_users(active_only: bool = False) -> List[User]:
    """Get list of users"""
    query = User.query
    if active_only:
        query = query.filter_by(is_active=True)
    return query.all()

def get_user_by_id(user_id: int) -> Optional[User]:
    """Get user by ID"""
    return User.query.get(user_id)
```

## Git Workflow

1. Create feature branch
```bash
git checkout -b feature/your-feature
```

2. Make changes and commit
```bash
git add .
git commit -m "feat: add new feature"
```

3. Push and create PR
```bash
git push origin feature/your-feature
```

## Documentation

- Use docstrings for functions and classes
- Keep README files up to date
- Document API changes in CHANGELOG.md
- Add type hints to all functions

## Troubleshooting


```181:194:docs/getting-started/README.md
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
```


For more details on specific topics:
- [Architecture Documentation](../architecture/README.md)
- [API Documentation](../api/README.md)
- [Deployment Guide](../deployment/README.md)
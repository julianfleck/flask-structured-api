

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
git clone https://github.com/julianfleck/flask-structured-api.git
cd flask-structured-api

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

## Code Organization

### Core vs Custom Code

- `app/core/`: Framework components (don't modify)
- `app/custom/`: Your custom implementations
- `app/api/core/`: Core API endpoints
- `app/api/custom/`: Your custom endpoints

### Adding Custom Endpoints

1. Create new endpoint in `app/api/custom/v1/`:

```python
# app/api/custom/v1/hello.py
from flask import Blueprint
from flask_structured_api.core.auth import require_auth
bp = Blueprint('hello', name)
@bp.route('/hello')
@require_auth
def hello():
    return {"message": "Hello, World!"}
```

1. Register the endpoint in your custom module:

```python
# app/custom/init.py
def init_custom_routes(app):
    from app.api.custom.v1.hello import bp
    app.register_blueprint(bp, url_prefix='/api/v1')
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

Here's the updated CLI commands section for `docs/development/README.md`:

### CLI Commands

The API provides CLI commands for common management tasks:

```bash
# Authentication
flask tokens create --email user@example.com --expires 60  # Create JWT token
flask api-keys create --email user@example.com --name "API" # Create API key
flask api-keys list --email user@example.com              # List API keys
flask api-keys revoke --email user@example.com --key-id 1 # Revoke API key

# User Management
flask users create-admin  # Create admin user

# Database
flask db upgrade         # Run migrations
flask db downgrade      # Rollback migration
flask db revision --autogenerate -m "description"  # Create migration
```

For detailed usage of any command:
```bash
flask <command> --help
```

Example outputs:

```bash
# Creating a JWT token
$ flask tokens create --email admin@example.com
Access Token (expires in 60 minutes):
eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...

Refresh Token:
eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...

# Creating an API key
$ flask api-keys create --email admin@example.com --name "Production API"
API Key (save this, it won't be shown again):
sk_live_abc123...

# Listing API keys
$ flask api-keys list --email admin@example.com
ID: 1
Name: Production API
Created: 2024-03-15 10:30:00
Last used: 2024-03-15 12:45:00
Expires: Never
Active: True
Scopes: read:items, write:items
```

## Creating CLI Commands

The API uses Click to create CLI commands. Here's how to add your own commands:

1. Create a new file in `app/cli/your_commands.py`:

```python
import click
from flask.cli import AppGroup

# Create a command group
your_cli = AppGroup('your-group', help='Description of your commands')

# Add a command to the group
@your_cli.command('command-name')
@click.option('--required-arg', prompt=True, help='Argument description')
@click.option('--optional-arg', default='default', help='Optional argument') 
def your_command(required_arg: str, optional_arg: str):
    """Command description shown in --help"""
    # Your command logic here
    click.echo(f"Doing something with {required_arg}")
```

2. Register your commands in `app/cli/__init__.py`:

```python
from flask import Flask
from app.cli.your_commands import your_cli

def init_cli(app: Flask):
    app.cli.add_command(your_cli)
```

3. Use your command:

```bash
# Show help
flask your-group --help

# Run command
flask your-group command-name --required-arg value
```

Key points:
- Use `AppGroup` to group related commands
- Add `@click.option()` for command arguments
- Provide help text for commands and options
- Use `click.echo()` for output
- Register commands in `init_cli()`


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
        "FLASK_APP": "src.flask_structured_api.main:create_app",
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
src.flask_structured_api.models import User

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
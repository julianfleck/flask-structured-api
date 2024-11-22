# Contributing to Flask Structured API

Thank you for your interest in contributing! This document provides guidelines and workflows for contributing to the project.

## 🚀 Quick Start

1. Fork and clone the repository
2. Set up development environment:
```bash
python -m venv venv
source venv/bin/activate  # Linux/macOS
# or
venv\Scripts\activate     # Windows

pip install -r requirements.txt
pip install -r requirements-dev.txt

# Install pre-commit hooks
pre-commit install
```

## 📝 Development Guidelines

### Code Style
- Use type hints for all functions
- Follow PEP 8 guidelines
- Run pre-commit hooks before committing
- Write descriptive docstrings

### Testing
- Write tests for new features
- Maintain or improve test coverage
- Run the test suite before submitting PRs:
```bash
pytest
```

### Documentation
- Update relevant documentation
- Follow the [Documentation Guidelines](docs/Guidelines.md)
- Include docstrings for public APIs
- Add examples for new features

## 🔄 Development Workflow

1. Create a feature branch:
```bash
git checkout -b feature/your-feature-name
```

2. Make your changes following our guidelines

3. Run tests and linting:
```bash
# Run tests
pytest

# Run type checking
mypy src/

# Run linting
flake8
```

4. Commit your changes:
```bash
git add .
git commit -m "feat: add new feature"
```

We follow [Conventional Commits](https://www.conventionalcommits.org/):
- `feat:` New features
- `fix:` Bug fixes
- `docs:` Documentation changes
- `refactor:` Code refactoring
- `test:` Adding/updating tests
- `chore:` Maintenance tasks

5. Push and create a Pull Request

## 🛠️ CLI Tools

The framework provides several CLI commands for development:
```bash
# Database
flask db upgrade
flask db revision --autogenerate -m "description"

# User Management
flask users create-admin

# Authentication
flask tokens create --email user@example.com
flask api-keys create --email user@example.com --name "Dev API"
```

## 🐛 Debugging

- Use `breakpoint()` in your code
- Configure VSCode debugging (see [Development Guide](docs/development/README.md))
- Check logs in `logs/` directory

## 📚 Project Structure

```
src/flask_structured_api/
├── api/          # API endpoints
├── core/         # Core framework
├── custom/       # Custom extensions
└── main.py       # Entry point
```

## ❓ Getting Help

- Review [documentation](docs/)
- Check [existing issues](https://github.com/julianfleck/flask-structured-api/issues)
- Open a new issue

## 📝 License

By contributing, you agree that your contributions will be licensed under the Apache License 2.0.

# Changelog

All notable changes to the Flask API Boilerplate will be documented in this file.

## [Unreleased]

## [0.2.0] - 2024-11-12

### Added
- Initial project structure and documentation
- Core API Features:
  - Flask API initialization with OpenAPI/Swagger UI support
  - Remote debugging support with debugpy
  - Root blueprint registration
  - Standardized API port configuration
  - Development server implementation (run.py)
  - Database connection and session management with SQLModel
  - Core authentication module with JWT support
  - Role-based access control implementation
  - AI service integration with validation and retries
  - Warning system with collector utility
  - Core exception handling system
  - Standardized API response models

### Infrastructure
- Docker setup and configuration
  - Development environment setup
  - Database environment configuration
  - Port standardization across Docker files

### Models & Responses
- Initial domain and request models
- Response models for authentication and items
- Core database model implementation with SQLModel
- Settings management with Pydantic


## [0.1.0] - 2024-11-11

- Initial repository setup
- Basic project structure

### Documentation Added
- Core documentation (`docs/README.md`):
  - Essential configuration guide
  - Environment variables reference
  - Project overview and structure
  - Resource links and getting help

- Architecture guidelines (`docs/architecture/README.md`):
  - System component diagram
  - Scaling considerations
  - Database design patterns
  - Service layer architecture

- API documentation (`docs/api/README.md`):
  - Versioning strategy
  - Standard response formats
  - Rate limiting specifications
  - Error handling patterns

- Development guide (`docs/development/README.md`):
  - Local setup instructions
  - Testing guidelines
  - Code style and conventions
  - Contribution workflow

- Getting started guide (`docs/getting-started/README.md`):
  - Quick start with Docker
  - Manual installation steps
  - Initial configuration
  - First API endpoint creation

- Deployment guide (`docs/deployment/README.md`):
  - Production deployment steps
  - Environment configuration
  - Docker deployment guide
  - Monitoring setup

### Implementation Guidelines
- Model-first architecture pattern with SQLModel and Pydantic
- Standardized error handling with semantic error codes
- Rate limiting implementation with Redis
- AI service integration patterns with provider abstraction
- Authentication flow using JWT tokens
- Health check implementation patterns
- API versioning strategy

### Project Structure
- Defined core project layout and component organization
- Documentation-driven development approach
- Type hints and validation patterns
- Testing structure and methodology
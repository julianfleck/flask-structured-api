# Changelog

All notable changes to the Flask API Boilerplate will be documented in this file.

# [Unreleased]

## [0.2.0] - 2024-11-12

### Added
- Authentication endpoints for user registration and login
- Database connection handling with retry mechanism
- SQLModel integration with Flask-Migrate
- Standardized API response format with success/error handling
- Custom exception handling for API errors
- Automated database backup system with configurable schedules
- Crontab generation script for automated backups
- Backup retention policy with daily/weekly/monthly options
- Development environment setup with debugpy support
- Proper environment-based dependency management in Docker
- Supervisor configuration for process management
- Debug logging for application startup and configuration
- Environment variable validation in settings
- `/v1/auth/me` endpoint for retrieving authenticated user information
- Login endpoint implementation with JWT token response
- Refresh token functionality in Auth service
- Token expiration configuration in settings
- Enhanced authentication documentation with rate limits and error codes
- Detailed authentication flow description
- Token refresh endpoint documentation
- Current user endpoint documentation
- Comprehensive authentication flow documentation with curl examples
- Token refresh mechanism documentation
- Bearer token usage examples
- Authentication error codes reference table
- Structured warning response format with ResponseWarning model
- Individual warning collection for unexpected request fields
- Graceful handling of multiple warnings in responses


### Changed
- Enhanced error responses to include status codes and error details
- Improved database initialization process with proper migration support
- Restructured Docker configuration for backup service
- Added backup volume management in docker-compose
- Modified Docker build process to support development/production environments
- Updated supervisor configuration for better log handling
- Standardized port configuration across development and production
- Improved environment variable handling in Docker setup
- Updated TokenResponse model to include bearer token type
- Standardized error handling in auth decorators
- Improved JWT token creation with proper expiration times
- Enhanced error messages for authentication failures
- Reorganized project structure:
  - Moved response models from `core/responses.py` to `models/responses/base.py`
  - Split exceptions into domain-specific modules under `core/exceptions/`
  - Organized AI-related models under `models/ai/`
  - Standardized imports across the codebase
  - Removed duplicate code in core module
- Standardized error handling with domain-specific error detail models
- Improved error response structure with consistent format
- Enhanced validation error details with field-level information
- Consolidated error models under `app/models/errors.py`
- Reorganized authentication documentation structure
- Improved token management section with expiration details
- Updated error response examples with actual codes from implementation
- Warning display format from string to structured object
- Warning collector to handle multiple warnings more effectively
- F-string formatting to .format() for consistent autoformatting
- BaseRequestModel validation to collect individual field warnings


### Fixed
- Database connection issues during application startup
- Error handling to return consistent JSON responses instead of HTML errors
- Syntax error in crontab generation script f-string formatting
- Debugpy installation in development environment
- Port binding issues in Docker configuration
- Environment variable interpolation in settings
- Process management in Docker containers
- Status code parameter in APIError instantiation
- Token validation error handling in require_auth decorator
- Missing get_user_by_id implementation in AuthService
- Inconsistent error response format in auth endpoints
- Error response status code mismatch in auth endpoints
- Standardized error response format for 401/403 responses
- APIError status field consistency in error handler
- Validation error status code (changed from 42 to 422)
- Error response format inconsistency in HTTP exception handler
- Error detail model inheritance structure
- Type validation for error response models
- Improved validation error response structure with required fields and detailed error information
- Warning collector only showing first warning in responses
- Inconsistent warning message formatting
- Extra field validation in request models


### Removed
- Deprecated `core/responses.py` (moved to `models/responses/base.py`)
- Deprecated `core/exceptions.py` (split into domain-specific modules)

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
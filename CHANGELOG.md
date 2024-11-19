# Changelog

All notable changes to the Flask API Boilerplate will be documented in this file.

# [Unreleased]

## [0.2.3] - 2024-11-19

### Fixed
- Automated database backup system with Docker integration
  - Daily backups with configurable retention policy
  - Backup compression support with gzip
  - CLI commands for backup management and listing
  - Initial backup on container startup
  - Backup volume persistence across container restarts
  - Backup cleanup with daily/weekly/monthly retention
- Storage session listing endpoint parameter validation
- Backup directory permissions in Docker containers
- Database connection handling during backup operations
- Environment variable consistency across containers

### Changed
- Improved backup system reliability with proper error handling
- Enhanced backup file naming with timestamps
- Standardized database credentials across services
- Optimized backup compression settings
- Improved backup logging with emojis for better visibility

### Security
- Secured database credentials in backup container
- Protected backup directory with proper permissions
- Isolated backup operations in dedicated container


## [0.2.2] - 2024-11-15

### Added
- Enhanced session pagination and filtering
  - Added entries_per_session parameter for detailed queries
  - Added metadata-based session filtering
  - Added pagination for session listings
  - Added detailed and simple session response models
  - Added session-specific warnings
- Comprehensive storage documentation update
  - Added clear introduction and use cases
  - Added practical AI model examples
  - Added detailed API reference
  - Added troubleshooting section
  - Added security considerations
  - Added best practices
  - Added future improvements roadmap
  - Added warning system documentation
- Comprehensive API request/response storage system
  - Automatic storage decorator with compression support
  - Session-based request grouping
  - Flexible metadata filtering
  - TTL-based storage expiration
  - Timezone-aware date filtering
- Storage query endpoints with pagination
  - /storage/query for direct data access
  - /storage/sessions for session management
  - /storage/sessions/query for detailed session data
- Storage management features
  - Automatic data compression for large payloads
  - TTL-based cleanup
  - Admin-only delete endpoint
- Warning system for storage optimization
  - Performance optimization hints
  - Non-critical issue reporting
  - Structured warning responses
- Comprehensive storage documentation
  - Setup guides and best practices
  - Query optimization tips
  - Session management guidelines

### Changed
- Improved session handling with granular control
- Enhanced documentation structure with progressive complexity
- Updated API reference with detailed parameters
- Standardized warning system documentation
- Enhanced response models to support storage metadata
- Improved session handling with automatic timeout
- Updated API documentation with storage endpoints
- Enhanced warning system to support storage-specific warnings

### Security
- Added role-based access for storage management
- Implemented user-scoped storage queries
- Added validation for storage operations

## [0.2.1] - 2024-11-13

### Added
- API key management system with secure token generation
- API key endpoints for creation, listing and revocation
- Maximum API keys per user limit
- Scoped API key support with customizable permissions
- API key model with hash-based storage
- Last used tracking for API keys
- Optional expiration for API keys
- API data storage system with request/response tracking
  - Storage query endpoint with filtering and pagination
  - Storage delete endpoint with admin access control
  - Automatic request/response storage decorator
  - Compressed data storage support
  - TTL-based storage expiration
  - Metadata filtering for stored data
- Endpoint normalization and validation

### Fixed
- Token refresh validation with proper secret key
- Token type validation in refresh flow
- Refresh token error handling with specific error codes
- JWT token validation in auth service

### Changed
- Enhanced token refresh mechanism to maintain refresh token
- Improved API key security with hash-based storage
- Standardized API key response format
- Added user ownership validation for API key operations

### Security
- Implemented secure API key generation using secrets module
- Added SHA-256 hashing for API key storage
- Restricted API key access to authenticated users only
- Added user validation for API key operations

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
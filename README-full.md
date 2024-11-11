
- [[Flask API Boilerplate/Fragments]]
- [[Flask API Boilerplate/Github-Readme]]
---

# Flask API Boilerplate with LLM Integration

A production-ready Flask API boilerplate using SQLModel, PostgreSQL, Redis, and LLM integrations. Built for developers who need a robust foundation for building AI-powered APIs while following best practices for production deployments.

## 1. Introduction

### Overview
This boilerplate provides a complete foundation for building modern APIs with AI capabilities, handling everything from database management to LLM integration patterns. It emphasizes clean architecture, type safety, and production readiness while maintaining developer productivity.

### Key Features
- 🏗️ **Model-First Architecture**
  - Clear separation of models (core/domain/requests/responses)
  - SQLModel for unified database models and validation
  - Type-safe database operations
- 🤖 **AI Integration**
  - Flexible LLM provider interface
  - Built-in response validation
  - Structured output parsing
  - Comprehensive error handling
- 🔐 **Security**
  - Role-based access control
  - JWT authentication
  - Request validation
  - Rate limiting
- 🛠️ **Developer Experience**
  - Clear project structure
  - Comprehensive CLI tools
  - Detailed documentation
  - Testing infrastructure
- 📦 **Production Ready**
  - Docker configuration
  - Monitoring setup
  - Deployment guides
  - Performance optimization

### Core Components

```mermaid
graph TD
    Client[Client] --> Nginx[Nginx Load Balancer]
    Nginx --> API1[API Instance 1]
    Nginx --> API2[API Instance 2]
    API1 --> AIService[AI Service Layer]
    API2 --> AIService
    AIService --> Cache[(Redis Cache)]
    AIService --> DB[(PostgreSQL)]
    
    subgraph "API Instance"
        Models[Domain Models] --> Services[Service Layer]
        Services --> Controllers[API Controllers]
        Models --> Validation[Request/Response Validation]
    end
```

### Tech Stack
- **Python 3.10+**: For type hints and modern features
- **Flask 2.3+**: Web framework
- **SQLModel**: Database ORM and validation
- **PostgreSQL**: Primary database
- **Redis**: Caching layer
- **Pydantic**: Data validation
- **pytest**: Testing framework
- **OpenAPI**: API documentation

### Prerequisites
- Python 3.10 or higher
- PostgreSQL 14 or higher
- Redis 6 or higher
- Docker and docker-compose (optional)

## 2. Quick Start

### Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/flask-api-boilerplate.git
cd flask-api-boilerplate
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

4. Set up environment:
```bash
cp .env.example .env
# Edit .env with your settings
```

Example `.env` configuration:
```env
# API Settings
FLASK_APP=app.main:create_app
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

# AI Provider (optional)
AI_PROVIDER=openai  # or 'azure', 'anthropic'
AI_API_KEY=your-api-key-here
```

### Running the API

#### Local Development
```bash
# Initialize database
flask db upgrade

# Create admin user
flask users create-admin

# Run development server
flask run --debug
```

#### Using Docker
```bash
# Build and start services
docker-compose up -d

# Run migrations
docker-compose exec api flask db upgrade

# Create admin user
docker-compose exec api flask users create-admin
```

### Your First Endpoint

Let's create a simple endpoint to verify the setup:

1. Create a new file `app/api/v1/endpoints/hello.py`:
```python
from flask import Blueprint
from app.core.responses import SuccessResponse
from datetime import datetime

hello_bp = Blueprint('hello', __name__)

@hello_bp.route('/hello', methods=['GET'])
def hello_world():
    """Basic endpoint example"""
    return SuccessResponse(
        message="Hello from Flask API Boilerplate!",
        data={
            "timestamp": datetime.utcnow(),
            "version": "1.0.0"
        }
    ).dict()
```

2. Register the blueprint in `app/api/v1/__init__.py`:
```python
from flask import Blueprint
from app.api.v1.endpoints.hello import hello_bp

api_v1 = Blueprint('api_v1', __name__, url_prefix='/api/v1')
api_v1.register_blueprint(hello_bp, url_prefix='/hello')
```

3. Test the endpoint:
```bash
curl http://localhost:5000/api/v1/hello
```

Expected response:
```json
{
    "success": true,
    "message": "Hello from Flask API Boilerplate!",
    "data": {
        "timestamp": "2024-11-11T12:00:00.000Z",
        "version": "1.0.0"
    }
}
```

### Health Check

The boilerplate includes a built-in health check endpoint:

```bash
curl http://localhost:5000/health
```

Response:
```json
{
    "status": "healthy",
    "checks": {
        "database": "ok",
        "redis": "ok",
        "ai_service": "ok"
    },
    "version": "1.0.0",
    "timestamp": "2024-11-11T12:00:00.000Z"
}
```

### What's Next?
- Learn about the [model-first architecture](#3-core-concepts)
- Set up [authentication](#32-authentication--authorization)
- Integrate with [AI services](#33-ai-integration)
- Explore [advanced features](#7-advanced-topics)

### 3.1 Model-First Architecture

The boilerplate follows a model-first approach with clear separation of concerns through different types of models. This provides type safety, validation, and clear data flow throughout the application.

#### Model Structure

```
app/models/
├── core/                      # Core functionality models
│   ├── base.py               # Base model classes
│   ├── auth.py               # Authentication models
│   └── ai.py                 # AI service base models
├── domain/                   # Business domain models
│   └── model.py             # Your domain models
├── requests/                 # API request models
│   └── model.py             # Request validation
├── responses/               # API response models
│   └── model.py            # Response formatting
└── ai/                     # AI-specific models
    ├── prompts/            # Prompt templates
    │   └── base.py         # Base prompt templates
    ├── validation/         # AI response validation
    │   └── base.py         # Validation schemas
    └── parser.py          # Output parsing utilities
```

#### Base Models

```python
from datetime import datetime
from typing import Optional
from sqlmodel import SQLModel, Field

class CoreModel(SQLModel):
    """Base model for all database models"""
    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(
        default_factory=datetime.utcnow,
        sa_column_kwargs={"onupdate": datetime.utcnow}
    )

# Base models for different concerns
class BaseRequestModel(SQLModel):
    """Base model for API requests"""
    class Config:
        extra = "forbid"  # Prevent additional properties

class BaseResponseModel(SQLModel):
    """Base model for API responses"""
    class Config:
        from_attributes = True

class BaseAIValidationModel(SQLModel):
    """Base model for AI response validation"""
    class Config:
        extra = "forbid"
        strict = True  # Strict type checking for AI responses
```

#### Model Types and Their Purpose

1. Domain Models:
```python
# app/models/domain/model.py
from sqlmodel import Field, Relationship
from app.models.core.base import CoreModel

class Item(CoreModel, table=True):
    """Example domain model"""
    name: str = Field(index=True)
    description: str
    properties: Dict[str, Any]
    user_id: int = Field(foreign_key="user.id")
    
    # Relationships
    user: "User" = Relationship(back_populates="items")
```

2. Request Models:
```python
# app/models/requests/model.py
from typing import Optional
from pydantic import Field
from app.models.core.base import BaseRequestModel

class CreateItemRequest(BaseRequestModel):
    """Example request validation model"""
    name: str = Field(..., min_length=3, max_length=100)
    description: str = Field(..., max_length=500)
    properties: Dict[str, Any] = Field(default_factory=dict)

class UpdateItemRequest(BaseRequestModel):
    """Example update request model"""
    name: Optional[str] = Field(None, min_length=3, max_length=100)
    description: Optional[str] = None
    properties: Optional[Dict[str, Any]] = None
```

3. AI Validation Models:
```python
# app/models/ai/validation/base.py
from typing import Dict
from pydantic import Field, validator
from app.models.core.base import BaseAIValidationModel

class AIGenerationResponse(BaseAIValidationModel):
    """Example AI response validation model"""
    content: str = Field(..., min_length=10)
    metadata: Dict[str, Any] = Field(...)
    confidence: float = Field(..., ge=0, le=1)
    
    @validator('metadata')
    def validate_metadata(cls, v):
        """Ensure required metadata fields"""
        required_fields = ['category', 'quality_score']
        if not all(field in v for field in required_fields):
            raise ValueError(f"Missing required metadata fields: {required_fields}")
        return v
```

4. Response Models:
```python
# app/models/responses/model.py
from typing import Optional, List
from app.models.core.base import BaseResponseModel

class ItemResponse(BaseResponseModel):
    """Example response model"""
    id: int
    name: str
    description: str
    properties: Dict[str, Any]
    created_at: datetime

class ItemListResponse(BaseResponseModel):
    """Example paginated response"""
    items: List[ItemResponse]
    total: int
    page: int
    size: int
    has_more: bool
```


[Previous section 3.1 remains as shown above]

### 3.2 Authentication & Authorization

The boilerplate provides a robust authentication system with role-based access control.

#### Core Authentication Models

```python
# app/models/core/auth.py
from enum import Enum
from typing import Optional
from sqlmodel import Field
from app.models.core.base import CoreModel

class UserRole(str, Enum):
    ADMIN = "admin"
    USER = "user"
    READONLY = "readonly"

class User(CoreModel, table=True):
    """Core user model"""
    email: str = Field(unique=True, index=True)
    hashed_password: str
    full_name: str
    role: UserRole = Field(default=UserRole.USER)
    is_active: bool = Field(default=True)
```

#### Authentication Request/Response Models

```python
# app/models/requests/auth.py
from pydantic import EmailStr, Field
from app.models.core.base import BaseRequestModel

class RegisterRequest(BaseRequestModel):
    """User registration request"""
    email: EmailStr
    password: str = Field(..., min_length=8)
    full_name: str = Field(..., min_length=2)

class LoginRequest(BaseRequestModel):
    """Login request"""
    email: EmailStr
    password: str

# app/models/responses/auth.py
from app.models.core.base import BaseResponseModel

class TokenResponse(BaseResponseModel):
    """Authentication token response"""
    access_token: str
    token_type: str = "bearer"
    expires_in: int

class UserResponse(BaseResponseModel):
    """User data response"""
    id: int
    email: str
    full_name: str
    role: str
    is_active: bool
```

### 3.3 AI Integration

The boilerplate provides a flexible system for integrating with AI services.

#### Core AI Models

```python
# app/models/core/ai.py
from typing import List, Optional, Any
from pydantic import BaseModel, Field

class AIMessage(BaseModel):
    """Standard AI message format"""
    role: str = Field(..., regex="^(system|user|assistant)$")
    content: str = Field(..., min_length=1)

class AICompletionRequest(BaseModel):
    """Standard completion request"""
    messages: List[AIMessage]
    temperature: float = Field(default=0.7, ge=0, le=2.0)
    max_tokens: Optional[int] = None
    response_schema: Optional[dict] = None

class AICompletionResponse(BaseModel):
    """Standard completion response"""
    content: str
    role: str = "assistant"
    finish_reason: str
    usage: dict
    warnings: List[str] = []
```

#### Base AI Service

```python
# app/core/ai/base.py
from typing import Protocol, Type, TypeVar, Optional
from pydantic import BaseModel

T = TypeVar('T', bound=BaseModel)

class AIProvider(Protocol):
    """Protocol for AI service providers"""
    async def complete(
        self,
        request: AICompletionRequest,
        response_model: Optional[Type[T]] = None
    ) -> T:
        """Generate completion"""
        ...

    async def validate_response(
        self,
        response: str,
        schema: dict
    ) -> bool:
        """Validate response against schema"""
        ...
```

#### Generic AI Service Implementation

```python
# app/core/ai/service.py
class AIService:
    def __init__(self, provider: AIProvider):
        self.provider = provider
        self.warning_collector = WarningCollector()

    async def complete_with_validation(
        self,
        request: AICompletionRequest,
        validation_model: Type[BaseModel]
    ) -> Tuple[Any, List[str]]:
        """Generate and validate completion"""
        try:
            # Generate completion
            response = await self.provider.complete(request)
            
            # Quality checks
            if response.usage.get('total_tokens', 0) > 1000:
                self.warning_collector.add_warning(
                    "High token usage detected",
                    "high_token_usage"
                )

            # Schema validation
            validated_data = validation_model.parse_raw(response.content)
            
            return validated_data, response.warnings
            
        except ValidationError as e:
            self.warning_collector.add_warning(
                "AI response failed validation",
                "validation_error"
            )
            raise AIResponseValidationError(
                "Response validation failed",
                validation_errors=e.errors()
            )
```

### 3.4 Error & Warning Management

#### Error Types

```python
# app/core/exceptions.py
class APIError(Exception):
    """Base API error"""
    def __init__(self, message: str, code: str = None, details: dict = None):
        self.message = message
        self.code = code or self.__class__.__name__
        self.details = details or {}

class ValidationError(APIError):
    """Data validation error"""
    def __init__(self, message: str, field: str = None):
        super().__init__(
            message=message,
            code="validation_error",
            details={"field": field}
        )

class AIServiceError(APIError):
    """AI service error"""
    def __init__(self, message: str, details: dict = None):
        super().__init__(
            message=message,
            code="ai_service_error",
            details=details
        )
```

#### Warning System

```python
# app/core/warnings.py
@dataclass
class Warning:
    """Warning message structure"""
    message: str
    code: str
    timestamp: datetime = field(default_factory=datetime.utcnow)
    severity: str = "warning"
    
    # Standard warning codes
    CODES: ClassVar[Dict[str, str]] = {
        "low_confidence": "AI model confidence below threshold",
        "high_token_usage": "High token usage detected",
        "validation_warning": "Non-critical validation issue",
        "rate_limit_warning": "Approaching rate limit",
        "performance_warning": "Performance degradation detected"
    }

class WarningCollector:
    """Warning collection utility"""
    def __init__(self):
        self.warnings: List[Warning] = []
    
    def add_warning(self, message: str, code: str):
        """Add new warning"""
        self.warnings.append(Warning(message=message, code=code))
    
    def get_warnings(self) -> List[Warning]:
        """Get collected warnings"""
        return self.warnings
```

### 3.5 Implementation Example: Recipe Generator

Now let's see how these components work together in a real-world example: an AI recipe generator.

This example demonstrates how to combine the core components to create a complete AI-powered feature.

#### Domain Model
```python
# EXAMPLE: app/models/domain/recipe.py
from sqlmodel import SQLModel, Field, Relationship
from typing import List
from app.models.core.base import CoreModel

class Recipe(CoreModel, table=True):
    """Example domain model for recipes"""
    title: str = Field(index=True)
    description: str
    ingredients: List[str]
    instructions: List[str]
    cooking_time: int
    difficulty: str
    user_id: int = Field(foreign_key="user.id")
    
    user: "User" = Relationship(back_populates="recipes")
```

#### Request/Response Models
```python
# EXAMPLE: app/models/requests/recipe.py
from typing import List, Optional
from pydantic import Field
from app.models.core.base import BaseRequestModel

class GenerateRecipeRequest(BaseRequestModel):
    """Example request model for recipe generation"""
    ingredients: List[str] = Field(..., min_items=1)
    dietary_restrictions: Optional[List[str]] = Field(default_factory=list)
    cuisine_type: Optional[str] = None
    cooking_time_max: Optional[int] = Field(None, gt=0)

# EXAMPLE: app/models/responses/recipe.py
from app.models.core.base import BaseResponseModel

class GeneratedRecipeResponse(BaseResponseModel):
    """Example response model for generated recipe"""
    recipe: Dict[str, Any]
    confidence_score: float
    warnings: List[str] = []
    metadata: Optional[dict] = None
```

#### AI Response Validation
```python
# EXAMPLE: app/models/ai/validation/recipe.py
from app.models.core.base import BaseAIValidationModel

class AIRecipeResponse(BaseAIValidationModel):
    """Example validation model for AI-generated recipe"""
    title: str = Field(..., min_length=3, max_length=100)
    ingredients: List[Dict[str, str]] = Field(..., min_items=1)
    instructions: List[Dict[str, str]] = Field(..., min_items=1)
    metadata: Dict[str, str] = Field(...)
    
    @validator('ingredients')
    def validate_ingredients(cls, v):
        """Validate ingredient structure"""
        for item in v:
            if not all(k in item for k in ['item', 'amount', 'unit']):
                raise ValueError("Each ingredient must have item, amount, and unit")
        return v
```

#### Prompt Template
```python
# EXAMPLE: app/models/ai/prompts/recipe.py
class RecipePromptTemplate(BaseModel):
    """Example prompt template for recipe generation"""
    system_prompt: str = """
    You are a professional chef specialized in creating recipes. 
    Generate detailed, clear recipes following these guidelines:
    - Use standard measurements
    - Include preparation steps
    - Consider dietary restrictions
    - Ensure ingredients are commonly available
    """
    
    @classmethod
    def generate_prompt(
        cls,
        ingredients: List[str],
        restrictions: List[str] = None,
        cuisine: str = None
    ) -> str:
        # Prompt generation logic
        ...
```

#### Service Implementation
```python
# EXAMPLE: app/services/recipe.py
class RecipeService:
    """Example service showing integration of all components"""
    def __init__(self, ai_service: AIService):
        self.ai_service = ai_service

    async def generate_recipe(
        self,
        request: GenerateRecipeRequest
    ) -> GeneratedRecipeResponse:
        # Create AI request
        ai_request = AICompletionRequest(
            messages=[
                AIMessage(
                    role="system",
                    content=RecipePromptTemplate.system_prompt
                ),
                AIMessage(
                    role="user",
                    content=RecipePromptTemplate.generate_prompt(
                        ingredients=request.ingredients,
                        restrictions=request.dietary_restrictions,
                        cuisine=request.cuisine_type
                    )
                )
            ]
        )
        
        # Generate and validate
        validated_recipe, warnings = await self.ai_service.complete_with_validation(
            request=ai_request,
            validation_model=AIRecipeResponse
        )
        
        # Return formatted response
        return GeneratedRecipeResponse(
            recipe=validated_recipe.dict(),
            warnings=warnings,
            metadata=validated_recipe.metadata
        )
```

#### API Endpoint
```python
# EXAMPLE: app/api/v1/endpoints/recipes.py
recipes_bp = Blueprint('recipes', __name__)

@recipes_bp.route('/generate', methods=['POST'])
@require_auth
async def generate_recipe():
    """Example endpoint demonstrating complete flow"""
    try:
        request_data = GenerateRecipeRequest(**request.json)
        recipe_service = RecipeService(ai_service=get_ai_service())
        result = await recipe_service.generate_recipe(request_data)
        
        return SuccessResponse(
            message="Recipe generated successfully",
            data=result.dict(),
            warnings=[asdict(w) for w in result.warnings]
        ).dict()
        
    except ValidationError as e:
        return ErrorResponse(
            message="Invalid request",
            errors=[e.dict()]
        ).dict()
```

This example demonstrates:
1. Proper separation of concerns using different model types
2. Integration with the core AI service
3. Implementation of request/response validation
4. Error and warning handling
5. Complete flow from request to response

The recipe generator is just one possible implementation using the boilerplate's architecture. You can follow the same patterns to implement other AI-powered features.



## 4. Development Guide

### 4.1 Project Structure

The boilerplate follows a modular structure designed for maintainability and scalability:

```
flask-api-boilerplate/
├── app/                      # Application package
│   ├── __init__.py          # App factory
│   ├── api/                 # API endpoints
│   │   ├── __init__.py
│   │   └── v1/             # API version 1
│   │       ├── __init__.py
│   │       └── endpoints/  # Route handlers by domain
│   ├── core/               # Core functionality
│   │   ├── __init__.py
│   │   ├── config.py      # Configuration management
│   │   ├── db.py         # Database setup
│   │   ├── security.py   # Security utilities
│   │   └── ai/          # AI service components
│   ├── models/           # All models (as described in section 3)
│   ├── services/         # Business logic layer
│   └── tasks/           # Background tasks
├── tests/               # Test suite
├── migrations/         # Database migrations
├── scripts/           # Utility scripts
└── docker/           # Docker configurations
```

### 4.2 Creating New Features

Let's walk through the process of adding a new feature to the API.

#### 1. Define Models

Start by defining your models in the appropriate directories:

```python
# app/models/domain/document.py
from app.models.core.base import CoreModel
from sqlmodel import Field

class Document(CoreModel, table=True):
    """Example: Adding a new document feature"""
    title: str = Field(index=True)
    content: str
    status: str = Field(default="draft")
    user_id: int = Field(foreign_key="user.id")
```

```python
# app/models/requests/document.py
from app.models.core.base import BaseRequestModel
from pydantic import Field

class CreateDocumentRequest(BaseRequestModel):
    title: str = Field(..., min_length=3)
    content: str = Field(..., min_length=10)

class UpdateDocumentRequest(BaseRequestModel):
    title: Optional[str] = Field(None, min_length=3)
    content: Optional[str] = None
    status: Optional[str] = Field(None, regex="^(draft|published)$")
```

```python
# app/models/responses/document.py
from app.models.core.base import BaseResponseModel

class DocumentResponse(BaseResponseModel):
    id: int
    title: str
    content: str
    status: str
    created_at: datetime
    updated_at: datetime
```

#### 2. Create Service Layer

Implement business logic in the service layer:

```python
# app/services/document.py
from app.models.domain.document import Document
from app.models.requests.document import CreateDocumentRequest
from app.core.exceptions import NotFoundError
from sqlmodel import Session, select

class DocumentService:
    @staticmethod
    async def create_document(
        session: Session,
        request: CreateDocumentRequest,
        user_id: int
    ) -> Document:
        document = Document(
            **request.dict(),
            user_id=user_id
        )
        session.add(document)
        session.commit()
        session.refresh(document)
        return document

    @staticmethod
    async def get_document(
        session: Session,
        document_id: int,
        user_id: int
    ) -> Document:
        document = session.get(Document, document_id)
        if not document or document.user_id != user_id:
            raise NotFoundError("Document not found")
        return document
```

#### 3. Implement API Endpoints

Add your API endpoints:

```python
# app/api/v1/endpoints/documents.py
from flask import Blueprint
from app.core.auth import require_auth
from app.services.document import DocumentService
from app.models.requests.document import CreateDocumentRequest
from app.models.responses.document import DocumentResponse
from app.core.responses import SuccessResponse

documents_bp = Blueprint('documents', __name__)

@documents_bp.route('/', methods=['POST'])
@require_auth
async def create_document():
    """Create new document"""
    try:
        request_data = CreateDocumentRequest(**request.json)
        document = await DocumentService.create_document(
            session=get_db(),
            request=request_data,
            user_id=g.current_user.id
        )
        return SuccessResponse(
            message="Document created",
            data=DocumentResponse.from_orm(document)
        ).dict()
    except ValidationError as e:
        return ErrorResponse(
            message="Invalid request",
            errors=e.errors()
        ).dict()
```

#### 4. Add Tests

Create tests for your new feature:

```python
# tests/services/test_document.py
import pytest
from app.services.document import DocumentService
from app.models.requests.document import CreateDocumentRequest

@pytest.mark.asyncio
async def test_create_document(db_session):
    """Test document creation"""
    request = CreateDocumentRequest(
        title="Test Document",
        content="Test content"
    )
    
    document = await DocumentService.create_document(
        session=db_session,
        request=request,
        user_id=1
    )
    
    assert document.title == "Test Document"
    assert document.content == "Test content"
    assert document.status == "draft"
```

```python
# tests/api/test_documents.py
async def test_create_document_endpoint(client, auth_headers):
    """Test document creation endpoint"""
    response = await client.post(
        "/api/v1/documents",
        headers=auth_headers,
        json={
            "title": "Test Document",
            "content": "Test content"
        }
    )
    
    assert response.status_code == 200
    assert response.json["data"]["title"] == "Test Document"
```

### 4.3 Development Workflow

#### Local Development

1. Create your virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # Linux/macOS
# or
venv\Scripts\activate     # Windows
```

2. Install development dependencies:
```bash
pip install -r requirements-dev.txt
```

3. Set up pre-commit hooks:
```bash
pre-commit install
```

4. Start development server:
```bash
# Start dependencies
docker-compose up -d db redis

# Run development server
flask run --debug
```

5. Run tests:
```bash
# Run all tests
pytest

# Run specific test file
pytest tests/services/test_document.py

# Run with coverage
pytest --cov=app
```

#### Code Style

The project uses:
- Black for code formatting
- isort for import sorting
- flake8 for linting
- mypy for type checking

Run all checks:
```bash
# Format code
black app tests

# Sort imports
isort app tests

# Run linting
flake8 app tests

# Run type checking
mypy app
```

#### Database Migrations

When modifying models:

```bash
# Create migration
flask db migrate -m "Add document model"

# Review migration file in migrations/versions/

# Apply migration
flask db upgrade

# Rollback if needed
flask db downgrade
```

This structure provides:
1. Clear organization of code
2. Consistent patterns for new features
3. Comprehensive testing approach
4. Maintainable development workflow

## 5. CLI Tools

The boilerplate provides a comprehensive set of CLI commands for common tasks. All commands are accessible via the `flask` command-line interface.

### 5.1 User Management

```python
# app/cli/users.py
import click
from flask.cli import with_appcontext
from app.models.core.auth import UserRole
from app.services.auth import AuthService

@click.group()
def users():
    """User management commands"""
    pass

@users.command()
@click.option('--email', prompt=True)
@click.option('--password', prompt=True, hide_input=True)
@click.option('--full-name', prompt=True)
@click.option('--role', type=click.Choice(['admin', 'user', 'readonly']), default='user')
@with_appcontext
def create(email: str, password: str, full_name: str, role: str):
    """Create a new user"""
    user = AuthService.create_user(
        email=email,
        password=password,
        full_name=full_name,
        role=UserRole(role)
    )
    click.echo(f"Created user: {user.email} with role: {user.role}")

@users.command()
@click.argument('email')
@click.option('--role', type=click.Choice(['admin', 'user', 'readonly']), required=True)
@with_appcontext
def change_role(email: str, role: str):
    """Change user role"""
    user = AuthService.update_role(email=email, role=UserRole(role))
    click.echo(f"Updated role for {user.email} to {role}")
```

Usage:
```bash
# Create new user
flask users create

# Create admin user
flask users create --role admin

# Change user role
flask users change-role user@example.com --role admin

# List all users
flask users list
```

### 5.2 Database Operations

```python
# app/cli/db.py
@click.group()
def db():
    """Database management commands"""
    pass

@db.command()
@click.option('--force', is_flag=True, help='Force reset without confirmation')
@with_appcontext
def reset(force: bool):
    """Reset database (DESTRUCTIVE)"""
    if force or click.confirm('This will delete all data. Continue?'):
        db.drop_all()
        db.create_all()
        click.echo("Database reset complete")

@db.command()
@click.argument('name')
@with_appcontext
def seed(name: str):
    """Seed database with test data"""
    try:
        seeder = get_seeder(name)
        seeder.run()
        click.echo(f"Seeded database with {name} data")
    except ValueError as e:
        click.echo(f"Error: {str(e)}", err=True)
```

Usage:
```bash
# Create new migration
flask db migrate -m "Add new table"

# Apply migrations
flask db upgrade

# Downgrade one version
flask db downgrade

# Reset database
flask db reset --force

# Seed test data
flask db seed test_data
```

### 5.3 AI Service Management

```python
# app/cli/ai.py
@click.group()
def ai():
    """AI service management"""
    pass

@ai.command()
@click.option('--provider', default='default')
@with_appcontext
def test_connection(provider: str):
    """Test AI provider connection"""
    try:
        result = AIService(provider).test_connection()
        click.echo(f"Connection successful: {result}")
    except Exception as e:
        click.echo(f"Connection failed: {str(e)}", err=True)

@ai.command()
@with_appcontext
def show_stats():
    """Show AI usage statistics"""
    stats = AIService.get_usage_stats()
    click.echo("\nAI Usage Statistics:")
    click.echo(f"Total requests: {stats['total_requests']}")
    click.echo(f"Total tokens: {stats['total_tokens']}")
    click.echo(f"Average tokens per request: {stats['avg_tokens']}")
```

Usage:
```bash
# Test AI provider connection
flask ai test-connection

# Clear AI cache
flask ai clear-cache

# Show AI usage statistics
flask ai show-stats
```

### 5.4 Development Tools

```python
# app/cli/dev.py
@click.group()
def dev():
    """Development utilities"""
    pass

@dev.command()
def lint():
    """Run code linting"""
    click.echo("Running black...")
    subprocess.run(["black", "app", "tests"])
    click.echo("Running isort...")
    subprocess.run(["isort", "app", "tests"])
    click.echo("Running flake8...")
    subprocess.run(["flake8", "app", "tests"])

@dev.command()
@click.option('--port', default=8000)
def swagger(port: int):
    """Start Swagger UI server"""
    click.echo(f"Starting Swagger UI at http://localhost:{port}")
    app.config['SWAGGER_URL'] = f"http://localhost:{port}"
    swagger.run(port=port)
```

Usage:
```bash
# Format and lint code
flask dev lint

# Start Swagger UI
flask dev swagger

# Generate OpenAPI spec
flask dev openapi
```

### 5.5 Deployment Tools

```python
# app/cli/deploy.py
@click.group()
def deploy():
    """Deployment management"""
    pass

@deploy.command()
@click.argument('target')
@click.option('--migrate/--no-migrate', default=True)
def prepare(target: str, migrate: bool):
    """Prepare deployment to target environment"""
    click.echo(f"Preparing deployment to {target}")
    if migrate:
        subprocess.run(["flask", "db", "upgrade"])
    
    # Run environment-specific checks
    checks = DeploymentChecker(target).run_checks()
    for check in checks:
        click.echo(f"✓ {check}")

@deploy.command()
def healthcheck():
    """Run deployment health checks"""
    results = HealthChecker().run_all()
    for service, status in results.items():
        click.echo(f"{service}: {'✓' if status else '✗'}")
```

Usage:
```bash
# Prepare deployment
flask deploy prepare production

# Run health checks
flask deploy healthcheck
```

### 5.6 Creating Custom Commands

Add your own commands by creating a new CLI group:

```python
# app/cli/custom.py
import click
from flask.cli import with_appcontext

@click.group()
def custom():
    """Custom management commands"""
    pass

@custom.command()
@click.argument('name')
@click.option('--flag', is_flag=True)
@with_appcontext
def command(name: str, flag: bool):
    """Custom command description"""
    click.echo(f"Running custom command: {name}")
    if flag:
        click.echo("Flag is set")

# Register in app/__init__.py
app.cli.add_command(custom)
```

Usage:
```bash
# Run custom command
flask custom command my-command --flag
```

All commands provide:
1. Clear documentation via `--help`
2. Input validation
3. Error handling
4. Logging
5. Environment context

## 6. Deployment

### 6.1 Basic Deployment

#### Environment Configuration

Create a production environment file:

```env
# .env.production
FLASK_ENV=production
FLASK_APP=app.main:create_app
DEBUG=false
API_HOST=0.0.0.0
API_PORT=5000

# Database
DATABASE_URL=postgresql://user:password@db:5432/app_db
DB_POOL_SIZE=20
DB_MAX_OVERFLOW=10
DB_POOL_TIMEOUT=30

# Redis
REDIS_URL=redis://redis:6379/0
REDIS_MAX_CONNECTIONS=20

# Security
SECRET_KEY=your-production-secret-key
JWT_SECRET_KEY=your-jwt-secret
ALLOWED_HOSTS=api.yourdomain.com,api-backup.yourdomain.com

# AI Service
AI_PROVIDER=openai
AI_API_KEY=your-production-api-key
AI_MODEL=gpt-4
AI_TIMEOUT=30

# Rate Limiting
RATE_LIMIT_DEFAULT=100
RATE_LIMIT_AUTHENTICATED=1000
RATE_LIMIT_WINDOW=3600
```

#### Docker Setup

```yaml
# docker-compose.prod.yml
version: '3.8'

services:
  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/nginx.conf:ro
      - ./nginx/conf.d:/etc/nginx/conf.d:ro
      - ./certs:/etc/nginx/certs:ro
    depends_on:
      - api
    networks:
      - app_network

  api:
    build: 
      context: .
      dockerfile: docker/Dockerfile.prod
    expose:
      - "5000"
    env_file: .env.production
    depends_on:
      - db
      - redis
    deploy:
      replicas: 3
      restart_policy:
        condition: on-failure
        max_attempts: 3
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:5000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
    networks:
      - app_network

  db:
    image: postgres:15-alpine
    volumes:
      - postgres_data:/var/lib/postgresql/data
    environment:
      POSTGRES_USER: ${DB_USER}
      POSTGRES_PASSWORD: ${DB_PASSWORD}
      POSTGRES_DB: ${DB_NAME}
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ${DB_USER}"]
      interval: 10s
      timeout: 5s
      retries: 5
    networks:
      - app_network

  redis:
    image: redis:7-alpine
    volumes:
      - redis_data:/data
    command: redis-server --appendonly yes
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 5s
      retries: 5
    networks:
      - app_network

volumes:
  postgres_data:
  redis_data:

networks:
  app_network:
    driver: bridge
```

### 6.2 Production Setup

#### Nginx Configuration

```nginx
# nginx/nginx.conf
worker_processes auto;
worker_rlimit_nofile 65535;

events {
    worker_connections 65535;
    multi_accept on;
    use epoll;
}

http {
    charset utf-8;
    sendfile on;
    tcp_nopush on;
    tcp_nodelay on;
    server_tokens off;
    log_not_found off;
    types_hash_max_size 2048;
    client_max_body_size 16M;

    # MIME
    include mime.types;
    default_type application/octet-stream;

    # Logging
    access_log /var/log/nginx/access.log combined buffer=512k flush=1m;
    error_log /var/log/nginx/error.log warn;

    # Rate limiting
    limit_req_zone $binary_remote_addr zone=api_limit:10m rate=10r/s;
    limit_req_status 429;

    # SSL
    ssl_session_timeout 1d;
    ssl_session_cache shared:SSL:50m;
    ssl_session_tickets off;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256;
    ssl_prefer_server_ciphers off;

    # Load configs
    include /etc/nginx/conf.d/*.conf;
}
```

```nginx
# nginx/conf.d/api.conf
upstream api_servers {
    least_conn;  # Load balancing method
    server api:5000;
    keepalive 32;
}

server {
    listen 80;
    listen [::]:80;
    server_name api.yourdomain.com;
    
    # Redirect HTTP to HTTPS
    location / {
        return 301 https://$server_name$request_uri;
    }
}

server {
    listen 443 ssl http2;
    listen [::]:443 ssl http2;
    server_name api.yourdomain.com;

    # SSL
    ssl_certificate /etc/nginx/certs/fullchain.pem;
    ssl_certificate_key /etc/nginx/certs/privkey.pem;

    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header Referrer-Policy "no-referrer-when-downgrade" always;
    add_header Content-Security-Policy "default-src 'self' http: https: data: blob: 'unsafe-inline'" always;
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;

    # API endpoints
    location /api/ {
        # Rate limiting
        limit_req zone=api_limit burst=20 nodelay;

        # Proxy headers
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # Proxy timeouts
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;

        # Proxy to Flask app
        proxy_pass http://api_servers;
        proxy_redirect off;
    }

    # Health check endpoint
    location /health {
        proxy_pass http://api_servers/health;
        access_log off;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### 6.3 Monitoring & Maintenance

#### Health Checks

```python
# app/core/health.py
from dataclasses import dataclass
from typing import Dict, Any
from redis import Redis
from sqlalchemy import text
from app.core.db import engine
from app.core.ai import AIService

@dataclass
class HealthStatus:
    status: str
    details: Dict[str, Any]
    
    @property
    def is_healthy(self) -> bool:
        return self.status == "healthy"

class HealthChecker:
    def check_database(self) -> bool:
        try:
            with engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            return True
        except Exception:
            return False

    def check_redis(self) -> bool:
        try:
            redis = Redis.from_url(settings.REDIS_URL)
            return redis.ping()
        except Exception:
            return False

    def check_ai_service(self) -> bool:
        try:
            return AIService().test_connection()
        except Exception:
            return False

    def get_status(self) -> HealthStatus:
        db_healthy = self.check_database()
        redis_healthy = self.check_redis()
        ai_healthy = self.check_ai_service()
        
        all_healthy = all([db_healthy, redis_healthy, ai_healthy])
        
        return HealthStatus(
            status="healthy" if all_healthy else "unhealthy",
            details={
                "database": "healthy" if db_healthy else "unhealthy",
                "redis": "healthy" if redis_healthy else "unhealthy",
                "ai_service": "healthy" if ai_healthy else "unhealthy",
                "version": settings.API_VERSION,
                "environment": settings.ENVIRONMENT
            }
        )
```

#### Metrics Collection

```python
# app/core/metrics.py
from prometheus_client import Counter, Histogram, Info
from functools import wraps
import time

# Metrics
REQUEST_COUNT = Counter(
    'request_total',
    'Total request count',
    ['method', 'endpoint', 'status']
)

REQUEST_LATENCY = Histogram(
    'request_latency_seconds',
    'Request latency',
    ['method', 'endpoint']
)

AI_REQUEST_COUNT = Counter(
    'ai_request_total',
    'Total AI request count',
    ['provider', 'model', 'status']
)

AI_TOKEN_COUNT = Counter(
    'ai_token_total',
    'Total AI tokens used',
    ['provider', 'model']
)

# Decorators
def track_request_metrics():
    def decorator(f):
        @wraps(f)
        def wrapped(*args, **kwargs):
            start_time = time.time()
            try:
                response = f(*args, **kwargs)
                status = response.status_code
            except Exception as e:
                status = 500
                raise e
            finally:
                REQUEST_COUNT.labels(
                    method=request.method,
                    endpoint=request.endpoint,
                    status=status
                ).inc()
                
                REQUEST_LATENCY.labels(
                    method=request.method,
                    endpoint=request.endpoint
                ).observe(time.time() - start_time)
            
            return response
        return wrapped
    return decorator

def track_ai_metrics():
    def decorator(f):
        @wraps(f)
        async def wrapped(*args, **kwargs):
            try:
                response = await f(*args, **kwargs)
                AI_REQUEST_COUNT.labels(
                    provider=kwargs.get('provider', 'default'),
                    model=kwargs.get('model', 'default'),
                    status='success'
                ).inc()
                
                if hasattr(response, 'usage'):
                    AI_TOKEN_COUNT.labels(
                        provider=kwargs.get('provider', 'default'),
                        model=kwargs.get('model', 'default')
                    ).inc(response.usage.get('total_tokens', 0))
                
                return response
            except Exception as e:
                AI_REQUEST_COUNT.labels(
                    provider=kwargs.get('provider', 'default'),
                    model=kwargs.get('model', 'default'),
                    status='error'
                ).inc()
                raise e
        return wrapped
    return decorator
```

#### Log Management

```python
# app/core/logging.py
import logging
import json
from datetime import datetime
from pythonjsonlogger import jsonlogger

class CustomJsonFormatter(jsonlogger.JsonFormatter):
    def add_fields(self, log_record, record, message_dict):
        super(CustomJsonFormatter, self).add_fields(log_record, record, message_dict)
        log_record['timestamp'] = datetime.utcnow().isoformat()
        log_record['level'] = record.levelname
        log_record['environment'] = settings.ENVIRONMENT

def setup_logging():
    logger = logging.getLogger()
    handler = logging.StreamHandler()
    formatter = CustomJsonFormatter(
        '%(timestamp)s %(level)s %(name)s %(message)s'
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(settings.LOG_LEVEL)

    # Add request ID to all logs within a request
    @app.before_request
    def before_request():
        g.request_id = request.headers.get('X-Request-ID') or str(uuid.uuid4())
        
    # Log all requests
    @app.after_request
    def after_request(response):
        logger.info(
            'Request processed',
            extra={
                'request_id': g.request_id,
                'method': request.method,
                'path': request.path,
                'status': response.status_code,
                'duration': g.get('request_duration'),
                'ip': request.remote_addr
            }
        )
        return response
```

### 6.4 Deployment Commands

```bash
# Build and deploy
docker-compose -f docker-compose.prod.yml build
docker-compose -f docker-compose.prod.yml up -d

# Scale services
docker-compose -f docker-compose.prod.yml up --scale api=3

# Monitor logs
docker-compose -f docker-compose.prod.yml logs -f

# Check service status
docker-compose -f docker-compose.prod.yml ps

# Deploy new version
./scripts/deploy.sh production
```

This provides:
1. Complete production environment setup
2. Secure Nginx configuration
3. Health monitoring
4. Metrics collection
5. Structured logging
6. Deployment automation

## 7. Advanced Topics

### 7.1 Background Tasks

#### Celery Configuration

```python
# app/core/tasks/config.py
from celery import Celery
from app.core.config import settings

celery_app = Celery(
    'tasks',
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
    include=['app.tasks']
)

celery_app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
    task_track_started=True,
    task_time_limit=3600,  # 1 hour
    worker_prefetch_multiplier=1,
    worker_concurrency=settings.CELERY_WORKERS
)
```

#### Task Definition

```python
# app/tasks/ai.py
from app.core.tasks.config import celery_app
from app.core.ai import AIService
from app.models.ai.validation import AIResponseValidation

@celery_app.task(
    bind=True,
    name='tasks.generate_ai_content',
    max_retries=3,
    soft_time_limit=300
)
def generate_ai_content(self, prompt: str, validation_schema: dict):
    """Background task for AI content generation"""
    try:
        service = AIService()
        response = service.complete_with_validation(
            prompt=prompt,
            validation_schema=validation_schema
        )
        return response.dict()
    except Exception as e:
        self.retry(exc=e, countdown=60)  # Retry after 1 minute

# Usage in API endpoint
@router.post('/generate-async')
async def generate_async():
    task = generate_ai_content.delay(
        prompt=request.json['prompt'],
        validation_schema=MySchema.schema()
    )
    return {'task_id': task.id}
```

### 7.2 Caching

#### Advanced Caching Strategies

```python
# app/core/cache.py
from functools import wraps
from typing import Optional, Callable
import hashlib
import json
from redis import Redis
from app.core.config import settings

class CacheManager:
    def __init__(self):
        self.redis = Redis.from_url(settings.REDIS_URL)
        self.default_ttl = 3600  # 1 hour

    def build_key(self, prefix: str, *args, **kwargs) -> str:
        """Build cache key from arguments"""
        key_parts = [prefix]
        if args:
            key_parts.extend([str(arg) for arg in args])
        if kwargs:
            key_parts.extend([f"{k}:{v}" for k, v in sorted(kwargs.items())])
        
        key_string = ":".join(key_parts)
        return f"cache:{hashlib.md5(key_string.encode()).hexdigest()}"

    async def get_or_set(
        self,
        key: str,
        func: Callable,
        ttl: Optional[int] = None,
        **kwargs
    ) -> Any:
        """Get from cache or compute and store"""
        cached = self.redis.get(key)
        if cached:
            return json.loads(cached)

        value = await func(**kwargs)
        self.redis.setex(
            key,
            ttl or self.default_ttl,
            json.dumps(value)
        )
        return value

    def invalidate_pattern(self, pattern: str):
        """Invalidate all keys matching pattern"""
        for key in self.redis.scan_iter(f"cache:{pattern}*"):
            self.redis.delete(key)

# Decorator for caching
def cache_response(
    prefix: str,
    ttl: Optional[int] = None,
    vary_on: Optional[List[str]] = None
):
    def decorator(func):
        @wraps(func)
        async def wrapped(*args, **kwargs):
            cache_mgr = CacheManager()
            
            # Build cache key including variation parameters
            vary_kwargs = {}
            if vary_on:
                vary_kwargs.update({
                    k: request.args.get(k)
                    for k in vary_on if k in request.args
                })
            
            cache_key = cache_mgr.build_key(prefix, **vary_kwargs)
            
            return await cache_mgr.get_or_set(
                key=cache_key,
                func=func,
                ttl=ttl,
                **kwargs
            )
        return wrapped
    return decorator
```

### 7.3 Advanced AI Features

#### Streaming Responses

```python
# app/core/ai/streaming.py
from typing import AsyncGenerator
from app.core.ai import AIService
from flask import Response, stream_with_context

class StreamingAIService(AIService):
    async def stream_completion(
        self,
        prompt: str,
        chunk_size: int = 100
    ) -> AsyncGenerator[str, None]:
        """Stream AI completion response"""
        async for chunk in self.provider.stream(prompt):
            yield chunk

# Usage in endpoint
@router.get('/stream')
async def stream_response():
    service = StreamingAIService()
    return Response(
        stream_with_context(service.stream_completion(
            prompt=request.args.get('prompt')
        )),
        mimetype='text/event-stream'
    )
```

#### Parallel Processing

```python
# app/core/ai/parallel.py
import asyncio
from typing import List
from app.core.ai import AIService

class ParallelAIService(AIService):
    async def batch_complete(
        self,
        prompts: List[str],
        max_concurrent: int = 5
    ) -> List[dict]:
        """Process multiple prompts in parallel"""
        semaphore = asyncio.Semaphore(max_concurrent)
        
        async def process_single(prompt: str) -> dict:
            async with semaphore:
                return await self.complete(prompt)
        
        tasks = [
            asyncio.create_task(process_single(prompt))
            for prompt in prompts
        ]
        
        return await asyncio.gather(*tasks)
```

### 7.4 Rate Limiting

#### Advanced Rate Limiting

```python
# app/core/rate_limit.py
from dataclasses import dataclass
from datetime import datetime
from typing import Optional
from redis import Redis

@dataclass
class RateLimit:
    key: str
    limit: int
    window: int
    remaining: int
    reset: datetime

class RateLimiter:
    def __init__(self, redis: Redis):
        self.redis = redis

    async def check_rate_limit(
        self,
        key: str,
        limit: int,
        window: int
    ) -> RateLimit:
        """Check rate limit for key"""
        pipeline = self.redis.pipeline()
        now = datetime.utcnow()
        
        # Clean old entries
        pipeline.zremrangebyscore(
            key,
            0,
            (now - timedelta(seconds=window)).timestamp()
        )
        
        # Add current request
        pipeline.zadd(key, {str(now.timestamp()): now.timestamp()})
        
        # Get request count
        pipeline.zcard(key)
        
        # Set expiry
        pipeline.expire(key, window)
        
        _, _, request_count, _ = pipeline.execute()
        
        return RateLimit(
            key=key,
            limit=limit,
            window=window,
            remaining=max(0, limit - request_count),
            reset=now + timedelta(seconds=window)
        )

# Usage in decorator
def rate_limit(
    limit: int,
    window: int = 3600,
    key_func: Optional[Callable] = None
):
    def decorator(f):
        @wraps(f)
        async def wrapped(*args, **kwargs):
            limiter = RateLimiter(redis=get_redis())
            
            # Get rate limit key
            if key_func:
                key = f"rate_limit:{key_func()}"
            else:
                key = f"rate_limit:{request.remote_addr}:{request.endpoint}"
            
            rate_limit = await limiter.check_rate_limit(
                key=key,
                limit=limit,
                window=window
            )
            
            # Set rate limit headers
            response = await f(*args, **kwargs)
            response.headers.update({
                'X-RateLimit-Limit': str(rate_limit.limit),
                'X-RateLimit-Remaining': str(rate_limit.remaining),
                'X-RateLimit-Reset': str(int(rate_limit.reset.timestamp()))
            })
            
            if rate_limit.remaining <= 0:
                raise TooManyRequests(
                    "Rate limit exceeded",
                    reset_time=rate_limit.reset
                )
            
            return response
        return wrapped
    return decorator
```

### 7.5 Advanced Testing

#### AI Service Mocking

```python
# tests/mocks/ai.py
from typing import Optional, Dict
from app.core.ai import AIProvider

class MockAIProvider(AIProvider):
    def __init__(self, responses: Optional[Dict[str, str]] = None):
        self.responses = responses or {}
        self.calls = []

    async def complete(self, prompt: str, **kwargs) -> str:
        self.calls.append({
            'prompt': prompt,
            'kwargs': kwargs
        })
        return self.responses.get(prompt, "Mock response")

    def assert_called_with(self, prompt: str):
        assert any(
            call['prompt'] == prompt
            for call in self.calls
        ), f"Provider was never called with prompt: {prompt}"

# Usage in tests
async def test_ai_generation(mocker):
    mock_provider = MockAIProvider({
        "test prompt": "Expected response"
    })
    
    service = AIService(provider=mock_provider)
    result = await service.complete("test prompt")
    
    mock_provider.assert_called_with("test prompt")
    assert result == "Expected response"
```


## 8. API Documentation

### 8.1 OpenAPI Integration

#### Basic Setup

```python
# app/core/openapi.py
from flask_openapi3 import OpenAPI, Info, Tag
from app.core.config import settings

info = Info(
    title=settings.API_TITLE,
    version=settings.API_VERSION,
    description="""
    API documentation for Flask Boilerplate.
    
    ## Features
    * Authentication using JWT
    * Role-based access control
    * AI-powered endpoints
    * Rate limiting
    * Request validation
    
    ## Authentication
    All protected endpoints require a Bearer token:
    ```
    Authorization: Bearer <your_token>
    ```
    """
)

# Tags for API grouping
tags = [
    Tag(name="auth", description="Authentication operations"),
    Tag(name="ai", description="AI-powered operations"),
    Tag(name="users", description="User management"),
]

app = OpenAPI(
    __name__,
    info=info,
    tags=tags,
    servers=[
        {"url": "https://api.yourdomain.com/v1", "description": "Production"},
        {"url": "http://localhost:5000/v1", "description": "Local development"}
    ]
)
```

#### Documentation Models

```python
# app/models/docs.py
from pydantic import BaseModel, Field
from typing import List, Optional

class ErrorResponse(BaseModel):
    """Standard error response"""
    message: str = Field(..., description="Error message")
    code: str = Field(..., description="Error code")
    details: Optional[dict] = Field(None, description="Additional error details")

class PaginationParams(BaseModel):
    """Standard pagination parameters"""
    page: Optional[int] = Field(1, description="Page number", ge=1)
    size: Optional[int] = Field(10, description="Items per page", ge=1, le=100)
    sort: Optional[str] = Field(None, description="Sort field")
    order: Optional[str] = Field(None, description="Sort order (asc/desc)")

class APIResponse(BaseModel):
    """Standard API response wrapper"""
    success: bool = Field(..., description="Operation success status")
    message: Optional[str] = Field(None, description="Response message")
    data: Optional[dict] = Field(None, description="Response data")
    warnings: Optional[List[str]] = Field(None, description="Warning messages")
```

#### Endpoint Documentation

```python
# app/api/v1/endpoints/ai.py
from flask_openapi3 import APIBlueprint
from app.models.requests.ai import GenerationRequest
from app.models.responses.ai import GenerationResponse
from app.models.docs import ErrorResponse

ai_bp = APIBlueprint(
    'ai',
    __name__,
    url_prefix='/ai',
    abp_tags=['ai'],
    abp_security=[{"bearerAuth": []}]
)

@ai_bp.post(
    '/generate',
    responses={
        "200": GenerationResponse,
        "400": ErrorResponse,
        "401": ErrorResponse,
        "429": ErrorResponse
    },
    description="""
    Generate content using AI.
    
    This endpoint allows you to generate content using various AI models.
    The response is validated against a schema to ensure quality.
    
    ## Rate Limits
    * Free tier: 10 requests per minute
    * Pro tier: 60 requests per minute
    
    ## Example
    ```python
    import requests
    
    response = requests.post(
        "https://api.yourdomain.com/v1/ai/generate",
        headers={"Authorization": "Bearer <your_token>"},
        json={
            "prompt": "Write a story about...",
            "max_tokens": 500,
            "temperature": 0.7
        }
    )
    ```
    """
)
async def generate_content(body: GenerationRequest):
    """Generate content using AI"""
    try:
        result = await ai_service.generate(body)
        return GenerationResponse(
            success=True,
            data=result
        )
    except Exception as e:
        handle_error(e)
```

### 8.2 API Versioning

```python
# app/core/versioning.py
from dataclasses import dataclass
from typing import Dict, Set
from datetime import datetime

@dataclass
class APIVersion:
    version: str
    released: datetime
    supported: bool
    sunset_date: Optional[datetime] = None
    
    @property
    def is_deprecated(self) -> bool:
        return self.sunset_date is not None

class VersionManager:
    VERSIONS: Dict[str, APIVersion] = {
        'v1': APIVersion(
            version='v1',
            released=datetime(2024, 1, 1),
            supported=True
        ),
        'v2': APIVersion(
            version='v2',
            released=datetime(2024, 6, 1),
            supported=True
        ),
        'v0': APIVersion(
            version='v0',
            released=datetime(2023, 1, 1),
            supported=False,
            sunset_date=datetime(2024, 1, 1)
        )
    }
    
    @classmethod
    def get_supported_versions(cls) -> Set[str]:
        return {
            v.version
            for v in cls.VERSIONS.values()
            if v.supported
        }
    
    @classmethod
    def get_latest_version(cls) -> str:
        supported = sorted([
            v for v in cls.VERSIONS.values()
            if v.supported
        ], key=lambda x: x.released, reverse=True)
        return supported[0].version if supported else None

# Middleware for version handling
@app.before_request
def handle_version():
    version = request.headers.get('API-Version')
    if not version:
        version = VersionManager.get_latest_version()
    
    if version not in VersionManager.get_supported_versions():
        raise APIError(
            message=f"API version {version} not supported",
            details={
                'supported_versions': list(VersionManager.get_supported_versions()),
                'latest_version': VersionManager.get_latest_version()
            }
        )
    
    g.api_version = version
```

### 8.3 Documentation Generation

```python
# app/core/docs.py
import yaml
from pathlib import Path
from app.core.openapi import app

def generate_openapi_spec(output_dir: str = 'docs/openapi'):
    """Generate OpenAPI specification"""
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    
    # Generate OpenAPI spec
    spec = app.get_openapi_spec()
    
    # Save as YAML
    yaml_path = Path(output_dir) / 'openapi.yaml'
    with open(yaml_path, 'w') as f:
        yaml.dump(spec, f, sort_keys=False)
    
    # Save as JSON
    json_path = Path(output_dir) / 'openapi.json'
    with open(json_path, 'w') as f:
        json.dump(spec, f, indent=2)

def generate_markdown_docs(output_dir: str = 'docs/api'):
    """Generate Markdown documentation"""
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    
    spec = app.get_openapi_spec()
    
    # Generate index
    index_path = Path(output_dir) / 'README.md'
    with open(index_path, 'w') as f:
        f.write(f"# {spec['info']['title']}\n\n")
        f.write(f"Version: {spec['info']['version']}\n\n")
        f.write(spec['info']['description'])
    
    # Generate endpoint documentation
    for path, methods in spec['paths'].items():
        endpoint_doc = f"# {path}\n\n"
        
        for method, details in methods.items():
            endpoint_doc += f"## {method.upper()}\n\n"
            endpoint_doc += f"{details['description']}\n\n"
            
            # Parameters
            if 'parameters' in details:
                endpoint_doc += "### Parameters\n\n"
                for param in details['parameters']:
                    endpoint_doc += f"* `{param['name']}` ({param['in']}) - {param['description']}\n"
            
            endpoint_doc += "\n"
        
        # Save endpoint doc
        doc_path = Path(output_dir) / f"{path.lstrip('/')}.md"
        doc_path.parent.mkdir(parents=True, exist_ok=True)
        with open(doc_path, 'w') as f:
            f.write(endpoint_doc)
```

### 8.4 Interactive Documentation UI

```python
# app/core/swagger.py
from flask_swagger_ui import get_swaggerui_blueprint

SWAGGER_URL = '/docs'
API_URL = '/openapi.json'

swagger_ui_blueprint = get_swaggerui_blueprint(
    SWAGGER_URL,
    API_URL,
    config={
        'app_name': settings.API_TITLE,
        'deepLinking': True,
        'persistAuthorization': True,
        'displayOperationId': False,
        'defaultModelsExpandDepth': 3,
        'defaultModelExpandDepth': 3,
        'defaultModelRendering': 'model',
        'displayRequestDuration': True,
        'docExpansion': 'list',
        'filter': True,
        'showExtensions': True,
        'showCommonExtensions': True,
        'tryItOutEnabled': True
    }
)

app.register_blueprint(swagger_ui_blueprint)
```

### 8.5 Documentation Examples

```python
# docs/examples/authentication.md
# Authentication Examples

## Login
```python
import requests

response = requests.post(
    "https://api.yourdomain.com/v1/auth/login",
    json={
        "email": "user@example.com",
        "password": "your_password"
    }
)

token = response.json()['data']['access_token']
```

## Using the Token
```python
headers = {
    "Authorization": f"Bearer {token}"
}

response = requests.get(
    "https://api.yourdomain.com/v1/users/me",
    headers=headers
)
```


## 9. Contributing

### 9.1 Development Setup

1. Fork and clone the repository:
```bash
git clone https://github.com/yourusername/flask-api-boilerplate.git
cd flask-api-boilerplate
```

2. Create virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # Linux/macOS
# or
venv\Scripts\activate     # Windows
```

3. Install development dependencies:
```bash
pip install -r requirements-dev.txt
```

4. Set up pre-commit hooks:
```bash
pre-commit install
```

### 9.2 Code Standards

#### Code Style

We use the following tools to maintain code quality:

```python
# pyproject.toml
[tool.black]
line-length = 88
target-version = ['py310']
include = '\.pyx?$'

[tool.isort]
profile = "black"
multi_line_output = 3
include_trailing_comma = true
force_grid_wrap = 0
use_parentheses = true
line_length = 88

[tool.mypy]
python_version = "3.10"
disallow_untyped_defs = true
disallow_incomplete_defs = true
check_untyped_defs = true
disallow_untyped_decorators = false
no_implicit_optional = true
warn_redundant_casts = true
warn_unused_ignores = true
warn_return_any = true
strict_optional = true
```

#### Type Hints

All new code must include type hints:

```python
from typing import Optional, List, Dict, Any

def process_data(
    data: Dict[str, Any],
    options: Optional[List[str]] = None
) -> Dict[str, Any]:
    """
    Process input data with optional configuration.
    
    Args:
        data: Input data to process
        options: Optional processing options
    
    Returns:
        Processed data dictionary
    """
    result: Dict[str, Any] = {}
    # Processing logic
    return result
```

### 9.3 Testing Requirements

#### Test Structure

```python
# tests/conftest.py
import pytest
from app import create_app
from app.core.db import get_db

@pytest.fixture
def app():
    """Create test application"""
    app = create_app('testing')
    return app

@pytest.fixture
def client(app):
    """Create test client"""
    return app.test_client()

@pytest.fixture
def db(app):
    """Create test database"""
    db = get_db()
    yield db
    db.close()
```

#### Writing Tests

```python
# tests/services/test_example.py
import pytest
from app.services.example import ExampleService
from app.models.example import ExampleModel

class TestExampleService:
    """Test example service functionality"""
    
    @pytest.fixture
    def service(self):
        return ExampleService()
    
    async def test_create_item(self, service, db):
        """Test item creation"""
        # Arrange
        data = {"name": "test", "value": 123}
        
        # Act
        result = await service.create_item(data)
        
        # Assert
        assert result.name == "test"
        assert result.value == 123

    async def test_invalid_input(self, service):
        """Test validation error handling"""
        with pytest.raises(ValidationError):
            await service.create_item({"invalid": "data"})
```

### 9.4 Pull Request Process

1. Create a feature branch:
```bash
git checkout -b feature/your-feature-name
```

2. Make your changes and ensure all tests pass:
```bash
pytest
black .
isort .
mypy app
```

3. Update documentation if needed

4. Submit PR with:
   - Clear description of changes
   - Any new dependencies
   - Screenshot/video for UI changes
   - Migration guide for breaking changes

## 10. Troubleshooting

### 10.1 Common Issues

#### Database Connection Issues

```python
# Problem: Database connection errors
sqlalchemy.exc.OperationalError: (psycopg2.OperationalError) could not connect to server

# Solution 1: Check connection string
DATABASE_URL=postgresql://user:password@localhost:5432/dbname

# Solution 2: Check if database is running
docker-compose ps
docker-compose logs db
```

#### Authentication Issues

```python
# Problem: JWT token issues
jwt.exceptions.InvalidTokenError: Token is invalid or expired

# Solution 1: Check token expiration
TOKEN_EXPIRE_MINUTES=60  # Increase if needed

# Solution 2: Check clock sync
ntpdate pool.ntp.org  # Sync server time
```

#### Rate Limiting Issues

```python
# Problem: Rate limit exceeded
429 Too Many Requests

# Solution 1: Check current limits
redis-cli GET "rate_limit:user_id:endpoint"

# Solution 2: Reset rate limit (admin only)
redis-cli DEL "rate_limit:user_id:endpoint"
```

### 10.2 Debug Tools

#### Request Debugging

```python
# app/core/debug.py
from flask import request
import logging

def log_request_details():
    """Debug request details"""
    logging.debug(
        "Request details",
        extra={
            'path': request.path,
            'method': request.method,
            'headers': dict(request.headers),
            'data': request.get_data(as_text=True),
            'args': dict(request.args)
        }
    )
```

#### Performance Profiling

```python
# app/core/profiler.py
import cProfile
import pstats
from functools import wraps

def profile(output_file):
    """Profile function execution"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            profiler = cProfile.Profile()
            try:
                return profiler.runcall(func, *args, **kwargs)
            finally:
                stats = pstats.Stats(profiler)
                stats.sort_stats('cumtime')
                stats.dump_stats(output_file)
        return wrapper
    return decorator
```

### 10.3 Logging Tips

```python
# app/core/logging.py
import logging
import json
from flask import request, g

class RequestContextFilter(logging.Filter):
    """Add request context to logs"""
    
    def filter(self, record):
        record.request_id = getattr(g, 'request_id', None)
        record.ip = request.remote_addr
        record.path = request.path
        return True

# Usage
logger = logging.getLogger(__name__)
logger.addFilter(RequestContextFilter())
```

### 10.4 Support Resources

1. Documentation
   - API Documentation: `/docs`
   - OpenAPI Spec: `/openapi.json`
   - Error Codes: `/docs/errors`

2. Monitoring
   - Health Check: `/health`
   - Metrics: `/metrics`
   - Status Page: `status.yourdomain.com`

3. Contact
   - GitHub Issues: Bug reports and feature requests
   - Email: support@yourdomain.com
   - Discord: [Community Server]
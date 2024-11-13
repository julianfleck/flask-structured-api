from sqlmodel import SQLModel, create_engine, Session
from typing import Generator
from app.core.config import settings
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from sqlalchemy import text

# Create database engine with connection pooling
engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,
    pool_size=settings.DB_POOL_SIZE,
    max_overflow=10,
    pool_recycle=3600,
)


def init_migrations(app: Flask) -> None:
    """Initialize database migrations"""
    # Import all models to register them with SQLModel
    from app.models import User, APIKey, Item, CoreModel

    # Create a SQLAlchemy database instance for Flask-Migrate
    db = SQLAlchemy(app)
    db.Model = SQLModel

    # Create tables directly first time
    SQLModel.metadata.create_all(bind=engine)

    # Initialize Flask-Migrate with the SQLAlchemy instance
    migrate = Migrate(app, db)


def get_session() -> Generator[Session, None, None]:
    """Get database session with connection pooling"""
    session = Session(engine)
    try:
        yield session
    finally:
        session.close()


def check_database_connection() -> bool:
    """Test database connection for health checks"""
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
            return True
    except Exception as e:
        print(f"Database connection failed: {e}")
        return False

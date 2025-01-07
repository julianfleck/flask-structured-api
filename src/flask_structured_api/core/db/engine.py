from typing import Generator
from flask import Flask
from sqlalchemy import text
from sqlmodel import Session, create_engine

from flask_structured_api.core.config import settings

# Create database engine with connection pooling
engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,
    pool_size=settings.DB_POOL_SIZE,
    max_overflow=10,
    pool_recycle=3600,
)


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


def init_db(app: Flask = None) -> None:
    """Initialize database tables"""
    from ..models import SQLModel
    SQLModel.metadata.create_all(engine)

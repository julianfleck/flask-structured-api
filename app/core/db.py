from sqlmodel import SQLModel, create_engine, Session
from typing import Generator
from functools import lru_cache
from app.core.config import settings

# Create database engine with connection pooling
engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,  # Enable connection health checks
    pool_size=settings.DB_POOL_SIZE,  # From advanced configuration
    max_overflow=10,
    pool_recycle=3600,  # Recycle connections after 1 hour
)

# Create all tables on startup


def init_db() -> None:
    """Initialize database tables"""
    SQLModel.metadata.create_all(engine)


@lru_cache
def get_session() -> Generator[Session, None, None]:
    """Get database session with connection pooling"""
    with Session(engine) as session:
        try:
            yield session
        finally:
            session.close()

# Health check function used by core/health.py


def check_database_connection() -> bool:
    """Test database connection for health checks"""
    try:
        # Execute simple query to test connection
        with engine.connect() as conn:
            conn.execute("SELECT 1")
        return True
    except Exception:
        return False

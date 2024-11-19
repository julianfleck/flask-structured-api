from sqlmodel import create_engine, Session
from typing import Generator
from app.core.config import settings
from sqlalchemy import text

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

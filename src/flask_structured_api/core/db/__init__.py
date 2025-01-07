from sqlmodel import SQLModel

from .engine import check_database_connection, engine, get_session, init_db
from .migrations import create_migration, init_migrations, upgrade_database
from .shared import db  # Import shared instance

__all__ = [
    "SQLModel",
    "engine",
    "get_session",
    "check_database_connection",
    "init_db",
    "init_migrations",
    "create_migration",
    "upgrade_database",
]


def init_db(app):
    """Initialize database connection"""
    # Check if db is already initialized for this app
    if not hasattr(app, 'db'):
        try:
            db.init_app(app)
            app.db = db
        except Exception as e:
            # If already initialized, just set the reference
            if "already been registered" in str(e):
                app.db = db
            else:
                raise

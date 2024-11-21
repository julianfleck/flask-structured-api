from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate, upgrade as flask_migrate_upgrade
from sqlmodel import SQLModel
from .engine import engine
import os


def init_migrations(app: Flask) -> None:
    """Initialize database migrations"""
    # Import all models to register them with SQLModel
    from flask_structured_api.core.models import (
        User, APIKey, CoreModel,
        APIStorage, StorageBase
    )

    # Create a SQLAlchemy database instance for Flask-Migrate
    db = SQLAlchemy(app)
    db.Model = SQLModel

    # Initialize Flask-Migrate with the SQLAlchemy instance
    migrate = Migrate(app, db)

    # Create migrations directory if it doesn't exist
    if not os.path.exists("migrations"):
        from flask_migrate import init as flask_migrate_init
        # Suppress output by redirecting stdout temporarily
        import sys
        from io import StringIO
        old_stdout = sys.stdout
        sys.stdout = StringIO()
        try:
            flask_migrate_init()
        finally:
            sys.stdout = old_stdout


def run_migrations(app: Flask) -> None:
    """Run all pending migrations"""
    try:
        with app.app_context():
            flask_migrate_upgrade()
    except Exception as e:
        print(f"Migration failed: {e}")
        raise

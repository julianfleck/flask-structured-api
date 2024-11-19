from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from sqlmodel import SQLModel
from .engine import engine


def init_migrations(app: Flask) -> None:
    """Initialize database migrations"""
    # Import all models to register them with SQLModel
    from app.core.models import (
        User, APIKey, CoreModel,
        APIStorage, StorageBase
    )

    # Create a SQLAlchemy database instance for Flask-Migrate
    db = SQLAlchemy(app)
    db.Model = SQLModel

    # Create tables directly first time
    SQLModel.metadata.create_all(bind=engine)

    # Initialize Flask-Migrate with the SQLAlchemy instance
    migrate = Migrate(app, db)

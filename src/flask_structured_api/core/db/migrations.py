import os
from flask import Flask
from flask_migrate import Migrate
from sqlmodel import SQLModel
from flask_migrate import init as migrate_init
from flask_migrate import stamp as migrate_stamp
from flask_migrate import revision as migrate_revision
from flask_migrate import upgrade as migrate_upgrade
from alembic.util.exc import CommandError
from sqlalchemy import text

from .engine import engine
from .shared import db


def init_migrations(app: Flask) -> bool:
    """Initialize migration tracking system"""
    # Import all models at the top to ensure they're registered
    from flask_structured_api.core.models import (
        User,
        APIKey,
        APIStorage,
        CoreModel,
        StorageBase,
        SQLModel
    )

    migrations_dir = os.environ.get('FLASK_MIGRATIONS_DIR', '/app/migrations')
    print(f"📂 Using migrations directory: {migrations_dir}")

    try:
        # Always ensure directory exists
        os.makedirs(migrations_dir, exist_ok=True)

        # Initialize Flask-Migrate first
        migrate = Migrate(app, db)
        migrate.directory = migrations_dir

        # Force model registration
        models = [User, APIKey, APIStorage]
        for model in models:
            print(f"Registering model in migrations: {model.__name__}")
            _ = model.__table__

        # Check if migrations directory is initialized
        is_initialized = os.path.exists(os.path.join(migrations_dir, 'env.py'))

        if not is_initialized:
            print("⚠️  Migrations directory not initialized, creating fresh setup...")
            with app.app_context():
                # Initialize migrations directory
                migrate_init(directory=migrations_dir)
                print("✅ Created fresh migrations directory")

                # Create initial migration with schema creation
                migrate_revision(directory=migrations_dir, autogenerate=True,
                                 message="Initial schema creation")
                print("✅ Created initial migration")

                # Apply the migration immediately
                migrate_upgrade(directory=migrations_dir)
                print("✅ Applied initial migration")

        # Create a new migration for any changes
        with app.app_context():
            try:
                migrate_revision(directory=migrations_dir, autogenerate=True,
                                 message="Create tables")
                print("✅ Additional migration created successfully")
            except Exception as e:
                print(f"Note: No additional migration needed: {e}")

        return True

    except Exception as e:
        print(f"❌ Failed to initialize migrations: {str(e)}")
        return False


def run_migrations(app: Flask, directory: str = None) -> None:
    """Run all pending migrations"""
    from flask_structured_api.core.models import (
        APIKey,
        APIStorage,
        CoreModel,
        StorageBase,
        User,
    )

    migrations_dir = directory or os.environ.get(
        'FLASK_MIGRATIONS_DIR', '/app/migrations')

    db.Model = SQLModel
    if not hasattr(app, 'db'):
        db.init_app(app)
        app.db = db

    # Initialize Flask-Migrate
    migrate = Migrate(app, db, directory=migrations_dir)

    try:
        with app.app_context():
            migrate_upgrade(directory=migrations_dir)
            print("✅ Migrations applied successfully")
            return True
    except Exception as e:
        print(f"❌ Failed to apply migrations: {str(e)}")
        raise


def create_migration(app: Flask, message: str, has_data: bool = False) -> None:
    """Create a new migration"""
    db.Model = SQLModel
    if not hasattr(app, 'db'):
        db.init_app(app)
        app.db = db

    # Initialize Flask-Migrate
    migrations_dir = "/app/migrations"
    migrate = Migrate(app, db, directory=migrations_dir)

    try:
        with app.app_context():
            if has_data:
                migrate_stamp(directory=migrations_dir)
                return

            migrate_revision(autogenerate=True, message=message,
                             directory=migrations_dir)
            print("✅ Migration created successfully")
            return True
    except Exception as e:
        print(f"❌ Failed to create migration: {str(e)}")
        raise


def upgrade_database(app: Flask, has_data: bool = False) -> None:
    """Apply pending migrations"""
    db.Model = SQLModel
    if not hasattr(app, 'db'):
        db.init_app(app)
        app.db = db

    # Initialize Flask-Migrate
    migrations_dir = "/app/migrations"
    migrate = Migrate(app, db, directory=migrations_dir)

    try:
        with app.app_context():
            if has_data:
                migrate_stamp(directory=migrations_dir)
                return

            migrate_upgrade(directory=migrations_dir)
            print("✅ Database upgraded successfully")
            return True
    except Exception as e:
        print(f"❌ Failed to upgrade database: {str(e)}")
        raise

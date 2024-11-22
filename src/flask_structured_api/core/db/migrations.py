from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import (
    Migrate,
    upgrade as flask_migrate_upgrade,
    init as flask_migrate_init,
    migrate as flask_migrate_migrate,
    revision as flask_migrate_revision,
    stamp as flask_migrate_stamp
)
from sqlmodel import SQLModel
from .engine import engine
import os

# Single SQLAlchemy instance
db = SQLAlchemy()


def init_migrations(app: Flask) -> None:
    """Initialize migration tracking system"""
    from flask_structured_api.core.models import (
        User, APIKey, CoreModel,
        APIStorage, StorageBase
    )
    print("🔄 Setting up migration tracking...")

    global db
    db.Model = SQLModel
    db.init_app(app)
    migrate = Migrate(app, db)

    migrations_dir = "/app/migrations"
    if not os.path.exists(migrations_dir):
        os.makedirs(migrations_dir, exist_ok=True)

    try:
        if not os.path.exists(os.path.join(migrations_dir, "alembic.ini")):
            flask_migrate_init(directory=migrations_dir)
            flask_migrate_stamp(directory=migrations_dir, revision="head")
            print("✅ Migration tracking initialized")
        else:
            print("✅ Migration tracking already initialized")
    except Exception as e:
        print("❌ Migration init error: {}".format(str(e)))
        raise


def create_migration(app: Flask, message: str, has_data: bool = False) -> None:
    """Create a new migration"""
    global db
    migrate = Migrate(app, db, compare_type=True)
    migrations_dir = "/app/migrations"

    try:
        if has_data:
            flask_migrate_stamp(directory=migrations_dir, revision="head")
            return

        flask_migrate_migrate(
            message=message,
            directory=migrations_dir
        )
    except Exception as e:
        print(f"❌ Failed to create migration: {e}")
        raise


def upgrade_database(app: Flask, has_data: bool = False) -> None:
    """Apply pending migrations"""
    global db
    migrate = Migrate(app, db, compare_type=True)
    migrations_dir = "/app/migrations"

    try:
        if has_data:
            flask_migrate_stamp(directory=migrations_dir, revision="head")
            return

        flask_migrate_upgrade(directory=migrations_dir)
    except Exception as e:
        print(f"❌ Failed to apply migrations: {e}")
        raise


def run_migrations(app: Flask) -> None:
    """Run all pending migrations"""
    from flask_structured_api.core.models import (
        User, APIKey, CoreModel,
        APIStorage, StorageBase
    )

    db = SQLAlchemy(app)
    db.Model = SQLModel
    migrate = Migrate(app, db)

    migrations_dir = "/app/migrations"
    flask_migrate_upgrade(directory=migrations_dir)

import os
import traceback
from flask_migrate import migrate, upgrade, current
from flask_structured_api.core.utils.logger import get_standalone_logger
from flask_structured_api.factory import create_flask_app
from flask_structured_api.core.db import db
from flask_structured_api.core.db.engine import init_db
from flask_structured_api.core.models import (
    User,
    APIKey,
    APIStorage,
    CoreModel,
    StorageBase,
    SQLModel
)
from flask_structured_api.core.enums import StorageType
from sqlalchemy.sql import text


def create_tables():
    """Create database tables using SQLModel's create_all"""
    print("\n🔨 Starting table creation process...")
    app = create_flask_app()

    with app.app_context():
        try:
            # Import and register models
            from flask_structured_api.core.models import (
                User,
                APIKey,
                APIStorage,
                CoreModel,
                StorageBase,
                SQLModel
            )

            # Ensure SQLModel metadata is bound to our engine
            SQLModel.metadata.bind = db.engine

            # Create all tables
            SQLModel.metadata.create_all(db.engine)
            print("✅ Tables created successfully")

            # Commit the session to persist changes
            db.session.commit()

            return True

        except Exception as e:
            print("❌ Failed during table creation: {}".format(str(e)))
            print("Full traceback:")
            print(traceback.format_exc())
            return False


if __name__ == "__main__":
    success = create_tables()
    if not success:
        exit(1)

import os
import sys
import time
import traceback

from sqlalchemy import text
from flask_migrate import Migrate, upgrade as migrate_upgrade, stamp as migrate_stamp

from flask_structured_api.core.db import check_database_connection
from flask_structured_api.core.db.shared import db  # Import shared instance
from flask_structured_api.core.db.migrations import init_migrations
from flask_structured_api.core.scripts.backup_db import (
    backup_database,
    check_tables_empty,
    drop_all_tables,
    restore_database,
)
from flask_structured_api.core.utils.logger import get_standalone_logger
from flask_structured_api.factory import create_flask_app
from flask_structured_api.core.models import User
from flask_structured_api.core.config import settings
from flask_structured_api.core.scripts.create_tables import create_tables
from werkzeug.security import generate_password_hash

# Create standalone logger for database initialization
db_logger = get_standalone_logger("db.init")


def wait_for_db():
    """Wait for database to be ready"""
    retries = 30
    while retries > 0:
        if check_database_connection():
            db_logger.info("Database connection established")
            time.sleep(2)
            return True
        retries -= 1
        db_logger.warning(
            "Waiting for database... ({} attempts remaining)".format(retries)
        )
        time.sleep(1)
    return False


def get_current_alembic_version():
    """Get the current alembic version from the database"""
    try:
        with db.engine.connect() as conn:
            result = conn.execute(
                text("SELECT version_num FROM alembic_version")).fetchone()
            if result:
                version = result[0]
                print(f" Current alembic version in database: {version}")
                return version
    except Exception as e:
        print(f"❌ Error reading alembic version: {e}")
    return None


def init_db() -> bool:
    """Initialize database with required tables"""
    print("🚀 Starting database initialization (init_db.py)...")

    try:
        app = create_flask_app()
        migrate = Migrate(app, db)
        print("Created Flask app and initialized Migrate")

        with app.app_context():
            migrations_dir = os.environ.get('FLASK_MIGRATIONS_DIR', '/app/migrations')
            print("Using migrations directory: {}".format(migrations_dir))

            # Initialize migrations if needed
            if not os.path.exists(os.path.join(migrations_dir, 'versions')):
                print("No migrations found, initializing fresh setup...")
                if not init_migrations(app):
                    print("❌ Failed to initialize migrations")
                    return False
                print("✅ Migrations initialized")

            # Check if tables exist, if not, create them
            inspector = db.inspect(db.engine)
            tables = inspector.get_table_names()

            if not tables or 'users' not in tables:
                print("No tables found or critical table 'users' missing, creating tables...")
                if not create_tables():
                    print("❌ Failed to create tables")
                    return False
                print("✅ Tables created successfully")
                db.session.commit()

                # Use Alembic's stamp command to set the version
                try:
                    print("Stamping database with current state...")
                    migrate_stamp(revision='head')
                    print("✅ Database stamped with current state")
                except Exception as e:
                    print(f"❌ Error during stamping: {e}")
                    return False

            # Create admin user if needed
            print("Checking for admin user...")
            try:
                admin = db.session.query(User).filter_by(
                    email=settings.ADMIN_EMAIL).first()
                if not admin:
                    print("Creating admin user...")
                    admin = User(
                        email=settings.ADMIN_EMAIL,
                        full_name=settings.ADMIN_NAME,
                        role="admin",
                        is_active=True,
                        permissions=["*"],
                        hashed_password=generate_password_hash(settings.ADMIN_PASSWORD)
                    )
                    db.session.add(admin)
                    db.session.commit()
                    print("✅ Admin user created successfully")
                else:
                    print("Admin user already exists")

            except Exception as e:
                print("❌ Failed to create admin user: {}".format(str(e)))
                print(traceback.format_exc())
                return False

            print("✨ Database initialization completed successfully")
            return True

    except Exception as e:
        print("❌ Database setup failed: {}".format(str(e)))
        print("Traceback:")
        traceback.print_exc()
        return False


def main():
    """Main entry point for init_db script"""
    try:
        print("🚀 Starting database initialization...")
        success = init_db()
        print("📊 Init DB returned: {}".format(success))
        if success:
            print("✨ Database initialization completed successfully")
            sys.exit(0)
        else:
            print("❌ Database initialization failed")
            sys.exit(1)
    except Exception as e:
        print("💥 Fatal error in main: {}".format(e))
        sys.exit(1)


if __name__ == "__main__":
    main()

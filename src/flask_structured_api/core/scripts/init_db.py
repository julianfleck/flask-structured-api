import time
import os
import sys
from sqlalchemy import text
from flask_structured_api.core.utils.logger import db_logger

from flask_structured_api.core.db import check_database_connection
from flask_structured_api.factory import create_app
from flask_structured_api.core.scripts.backup_db import restore_database, check_tables_empty, drop_all_tables, backup_database
from flask_structured_api.core.db.migrations import db  # Import shared instance


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
            "Waiting for database... ({} attempts remaining)".format(retries))
        time.sleep(1)
    return False


def init_db():
    """Initialize database with migrations"""
    from flask_structured_api.core.db import (
        check_database_connection, SQLModel, engine,
        init_migrations, create_migration, upgrade_database
    )

    app = create_app()
    with app.app_context():
        db_logger.info("Starting database initialization...")

        if not wait_for_db():
            db_logger.error("Database connection failed")
            return False

        try:
            # Initialize migrations tracking first
            init_migrations(app)

            # Check if we have any tables at all
            try:
                with engine.connect() as conn:
                    result = conn.execute(text("""
                        SELECT COUNT(*) FROM users;
                    """))
                    has_tables = True
                    user_count = result.scalar()
                    db_logger.info(f"Found {user_count} users in database")
                    has_data = user_count > 0
            except Exception:
                has_tables = False
                has_data = False
                db_logger.info("No existing tables found")

            if not has_tables:
                db_logger.info("Creating fresh database schema...")
                create_migration(app, "Initial migration", has_data=False)
                upgrade_database(app, has_data=False)
                return True

            if not has_data:
                db_logger.info("Found empty database, attempting restore...")
                if restore_database():
                    db_logger.info("Database restored from backup")
                    return True

            # For existing database with data, just stamp current state
            db_logger.info("Found existing data, stamping current state...")
            create_migration(app, "Existing data", has_data=True)
            upgrade_database(app, has_data=True)
            return True

        except Exception as e:
            db_logger.error(f"Database setup failed: {e}")
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

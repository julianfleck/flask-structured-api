from flask import Flask, current_app
from flask_migrate import upgrade, init, migrate
import time
import os
from flask_structured_api.core.db import check_database_connection, SQLModel, engine, init_migrations
from flask_structured_api.core.config import settings
from flask_structured_api.factory import create_app
from sqlalchemy import text
import sys


def wait_for_db():
    """Wait for database to be ready"""
    retries = 30
    while retries > 0:
        if check_database_connection():
            print("✅ Database connection established")
            time.sleep(2)
            return True
        retries -= 1
        print(f"⏳ Waiting for database... ({retries} attempts remaining)")
        time.sleep(1)
    return False


def init_db():
    """Initialize database with migrations"""
    app = create_app()
    with app.app_context():
        if not wait_for_db():
            print("❌ Database connection failed")
            return False

        try:
            # Check if tables already exist
            with engine.connect() as conn:
                result = conn.execute(text("""
                    SELECT EXISTS (
                        SELECT FROM information_schema.tables 
                        WHERE table_name = 'users'
                    );
                """))
                tables_exist = result.scalar()

            if tables_exist:
                print("✅ Database already initialized, skipping setup")
                return True

            # Only drop and recreate if tables don't exist
            with engine.connect() as conn:
                conn.execute(text("""
                    DROP TABLE IF EXISTS api_keys CASCADE;
                    DROP TABLE IF EXISTS api_storage CASCADE;
                    DROP TABLE IF EXISTS users CASCADE;
                    DROP TABLE IF EXISTS alembic_version CASCADE;
                """))
                conn.commit()
                print("✅ Existing tables dropped")

            # Initialize migrations
            init_migrations(app)
            print("✅ Migration tracking initialized")

            # Create initial migration
            migrate()
            print("✅ Initial migration created")

            # Apply migration
            upgrade()
            print("✅ Initial migration applied")
            return True

        except Exception as e:
            print("❌ Database setup failed: {}".format(e))
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

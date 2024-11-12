from flask import Flask
from app.main import create_app
from flask_migrate import upgrade, init, migrate
import time
from app.core.db import check_database_connection
import os


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
            # Initialize migrations if they don't exist
            if not os.path.exists("migrations"):
                init()
                print("✅ Migrations initialized")
                migrate(message="Initial migration")
                print("✅ Initial migration created")

            # Apply migrations
            upgrade()
            print("✅ Database migrations applied successfully")
            return True
        except Exception as e:
            print(f"❌ Migration failed: {e}")
            return False


if __name__ == "__main__":
    init_db()

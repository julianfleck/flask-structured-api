from flask_structured_api.main import create_app
from flask_migrate import migrate, upgrade
import os


def create_tables():
    """Create database tables and run migrations"""
    app = create_app()

    with app.app_context():
        # Create new migration if needed
        migrate(message="Create tables")
        print("✅ Migration created")

        # Apply migrations
        upgrade()
        print("✅ Migrations applied")


if __name__ == "__main__":
    create_tables()

import os
import sys
from dotenv import load_dotenv
from flask_structured_api.factory import create_app
from flask_structured_api.core.config import settings

# Load environment variables
load_dotenv()


def run_app(debug=True, use_debugpy=False):
    """Run the Flask application with optional remote debugging support"""
    if use_debugpy:
        os.environ['DEBUGPY_ENABLE'] = '1'

    # Create app using factory pattern
    app = create_app()
    if not app:
        print("❌ Failed to create Flask app")
        return

    print(f"🚀 Starting {settings.API_NAME} v{settings.API_VERSION}")
    print(f"🌍 Environment: {settings.ENVIRONMENT}")

    app.run(
        host=settings.API_HOST,
        port=settings.API_PORT,
        debug=debug and settings.ENVIRONMENT == "development",
        use_reloader=True,
        reloader_type='stat'
    )


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(
        description=f"Run {settings.API_NAME} with optional remote debugging")
    parser.add_argument("--debugpy", action="store_true",
                        help="Enable remote debugging with debugpy")
    parser.add_argument("--no-debug", action="store_true",
                        help="Disable Flask debug mode")
    args = parser.parse_args()

    # Set Python flags via environment
    os.environ['PYTHONFLAGS'] = '-X frozen_modules=off'

    # Debug mode is enabled only if:
    # 1. --no-debug is not set
    # 2. We're in development environment
    debug_mode = not args.no_debug and settings.ENVIRONMENT == "development"
    run_app(debug=debug_mode, use_debugpy=args.debugpy)

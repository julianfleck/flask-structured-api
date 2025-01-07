import os
import sys
import asyncio
from dotenv import load_dotenv

from flask_structured_api.core.config import settings
from flask_structured_api.factory import create_flask_app, create_app

# Load environment variables
load_dotenv()


def run_app(debug=True, use_debugpy=False):
    """Run the application with optional remote debugging support"""
    if use_debugpy:
        os.environ["DEBUGPY_ENABLE"] = "1"

    print("🚀 Starting {} v{}".format(settings.API_NAME, settings.API_VERSION))
    print("🌍 Environment: {}".format(settings.ENVIRONMENT))

    if settings.ENVIRONMENT == "development":
        # Use Flask's development server
        app = create_flask_app()
        if not app:
            print("❌ Failed to create Flask app")
            return

        app.run(
            host=settings.API_HOST,
            port=settings.API_PORT,
            debug=debug,
            use_reloader=True,
            reloader_type="stat",
        )
    else:
        # Use Hypercorn for production
        from hypercorn.asyncio import serve
        from hypercorn.config import Config

        async def serve_app():
            config = Config()
            config.bind = ["{0}:{1}".format(settings.API_HOST, settings.API_PORT)]
            config.worker_class = "asyncio"
            config.debug = debug

            asgi_app = create_app()
            await serve(asgi_app, config)

        asyncio.run(serve_app())


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="Run {} with optional remote debugging".format(settings.API_NAME)
    )
    parser.add_argument(
        "--debugpy", action="store_true", help="Enable remote debugging with debugpy"
    )
    parser.add_argument(
        "--no-debug", action="store_true", help="Disable Flask debug mode"
    )
    args = parser.parse_args()

    # Set Python flags via environment
    os.environ["PYTHONFLAGS"] = "-X frozen_modules=off"

    # Debug mode is enabled only if:
    # 1. --no-debug is not set
    # 2. We're in development environment
    debug_mode = not args.no_debug and settings.ENVIRONMENT == "development"
    run_app(debug=debug_mode, use_debugpy=args.debugpy)

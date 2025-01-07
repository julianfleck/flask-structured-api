from flask_structured_api.core.config import settings
from flask_structured_api.factory import create_app, create_flask_app
from flask_structured_api.extensions.services.stip.processor import STIPProcessor
from flask_structured_api.extensions.services.stip.storage import FileStore
from flask_structured_api.core.warnings import WarningCollector
from flask_structured_api.core.services.ai import AIService
from flask_structured_api.core.ai.providers import get_provider


def create_application():
    """Create and initialize the application"""
    # Create both WSGI and ASGI apps using the same base Flask app
    flask_app = create_flask_app()  # This will return the same instance
    asgi_wrapped = create_app()     # This will use the same base instance
    flask_asgi_app = asgi_wrapped.flask_app

    # Initialize services within app context
    with flask_app.app_context():
        # Initialize AI service
        provider = get_provider(settings.AI_PROVIDER)
        flask_app.ai_service = AIService(provider)

        # Initialize additional services
        file_store = FileStore()
        flask_app.file_store = file_store
        flask_app.stip_processor = STIPProcessor(file_store=file_store)
        flask_app.warning_collector = WarningCollector()

        # Copy services to the underlying Flask app of the ASGI wrapper
        flask_asgi_app.ai_service = flask_app.ai_service
        flask_asgi_app.file_store = flask_app.file_store
        flask_asgi_app.stip_processor = flask_app.stip_processor
        flask_asgi_app.warning_collector = flask_app.warning_collector

    return asgi_wrapped


# Create the application instance
app = create_application()

if __name__ == "__main__":
    from hypercorn.config import Config
    from hypercorn.asyncio import serve
    import asyncio

    config = Config()
    config.bind = ["{0}:{1}".format(settings.API_HOST, settings.API_PORT)]
    config.worker_class = "asyncio"
    config.debug = settings.API_DEBUG

    print("🌐 Starting {} v{}".format(settings.API_NAME, settings.API_VERSION))
    print("🌐 Server starting at http://{}:{}".format(settings.API_HOST, settings.API_PORT))

    asyncio.run(serve(app, config))

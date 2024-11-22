from .factory import create_app
from .core.utils.logger import system_logger
import logging

# Configure Flask's logger to use our system logger
werkzeug_logger = logging.getLogger('werkzeug')
werkzeug_logger.handlers = system_logger.handlers

app = create_app()

if __name__ == "__main__":
    # Disable Flask's default logging handler
    app.logger.handlers = system_logger.handlers
    app.run()

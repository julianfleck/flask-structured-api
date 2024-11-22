from .factory import create_app
from .core.utils.logger import system_logger
import logging

# Configure Flask's logger to use our system logger
app = create_app()

if __name__ == "__main__":
    app.run()

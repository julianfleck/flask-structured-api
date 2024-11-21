import multiprocessing
import os
try:
    from gunicorn.app.base import BaseApplication
except ImportError:
    print("⚠️  Gunicorn not installed. Install with: pip install gunicorn")
    BaseApplication = object  # Fallback for type hints

from flask_structured_api.factory import create_app


class GunicornApp(BaseApplication):
    def __init__(self, app, options=None):
        self.options = options or {}
        self.application = app
        super().__init__()

    def load_config(self):
        for key, value in self.options.items():
            self.cfg.set(key, value)

    def load(self):
        return self.application


def run():
    """Run application with Gunicorn"""
    try:
        from gunicorn.app.base import BaseApplication
    except ImportError:
        print("⚠️  Gunicorn not installed. Install with: pip install gunicorn")
        return

    workers = int(os.getenv('GUNICORN_WORKERS',
                  multiprocessing.cpu_count() * 2 + 1))
    bind = f"{os.getenv('API_HOST', '0.0.0.0')}:{os.getenv('API_PORT', 5000)}"

    app = create_app()
    options = {
        'bind': bind,
        'workers': workers,
        'worker_class': 'gthread',
        'timeout': 120,
    }
    GunicornApp(app, options).run()

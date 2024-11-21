import os
from celery import Celery
from flask_structured_api.factory import create_app


def make_celery(app):
    """Create and configure Celery instance with Flask app context"""
    celery = Celery(
        app.import_name,
        broker=app.config['CELERY_BROKER_URL'],
        backend=app.config['CELERY_RESULT_BACKEND']
    )

    # Update celery config from Flask config
    celery.conf.update(app.config)

    # Ensure tasks run within Flask app context
    class ContextTask(celery.Task):
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)

    celery.Task = ContextTask
    return celery


# Create Flask app and Celery instances
flask_app = create_app()
celery_app = make_celery(flask_app)


def worker():
    """Run Celery worker"""
    argv = [
        'worker',
        '--loglevel=INFO',
        f"--concurrency={os.getenv('CELERY_WORKERS', 4)}",
        '--pool=prefork'
    ]
    celery_app.worker_main(argv)


def beat():
    """Run Celery beat scheduler"""
    argv = [
        'beat',
        '--loglevel=INFO'
    ]
    celery_app.worker_main(argv)


def flower():
    """Run Flower monitoring tool"""
    try:
        from flower.command import FlowerCommand
        argv = [
            'flower',
            '--port=5555',
            '--broker=redis://localhost:6379/0'
        ]
        FlowerCommand().execute_from_commandline(argv)
    except ImportError:
        print("⚠️  Flower not installed. Install with: pip install flower")


if __name__ == '__main__':
    import sys
    if len(sys.argv) > 1:
        if sys.argv[1] == 'worker':
            worker()
        elif sys.argv[1] == 'beat':
            beat()
        elif sys.argv[1] == 'flower':
            flower()
        else:
            print("Usage: celery.py [worker|beat|flower]")
    else:
        print("Usage: celery.py [worker|beat|flower]")

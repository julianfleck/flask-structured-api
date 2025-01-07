from .backup_db import backup_database, cleanup_backups
from .celery import beat as run_beat
from .celery import flower as run_flower
from .celery import worker as run_worker
from .create_tables import create_tables
# from .gunicorn import run as run_gunicorn
from .test_backup import test_backup_system


def init_db():
    from .init_db import init_db as _init_db

    return _init_db()


def init_db_main():
    from .init_db import main as _main

    return _main()


__all__ = [
    "backup_database",
    "cleanup_backups",
    "init_db",
    "create_tables",
    # "run_gunicorn",
    "run_worker",
    "run_beat",
    "run_flower",
    "test_backup_system",
]

from flask import Flask
from flask_migrate import Migrate

from flask_structured_api.core.cli.api_keys import api_keys_cli
from flask_structured_api.core.cli.backup import backup_cli
from flask_structured_api.core.cli.tokens import tokens_cli


def init_cli(app: Flask):
    # Ensure Migrate is initialized
    if not hasattr(app, 'db'):
        raise RuntimeError("Database must be initialized before CLI")

    app.cli.add_command(tokens_cli)
    app.cli.add_command(api_keys_cli)
    app.cli.add_command(backup_cli)

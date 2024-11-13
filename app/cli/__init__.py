from flask import Flask
from app.cli.tokens import tokens_cli
from app.cli.api_keys import api_keys_cli


def init_cli(app: Flask):
    app.cli.add_command(tokens_cli)
    app.cli.add_command(api_keys_cli)

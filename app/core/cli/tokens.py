import click
from flask.cli import AppGroup
from app.services.auth import AuthService
from app.core.db import get_session

tokens_cli = AppGroup('tokens', help='JWT token management commands')


@tokens_cli.command('create')
@click.option('--email', prompt=True, help='User email')
@click.option('--expires', default=60, help='Token expiry in minutes')
def create_token(email: str, expires: int):
    """Create a JWT token for a user"""
    db = next(get_session())
    auth_service = AuthService(db)

    user = auth_service.get_user_by_email(email)
    if not user:
        click.echo(f"Error: User {email} not found")
        return

    tokens = auth_service.create_tokens_for_user(
        user.id, expires_minutes=expires)
    click.echo("\nAccess Token (expires in {} minutes):".format(expires))
    click.echo(tokens.access_token)
    click.echo("\nRefresh Token:")
    click.echo(tokens.refresh_token)

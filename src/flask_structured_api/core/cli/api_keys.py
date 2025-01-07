from datetime import datetime, timedelta

import click
from flask.cli import AppGroup

from flask_structured_api.core.db import get_session
from flask_structured_api.core.models.domain import APIKey, User
from flask_structured_api.core.services.auth import AuthService

api_keys_cli = AppGroup("api-keys", help="API key management commands")


@api_keys_cli.command("create")
@click.option("--email", prompt=True, help="User email")
@click.option("--name", prompt=True, help="Key name")
@click.option("--expires", default=None, type=int, help="Days until expiration")
@click.option("--scopes", multiple=True, help="Scopes to assign")
def create_key(email: str, name: str, expires: int, scopes: tuple):
    """Create an API key for a user"""
    db = next(get_session())
    auth_service = AuthService(db)

    user = auth_service.get_user_by_email(email)
    if not user:
        click.echo(f"Error: User {email} not found")
        return

    expires_at = None
    if expires:
        expires_at = datetime.utcnow() + timedelta(days=expires)

    api_key = auth_service.create_api_key(
        user_id=user.id, name=name, scopes=list(scopes), expires_at=expires_at
    )

    click.echo("\nAPI Key (save this, it won't be shown again):")
    click.echo(api_key)
    if expires_at:
        click.echo(f"\nExpires at: {expires_at}")


@api_keys_cli.command("list")
@click.option("--email", prompt=True, help="User email")
def list_keys(email: str):
    """List all API keys for a user"""
    db = next(get_session())
    auth_service = AuthService(db)

    user = auth_service.get_user_by_email(email)
    if not user:
        click.echo(f"Error: User {email} not found")
        return

    keys = auth_service.get_user_api_keys(user.id)
    if not keys:
        click.echo("No API keys found")
        return

    for key in keys:
        click.echo(f"\nID: {key.id}")
        click.echo(f"Name: {key.name}")
        click.echo(f"Created: {key.created_at}")
        click.echo(f"Last used: {key.last_used_at or 'Never'}")
        click.echo(f"Expires: {key.expires_at or 'Never'}")
        click.echo(f"Active: {key.is_active}")
        click.echo(f"Scopes: {', '.join(key.scopes)}")


@api_keys_cli.command("revoke")
@click.option("--email", prompt=True, help="User email")
@click.option("--key-id", prompt=True, type=int, help="API key ID")
def revoke_key(email: str, key_id: int):
    """Revoke an API key"""
    db = next(get_session())
    auth_service = AuthService(db)

    user = auth_service.get_user_by_email(email)
    if not user:
        click.echo(f"Error: User {email} not found")
        return

    try:
        auth_service.revoke_api_key(key_id, user.id)
        click.echo("API key revoked successfully")
    except Exception as e:
        click.echo(f"Error: {str(e)}")

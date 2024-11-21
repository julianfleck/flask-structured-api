import click
from flask.cli import AppGroup
from pathlib import Path
from datetime import datetime

backup_cli = AppGroup('backup', help='Database backup management')


@backup_cli.command('list')
def list_backups():
    """List all available backups"""
    backup_dir = Path("/backups")
    if not backup_dir.exists():
        click.echo("No backups directory found")
        return

    backups = sorted(backup_dir.glob("*.sql*"),
                     key=lambda x: x.stat().st_mtime, reverse=True)
    if not backups:
        click.echo("No backups found")
        return

    click.echo("\nAvailable backups:")
    for backup in backups:
        size = backup.stat().st_size / (1024 * 1024)  # Convert to MB
        timestamp = datetime.fromtimestamp(backup.stat().st_mtime)
        click.echo(f"📁 {backup.name}")
        click.echo(f"   📅 {timestamp.strftime('%Y-%m-%d %H:%M:%S')}")
        click.echo(f"   📊 {size:.2f} MB\n")


@backup_cli.command('create')
def create_backup():
    """Create a new backup manually"""
    from flask_structured_api.core.scripts.backup_db import backup_database
    backup_database()

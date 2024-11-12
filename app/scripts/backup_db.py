from datetime import datetime, timedelta
from pathlib import Path
import subprocess
import gzip
import os
from app.core.config import settings

BACKUP_DIR = Path("/backups")


def cleanup_backups():
    """Cleanup old backups based on retention policy"""
    now = datetime.now()

    # Keep daily backups for BACKUP_KEEP_DAYS
    daily_cutoff = now - timedelta(days=settings.BACKUP_KEEP_DAYS)
    # Keep weekly backups for BACKUP_KEEP_WEEKS
    weekly_cutoff = now - timedelta(weeks=settings.BACKUP_KEEP_WEEKS)
    # Keep monthly backups for BACKUP_KEEP_MONTHS
    monthly_cutoff = now - timedelta(days=settings.BACKUP_KEEP_MONTHS * 30)

    for backup in BACKUP_DIR.glob("*.sql*"):
        timestamp = datetime.strptime(
            backup.stem.split('_')[1], "%Y%m%d%H%M%S")

        # Keep if it's a monthly backup within retention
        if timestamp.day == 1 and timestamp > monthly_cutoff:
            continue
        # Keep if it's a weekly backup within retention
        if timestamp.weekday() == 0 and timestamp > weekly_cutoff:
            continue
        # Keep if it's a daily backup within retention
        if timestamp > daily_cutoff:
            continue

        backup.unlink()


def backup_database():
    """Create PostgreSQL database backup"""
    BACKUP_DIR.mkdir(exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")

    if settings.BACKUP_COMPRESSION:
        backup_file = BACKUP_DIR / f"backup_{timestamp}.sql.gz"
        with gzip.open(backup_file, 'wb') as gz:
            process = subprocess.Popen([
                "pg_dump",
                "-h", os.getenv("POSTGRES_HOST", "db"),
                "-U", os.getenv("POSTGRES_USER", "user"),
                "-d", os.getenv("POSTGRES_DB", "api"),
            ], stdout=subprocess.PIPE, env={"PGPASSWORD": os.getenv("POSTGRES_PASSWORD")})
            gz.write(process.stdout.read())
    else:
        backup_file = BACKUP_DIR / f"backup_{timestamp}.sql"
        subprocess.run([
            "pg_dump",
            "-h", os.getenv("POSTGRES_HOST", "db"),
            "-U", os.getenv("POSTGRES_USER", "user"),
            "-d", os.getenv("POSTGRES_DB", "api"),
            "-f", str(backup_file)
        ], env={"PGPASSWORD": os.getenv("POSTGRES_PASSWORD")})

    cleanup_backups()


if __name__ == "__main__":
    backup_database()

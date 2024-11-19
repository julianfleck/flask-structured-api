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
        # Extract timestamp from filename like "backup_20241119192601.sql.gz"
        try:
            filename = backup.name.split('.')[0]  # Remove extension(s)
            timestamp = datetime.strptime(
                filename.split('_')[1], "%Y%m%d%H%M%S")

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
        except (IndexError, ValueError) as e:
            print(f"⚠️ Skipping invalid backup filename: {backup.name}")
            continue


def backup_database():
    """Create PostgreSQL database backup"""
    try:
        # Validate required environment variables
        required_vars = {
            "POSTGRES_HOST": os.getenv("POSTGRES_HOST", "db"),
            "POSTGRES_USER": os.getenv("POSTGRES_USER", "user"),
            "POSTGRES_DB": os.getenv("POSTGRES_DB", "api"),
            "POSTGRES_PASSWORD": os.getenv("POSTGRES_PASSWORD")
        }

        # Check for missing required variables
        missing_vars = [k for k, v in required_vars.items() if v is None]
        if missing_vars:
            raise Exception("Missing required environment variables: {}".format(
                ", ".join(missing_vars)))

        BACKUP_DIR.mkdir(exist_ok=True, parents=True)
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")

        if settings.BACKUP_COMPRESSION:
            backup_file = BACKUP_DIR / "backup_{}.sql.gz".format(timestamp)
            with gzip.open(backup_file, 'wb') as gz:
                process = subprocess.run([
                    "pg_dump",
                    "-h", required_vars["POSTGRES_HOST"],
                    "-U", required_vars["POSTGRES_USER"],
                    "-d", required_vars["POSTGRES_DB"],
                ], capture_output=True, check=True,
                    env={"PGPASSWORD": required_vars["POSTGRES_PASSWORD"]})

                if process.returncode != 0:
                    raise Exception("Backup failed: {}".format(
                        process.stderr.decode()))

                gz.write(process.stdout)
        else:
            backup_file = BACKUP_DIR / "backup_{}.sql".format(timestamp)
            process = subprocess.run([
                "pg_dump",
                "-h", required_vars["POSTGRES_HOST"],
                "-U", required_vars["POSTGRES_USER"],
                "-d", required_vars["POSTGRES_DB"],
                "-f", str(backup_file)
            ], capture_output=True, check=True,
                env={"PGPASSWORD": required_vars["POSTGRES_PASSWORD"]})

            if process.returncode != 0:
                raise Exception("Backup failed: {}".format(
                    process.stderr.decode()))

        print("✅ Backup created successfully: {}".format(backup_file))
        cleanup_backups()
        return backup_file

    except Exception as e:
        print("❌ Backup failed: {}".format(str(e)))
        raise


if __name__ == "__main__":
    backup_database()

import gzip
import os
import subprocess
from datetime import datetime, timedelta
from pathlib import Path

from flask_structured_api.core.config import settings
from flask_structured_api.core.utils.logger import get_standalone_logger

BACKUP_DIR = Path("/backups")

# Create standalone logger for backup operations
backup_logger = get_standalone_logger("db.backup")


def main():
    """Main entry point for backup script"""
    try:
        success = backup_database()
        if success:
            backup_logger.info("✅ Backup completed successfully")
            return 0
        backup_logger.error("❌ Backup failed")
        return 1
    except Exception as e:
        backup_logger.error("❌ Backup failed: {}".format(e))
        return 1


def backup_database():
    """Create database backup"""
    try:
        # Validate required environment variables
        required_vars = {
            "POSTGRES_HOST": os.getenv("POSTGRES_HOST", "db"),
            "POSTGRES_USER": os.getenv("POSTGRES_USER", "user"),
            "POSTGRES_DB": os.getenv("POSTGRES_DB", "api"),
            "POSTGRES_PASSWORD": os.getenv("POSTGRES_PASSWORD"),
        }

        # Check for missing required variables
        missing_vars = [k for k, v in required_vars.items() if v is None]
        if missing_vars:
            raise Exception(
                "Missing required environment variables: {}".format(
                    ", ".join(missing_vars)
                )
            )

        BACKUP_DIR.mkdir(exist_ok=True, parents=True)
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")

        if settings.BACKUP_COMPRESSION:
            backup_file = BACKUP_DIR / "backup_{}.sql.gz".format(timestamp)
            with gzip.open(backup_file, "wb") as gz:
                process = subprocess.run(
                    [
                        "pg_dump",
                        "-h",
                        required_vars["POSTGRES_HOST"],
                        "-U",
                        required_vars["POSTGRES_USER"],
                        "-d",
                        required_vars["POSTGRES_DB"],
                        "--clean",
                        "--if-exists",
                        "--no-owner",
                        "--no-privileges",
                    ],
                    capture_output=True,
                    check=True,
                    env={"PGPASSWORD": required_vars["POSTGRES_PASSWORD"]},
                )

                if process.returncode != 0:
                    raise Exception("Backup failed: {}".format(process.stderr.decode()))

                gz.write(process.stdout)
        else:
            backup_file = BACKUP_DIR / "backup_{}.sql".format(timestamp)
            process = subprocess.run(
                [
                    "pg_dump",
                    "-h",
                    required_vars["POSTGRES_HOST"],
                    "-U",
                    required_vars["POSTGRES_USER"],
                    "-d",
                    required_vars["POSTGRES_DB"],
                    "-f",
                    str(backup_file),
                ],
                capture_output=True,
                check=True,
                env={"PGPASSWORD": required_vars["POSTGRES_PASSWORD"]},
            )

            if process.returncode != 0:
                raise Exception("Backup failed: {}".format(process.stderr.decode()))

        backup_logger.info("✅ Backup created successfully: {}".format(backup_file))
        cleanup_backups()
        return True

    except Exception as e:
        backup_logger.error(f"⚠️ Backup failed: {e}")
        return False


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
            filename = backup.name.split(".")[0]  # Remove extension(s)
            timestamp = datetime.strptime(filename.split("_")[1], "%Y%m%d%H%M%S")

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
            backup_logger.warning(f"⚠️ Skipping invalid backup filename: {backup.name}")
            continue


def check_tables_empty():
    """Check if all tables in database are empty"""
    from sqlalchemy import text

    from flask_structured_api.core.db import engine

    try:
        with engine.connect() as conn:
            # Get all table names
            result = conn.execute(
                text(
                    """
                SELECT tablename
                FROM pg_tables
                WHERE schemaname = 'public'
                AND tablename != 'alembic_version';
            """
                )
            )
            tables = [row[0] for row in result]
            backup_logger.info("Found tables: {}".format(", ".join(tables)))

            # Check each table for data
            for table in tables:
                result = conn.execute(
                    text(
                        f"""
                    SELECT * FROM {table};
                """
                    )
                )
                rows = result.fetchall()
                count = len(rows)
                backup_logger.info("Table {} has {} rows".format(table, count))
                if count > 0:
                    backup_logger.info(
                        "Data in {}: {}".format(
                            table, [dict(row._mapping) for row in rows]
                        )
                    )
                    return False
            return True
    except Exception as e:
        backup_logger.error("Error checking tables: {}".format(e))
        return False


def drop_all_tables():
    """Drop all tables in database"""
    from sqlalchemy import text

    from flask_structured_api.core.db import engine

    try:
        with engine.connect() as conn:
            conn.execute(
                text(
                    """
                DROP SCHEMA public CASCADE;
                CREATE SCHEMA public;
                GRANT ALL ON SCHEMA public TO public;
            """
                )
            )
            conn.commit()
            backup_logger.info("✅ All tables dropped")
            return True
    except Exception as e:
        backup_logger.error(f"❌ Failed to drop tables: {e}")
        return False


def restore_database(backup_file=None, force=False):
    """Restore database from backup"""
    try:
        if not force and not check_tables_empty():
            backup_logger.warning("Database contains data! Use force=True to overwrite")
            return False

        required_vars = {
            "POSTGRES_HOST": os.getenv("POSTGRES_HOST", "db"),
            "POSTGRES_USER": os.getenv("POSTGRES_USER", "user"),
            "POSTGRES_DB": os.getenv("POSTGRES_DB", "api"),
            "POSTGRES_PASSWORD": os.getenv("POSTGRES_PASSWORD"),
        }

        if not backup_file:
            backups = sorted(BACKUP_DIR.glob("backup_*.sql*"))
            if not backups:
                raise Exception("No backup files found")
            backup_file = backups[-1]

        backup_logger.info("Restoring from: {}".format(backup_file))

        # Drop existing tables if they exist
        if not drop_all_tables():
            raise Exception("Failed to prepare database for restore")

        if str(backup_file).endswith(".gz"):
            with gzip.open(backup_file, "rb") as gz:
                process = subprocess.run(
                    [
                        "psql",
                        "-h",
                        required_vars["POSTGRES_HOST"],
                        "-U",
                        required_vars["POSTGRES_USER"],
                        "-d",
                        required_vars["POSTGRES_DB"],
                    ],
                    input=gz.read(),
                    capture_output=True,
                    check=True,
                    env={"PGPASSWORD": required_vars["POSTGRES_PASSWORD"]},
                )
        else:
            process = subprocess.run(
                [
                    "psql",
                    "-h",
                    required_vars["POSTGRES_HOST"],
                    "-U",
                    required_vars["POSTGRES_USER"],
                    "-d",
                    required_vars["POSTGRES_DB"],
                    "-f",
                    str(backup_file),
                ],
                capture_output=True,
                check=True,
                env={"PGPASSWORD": required_vars["POSTGRES_PASSWORD"]},
            )

        if process.returncode != 0:
            raise Exception(f"Restore failed: {process.stderr.decode()}")

        backup_logger.info("✅ Database restored successfully")
        return True

    except Exception as e:
        backup_logger.error(f"❌ Restore failed: {e}")
        return False


# Only run if called directly
if __name__ == "__main__":
    main()

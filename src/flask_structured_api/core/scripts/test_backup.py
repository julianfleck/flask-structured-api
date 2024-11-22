from flask_structured_api.core.scripts.backup_db import backup_database, cleanup_backups
from flask_structured_api.core.scripts.generate_crontab import generate_crontab
from flask_structured_api.core.utils.logger import system_logger
from pathlib import Path
import os


def test_backup_system():
    """Test the backup system functionality"""
    backup_dir = Path("/backups")

    # Test crontab generation
    generate_crontab()
    assert os.path.exists("/etc/crontabs/root"), "Crontab file not created"

    # Test backup creation
    backup_database()
    backups = list(backup_dir.glob("*.sql*"))
    assert len(backups) > 0, "No backup files created"

    system_logger.info("✅ Backup test completed successfully")
    system_logger.info("Created backup files: {}".format(
        [b.name for b in backups]))


if __name__ == "__main__":
    test_backup_system()

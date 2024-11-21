from flask_structured_api.core.config import settings
import re


def schedule_to_cron(schedule: str) -> str:
    """Convert schedule string to cron expression"""
    # Handle common macros
    macros = {
        "@yearly": "0 0 1 1 *",
        "@monthly": "0 0 1 * *",
        "@weekly": "0 0 * * 0",
        "@daily": "0 0 * * *",
        "@hourly": "0 * * * *"
    }

    if schedule in macros:
        return macros[schedule]

    # Return as-is if it's already a cron expression
    if re.match(r"^(\*|[0-9,\-*/]+\s){4}(\*|[0-9,\-*/]+)$", schedule):
        return schedule

    raise ValueError(f"Invalid schedule format: {schedule}")


def generate_crontab():
    """Generate crontab file with configured schedule"""
    cron_schedule = schedule_to_cron(settings.BACKUP_SCHEDULE)
    crontab = (
        f"{cron_schedule} python -m app.scripts.backup_db >> /var/log/cron.log 2>&1\n"
    )

    with open("/etc/crontabs/root", "w") as f:
        f.write(crontab)


if __name__ == "__main__":
    generate_crontab()

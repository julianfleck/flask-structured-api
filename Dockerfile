# Base image with common dependencies
FROM python:3.11-slim as base

# Add build argument for environment
ARG ENVIRONMENT

# Install common required packages
RUN apt-get update && apt-get install -y \
    postgresql-client \
    redis-tools \
    cron \
    supervisor \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy requirements first
COPY requirements/ ./requirements/
RUN pip install -r requirements/base.txt && \
    if [ "$ENVIRONMENT" = "development" ] ; then \
        pip install -r requirements/dev.txt -r requirements/test.txt; \
    fi

# API image
FROM base as api
COPY . .
RUN pip install -e .

# Setup directories and permissions
RUN mkdir -p /var/log && \
    touch /var/log/flask.log /var/log/flask.err.log && \
    chmod -R 755 /var/log && \
    mkdir -p /etc/supervisor/conf.d && \
    cp docker/api/supervisord.conf /etc/supervisor/conf.d/

COPY docker/api/entrypoint.sh /app/docker/
RUN chmod +x /app/docker/api/entrypoint.sh
ENTRYPOINT ["/app/docker/api/entrypoint.sh"]

# Backup image
FROM base as backup
# Only copy what's needed for backups
COPY src/flask_structured_api/core/scripts/backup_db.py /app/src/flask_structured_api/core/scripts/
COPY src/flask_structured_api/core/config /app/src/flask_structured_api/core/config/
COPY docker/backup/crontab /app/docker/backup/

# Setup backup directories
RUN mkdir -p /backups /var/log && \
    touch /var/log/cron.log && \
    chmod -R 755 /backups /var/log

COPY docker/backup/entrypoint.sh /app/docker/backup/
RUN chmod +x /app/docker/backup/entrypoint.sh
ENTRYPOINT ["/app/docker/backup/entrypoint.sh"]
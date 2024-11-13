# Base image with common dependencies
FROM python:3.11-slim as base

# Add build argument for environment
ARG ENVIRONMENT=production

# Install common required packages
RUN apt-get update && apt-get install -y \
    postgresql-client \
    cron \
    supervisor \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy requirements first
COPY requirements.txt requirements-dev.txt ./

# Install base dependencies
RUN pip install -r requirements.txt

# Development dependencies if needed
RUN if [ "$ENVIRONMENT" = "development" ] ; then \
        echo "🔧 Installing development dependencies..." && \
        pip install -r requirements-dev.txt ; \
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
    cp /app/docker/supervisord.conf /etc/supervisor/conf.d/

# Verify debugpy installation for development
RUN if [ "$ENVIRONMENT" = "development" ] ; then \
        echo "🔍 Verifying debugpy installation..." && \
        pip list | grep debugpy || echo "❌ debugpy not found!" ; \
    fi

COPY docker/entrypoint.sh /app/docker/
RUN chmod +x /app/docker/entrypoint.sh
ENTRYPOINT ["/app/docker/entrypoint.sh"]

# Backup image
FROM base as backup
# Only copy what's needed for backups
COPY app/scripts/backup_db.py /app/app/scripts/
COPY app/core/config.py /app/app/core/
COPY docker/crontab /app/docker/

# Setup backup directories
RUN mkdir -p /backups /var/log && \
    touch /var/log/cron.log && \
    chmod -R 755 /backups /var/log

COPY docker/entrypoint.backup.sh /app/docker/
RUN chmod +x /app/docker/entrypoint.backup.sh
ENTRYPOINT ["/app/docker/entrypoint.backup.sh"]
# Base image with common dependencies
FROM python:3.11-slim as base

# Add build argument for environment
ARG ENVIRONMENT

# Install common required packages more efficiently
RUN apt-get update && apt-get install -y --no-install-recommends \
    postgresql-client \
    redis-tools \
    cron \
    supervisor \
    libmagic1 \
    poppler-utils \
    dos2unix \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

WORKDIR /app

# Copy only requirements first to leverage cache
COPY requirements/ ./requirements/
RUN pip install --no-cache-dir -r requirements/base.txt \
    && pip install --no-cache-dir -r requirements/stip.txt \
    && rm -rf ~/.cache/pip/*

# Development stage
FROM base as development
RUN pip install --no-cache-dir -r requirements/dev.txt \
    && rm -rf ~/.cache/pip/*

# Common setup for both api and backup
FROM base as common

# Create necessary directories
RUN mkdir -p /app/src

# Copy the entire project
COPY . . 
ENV PYTHONPATH=/app/src
RUN pip install -e .

# API image
FROM common as api
RUN mkdir -p /var/log && \
    touch /var/log/flask.log /var/log/flask.err.log && \
    chmod -R 755 /var/log && \
    mkdir -p /etc/supervisor/conf.d

COPY docker/api/supervisord.conf /etc/supervisor/conf.d/
COPY docker/api/entrypoint.sh /app/docker/api/
RUN dos2unix /app/docker/api/entrypoint.sh && \
    chmod +x /app/docker/api/entrypoint.sh

ENTRYPOINT ["/bin/sh", "/app/docker/api/entrypoint.sh"]

# Backup image
FROM common as backup
COPY docker/backup/crontab /app/docker/backup/
COPY docker/backup/entrypoint.sh /app/docker/backup/

RUN mkdir -p /backups /var/log && \
    touch /var/log/cron.log && \
    chmod -R 755 /backups /var/log && \
    chmod +x /app/docker/backup/entrypoint.sh

ENTRYPOINT ["/app/docker/backup/entrypoint.sh"]

# Production stage (uses api target by default)
FROM api as production

FROM python:3.11-slim

# Add build argument for environment
ARG ENVIRONMENT=production

# Install required packages
RUN apt-get update && apt-get install -y \
    postgresql-client \
    cron \
    supervisor \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy requirements first
COPY requirements.txt requirements-dev.txt ./

# Install dependencies and show what's being installed
RUN pip install --no-cache-dir -r requirements.txt && \
    if [ "$ENVIRONMENT" = "development" ] ; then \
        echo "🔧 Installing development dependencies..." && \
        pip install --no-cache-dir -r requirements-dev.txt && \
        pip list | grep debugpy || echo "❌ debugpy not found!" ; \
    fi

# Copy source code and setup files
COPY . .
RUN pip install -e .

# Verify debugpy installation after everything is set up
RUN if [ "$ENVIRONMENT" = "development" ] ; then \
        echo "🔍 Verifying debugpy installation..." && \
        pip list | grep debugpy || echo "❌ debugpy not found!" ; \
    fi

# Setup directories and permissions
RUN mkdir -p /var/log /backups \
    && touch /var/log/cron.log /var/log/flask.log /var/log/flask.err.log \
    && chmod -R 755 /var/log /backups \
    && mkdir -p /etc/supervisor/conf.d \
    && cp /app/docker/supervisord.conf /etc/supervisor/conf.d/

# Create crontab directory with proper permissions
RUN mkdir -p /etc/crontabs \
    && chmod -R 755 /etc/crontabs

# Set entrypoint permissions and make doubly sure it's executable
RUN chmod +x /app/docker/entrypoint.sh && \
    ls -l /app/docker/entrypoint.sh && \
    test -x /app/docker/entrypoint.sh

# Use shell form of ENTRYPOINT to ensure proper execution
ENTRYPOINT exec /app/docker/entrypoint.sh
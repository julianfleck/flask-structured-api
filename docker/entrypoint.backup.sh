#!/bin/bash
set -e

# Wait for database to be ready
echo "🔄 Waiting for database..."
while ! pg_isready -h db -U user -d api; do
    sleep 1
done

# Install crontab
echo "📅 Installing crontab..."
crontab /app/docker/crontab

# Start cron in foreground
echo "🚀 Starting cron..."
exec cron -f 
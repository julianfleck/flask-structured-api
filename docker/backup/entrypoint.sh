#!/bin/bash
set -e

# Wait for PostgreSQL
echo "🔄 Waiting for PostgreSQL..."
while ! pg_isready -h "${POSTGRES_HOST:-db}" -U "${POSTGRES_USER:-user}" -d "${POSTGRES_DB:-api}"; do
    sleep 1
done

# Setup environment in crontab
echo "📅 Setting up environment..."
printenv | grep -E '^(POSTGRES_|BACKUP_)' | sed 's/^\(.*\)$/export \1/g' > /root/backup.env
echo "source /root/backup.env" > /root/.profile

# Install crontab
echo "📅 Installing crontab..."
crontab /app/docker/backup/crontab

# Start cron in foreground
echo "🚀 Starting cron..."
exec cron -f

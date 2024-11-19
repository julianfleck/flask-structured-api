#!/bin/bash
set -e

# Wait for database to be ready
echo "🔄 Waiting for database..."
while ! pg_isready -h db -U user -d api; do
    sleep 1
done

# Wait for backup directory to be ready
echo "🔄 Waiting for backup directory..."
MAX_RETRIES=30
RETRY_COUNT=0
while [ ! -w "/backups" ] && [ $RETRY_COUNT -lt $MAX_RETRIES ]; do
    echo "⏳ Waiting for backup directory... ($(($MAX_RETRIES - $RETRY_COUNT)) attempts remaining)"
    sleep 1
    RETRY_COUNT=$((RETRY_COUNT + 1))
done

if [ ! -w "/backups" ]; then
    echo "⚠️ Backup directory not ready, skipping initial backup"
else
    # Create initial backup
    echo "💾 Creating initial backup..."
    python -m app.core.scripts.backup_db || echo "⚠️ Initial backup failed, continuing anyway..."
fi

# Run database migrations
echo "🔄 Setting up database..."
python -m app.core.scripts.init_db

# Start the application
echo "🚀 Starting application..."
exec supervisord -c /etc/supervisor/conf.d/supervisord.conf
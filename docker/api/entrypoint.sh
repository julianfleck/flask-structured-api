#!/bin/bash
set -e

# Wait for dependencies
echo "🔄 Waiting for PostgreSQL..."
until PGPASSWORD=$POSTGRES_PASSWORD psql -h "db" -U "$POSTGRES_USER" -d "$POSTGRES_DB" -c '\q'; do
  sleep 1
done

echo "🔄 Waiting for Redis..."
until redis-cli -h redis ping; do
  sleep 1
done

# Wait for backup directory
echo "🔄 Checking backup directory..."
if [ -w "/backups" ]; then
    echo "💾 Creating initial backup..."
    if python -Xfrozen_modules=off -m flask_structured_api.core.scripts.run backup_db; then
        echo "✅ Initial backup completed"
    fi
fi

# Run database migrations
echo "🔄 Setting up database..."
if python -Xfrozen_modules=off -m flask_structured_api.core.scripts.run init_db; then
    echo "✅ Database setup completed"
else
    echo "❌ Database setup failed"
    exit 1
fi

# Start services based on environment
if [ "$ENVIRONMENT" = "development" ]; then
    echo "🚀 Starting development server..."
    export PYTHONPATH=/app/src
    export PYDEVD_DISABLE_FILE_VALIDATION=1
    exec python -Xfrozen_modules=off \
        -m flask run \
        --host=0.0.0.0 \
        --port=$API_PORT \
        --debug \
        # --no-reload
else
    echo "🚀 Starting production services..."
    exec supervisord -c /etc/supervisor/conf.d/supervisord.conf
fi 
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

# Initialize database and run migrations
echo "🔄 Setting up database..."
if python -m flask_structured_api.core.scripts.init_db; then
    echo "✅ Database setup completed"
else
    echo "❌ Database setup failed"
    exit 1
fi

# Start services based on environment
if [ "$ENVIRONMENT" = "development" ]; then
    echo "🚀 Starting development server..."
    export PYTHONPATH=/app/src
    exec python -m flask run --host=0.0.0.0 --port=$API_PORT --debug
else
    echo "🚀 Starting production services..."
    exec supervisord -c /etc/supervisor/conf.d/supervisord.conf
fi 
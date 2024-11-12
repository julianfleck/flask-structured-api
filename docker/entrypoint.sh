#!/bin/bash
set -e

# Wait for database to be ready
echo "🔄 Waiting for database..."
while ! pg_isready -h db -U user -d api; do
    sleep 1
done

# Run database migrations
echo "🔄 Setting up database..."
python -m app.scripts.init_db

# Start the application
echo "🚀 Starting application..."
exec supervisord -c /etc/supervisor/conf.d/supervisord.conf
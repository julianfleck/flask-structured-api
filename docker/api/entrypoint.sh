#!/bin/sh
set -e

echo "🔍 Debug: Starting entrypoint script..."

# Print environment variables
echo "Environment variables:"
echo "- ENVIRONMENT: ${ENVIRONMENT:-development}"
echo "- API_PORT: ${API_PORT:-5000}"
echo "- PYTHONPATH: ${PYTHONPATH:-not set}"
echo "- POSTGRES_USER: ${POSTGRES_USER:-not set}"
echo "- POSTGRES_DB: ${POSTGRES_DB:-not set}"

# Suppress deprecation warnings
export PYTHONWARNINGS="ignore::DeprecationWarning"

# Suppress frozen modules warning
export PYDEVD_DISABLE_FILE_VALIDATION=1 

# Install package in development mode
echo "📦 Installing package..."
pip install -e /app || {
    echo "❌ Failed to install package"
    exit 1
}
echo "✅ Package installed successfully"

# Wait for dependencies using more portable commands
echo "🔄 Waiting for PostgreSQL..."
until PGPASSWORD=$POSTGRES_PASSWORD pg_isready -h "db" -U "$POSTGRES_USER" -d "$POSTGRES_DB"; do
  echo "PostgreSQL is unavailable - sleeping"
  sleep 1
done
echo "✅ PostgreSQL is ready"

echo "🔄 Waiting for Redis..."
until redis-cli -h redis ping; do
  echo "Redis is unavailable - sleeping"
  sleep 1
done
echo "✅ Redis is ready"

# Initialize database and run migrations
echo "🔄 Setting up database..."
python -m flask_structured_api.core.scripts.init_db || {
    echo "❌ Database setup failed"
    echo "Check logs above for database initialization errors"
    exit 1
}
echo "✅ Database setup completed"

# Start services based on environment
if [ "$ENVIRONMENT" = "development" ]; then
    echo "🚀 Starting development server with hot reload..."
    echo "Debug: Using development configuration"
    echo "- Bind address: 0.0.0.0:${API_PORT:-5000}"
    echo "- Reload directory: /app/src"
    export PYTHONPATH=/app/src
    echo "Starting Hypercorn..."
    exec hypercorn "flask_structured_api.main:app" \
        --bind "0.0.0.0:${API_PORT:-5000}" \
        --reload \
        --access-logfile - \
        --error-logfile - \
        --log-level DEBUG || {
            echo "❌ Failed to start Hypercorn"
            exit 1
        }
else
    echo "🚀 Starting production services..."
    echo "Debug: Using production configuration"
    echo "- Bind address: 0.0.0.0:${API_PORT:-5000}"
    echo "- Worker count: 4"
    echo "Starting Hypercorn..."
    exec hypercorn "flask_structured_api.main:app" \
        --bind "0.0.0.0:${API_PORT:-5000}" \
        --workers 4 \
        --access-logfile - \
        --error-logfile - \
        --log-level INFO || {
            echo "❌ Failed to start Hypercorn"
            exit 1
        }
fi

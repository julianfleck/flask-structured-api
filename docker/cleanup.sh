#!/bin/bash

echo "🧹 Starting Docker cleanup..."

# Stop all running containers
echo "⏹️ Stopping containers..."
docker-compose down

# Remove unused Docker resources but preserve named volumes
echo "🗑️ Removing unused Docker resources..."
docker system prune -af

# Clean up builder cache
echo "🧼 Cleaning builder cache..."
docker builder prune -af

# Optional: Clean specific volumes while preserving data
echo "📦 Cleaning temporary volumes..."
docker volume ls -qf dangling=true | xargs -r docker volume rm

# Optimize Postgres (requires container to be running)
echo "🐘 Optimizing Postgres..."
docker-compose up -d db
sleep 5  # Wait for DB to start
docker-compose exec db vacuumdb -U ${POSTGRES_USER:-user} -d ${POSTGRES_DB:-api} --analyze
docker-compose down
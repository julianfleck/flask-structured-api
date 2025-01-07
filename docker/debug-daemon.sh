#!/bin/bash

echo "🔍 Debugging Docker on macOS..."

# Check Docker Desktop VM status
echo "📊 Docker Desktop VM status:"
ps aux | grep docker

# Check Docker Desktop resources
echo "💻 Resource allocation:"
docker run --rm busybox free -m

# Try to reset Docker Desktop networking
echo "🌐 Resetting Docker networking..."
docker network prune -f

# Clean everything except volumes
echo "🧹 Deep cleaning..."
docker system prune -af --volumes

# Optional: Reset Docker Desktop
echo "🔄 Would you like to reset Docker Desktop? (y/N)"
read -r response
if [[ "$response" =~ ^([yY][eE][sS]|[yY])+$ ]]; then
    osascript -e 'quit app "Docker"'
    sleep 5
    open -a Docker
    echo "⏳ Waiting for Docker to restart..."
    until docker info > /dev/null 2>&1; do
        sleep 1
    done
    echo "✅ Docker Desktop restarted"
fi
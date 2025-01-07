#!/bin/bash

echo "🔍 Testing minimal build..."

# Create minimal test Dockerfile
cat > Dockerfile.minimal << 'EOF'
FROM python:3.11-slim
WORKDIR /app
COPY requirements/base.txt requirements/
RUN pip install -r requirements/base.txt
EOF

# Try building with different settings
echo "🚀 Building with BuildKit disabled..."
DOCKER_BUILDKIT=0 docker build -f Dockerfile.minimal -t test-build .

echo "🚀 Building with BuildKit enabled..."
DOCKER_BUILDKIT=1 docker build -f Dockerfile.minimal -t test-build .

# Cleanup
rm Dockerfile.minimal 
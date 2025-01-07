#!/bin/bash

echo "🔍 Testing Docker context..."

# Create temporary Dockerfile
echo "FROM busybox
COPY . /app
WORKDIR /app
RUN find . -type f" > Dockerfile.test

# Build with debug output
DOCKER_BUILDKIT=0 docker build -f Dockerfile.test -t test-context . 2>&1 | grep "COPY"

# Cleanup
rm Dockerfile.test 
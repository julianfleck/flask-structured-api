#!/bin/bash
set -e

echo "🏗️  Building API image for AMD64..."
docker buildx build --platform linux/amd64 \
  -t gcr.io/windy-augury-442117-b9/api:latest \
  --target production \
  --push \
  .

echo "🚀 Starting redeployment..."
./k8s/redeploy.sh

echo "📝 Following API logs..."
kubectl logs -f deployment/api 
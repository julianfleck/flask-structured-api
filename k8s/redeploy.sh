#!/bin/bash
# redeploy.sh
set -e

echo "🔍 Current state before cleanup:"
kubectl get pods,pvc,pv,statefulset

echo "🧹 Cleaning up deployments, statefulsets and pods..."
kubectl delete deployment redis api --ignore-not-found
kubectl delete statefulset postgres --ignore-not-found
kubectl delete pods --all --force --grace-period=0 --ignore-not-found

echo "💣 Double-checking for stuck pods..."
for pod in $(kubectl get pods --no-headers | grep -E "Terminating|Error" | awk '{print $1}'); do
    echo "Force deleting pod $pod..."
    kubectl delete pod $pod --force --grace-period=0
    kubectl patch pod $pod -p '{"metadata":{"finalizers":null}}'
done

echo "⏳ Brief pause for cleanup..."
sleep 5

echo "🔄 Applying secrets and configurations..."
kubectl apply -f k8s/base/secrets.yaml
kubectl apply -f k8s/base/storage.yaml
sleep 2

echo "🔄 Applying services..."
kubectl apply -f k8s/base/postgres-service.yaml
kubectl apply -f k8s/base/redis-service.yaml

echo "🔄 Applying deployments and statefulsets..."
kubectl apply -f k8s/base/postgres.yaml
kubectl apply -f k8s/base/redis.yaml
kubectl apply -f k8s/base/api.yaml

echo "⏳ Waiting for core services (60s timeout)..."
timeout 60 kubectl wait --for=condition=ready pod -l app=postgres --timeout=60s || true
timeout 40 kubectl wait --for=condition=ready pod -l app=redis --timeout=40s || true

echo "🔍 Verifying environment variables..."
echo "Checking API pod environment:"
API_POD=$(kubectl get pod -l app=api -o jsonpath='{.items[0].metadata.name}')
kubectl exec $API_POD -- env | grep -E "CELERY|REDIS"

echo "🔍 Current state:"
kubectl get pods,pvc,pv,statefulset

echo "📝 Postgres Logs:"
kubectl logs -l app=postgres --tail=20 || true

echo "🔄 Final API restart..."
kubectl rollout restart deployment api

echo "🎉 Deployment completed!"

echo "🔍 API Logs:"
kubectl logs -f deployment/api

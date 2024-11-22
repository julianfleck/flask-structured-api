# Core API Endpoints

This document details the core API endpoints that provide essential system functionality and monitoring capabilities.

## Health Check

### `GET /health`

Returns the current health status of the system and its components.

```python
# Request
GET /health
```

```python
# Response 200 OK
{
    "status": "healthy",
    "details": {
        "database": "healthy",
        "redis": "healthy",
        "ai_service": "healthy",
        "version": "1.0.0",
        "environment": "production"
    }
}
```

## Metrics

### `GET /metrics`

Returns Prometheus-formatted metrics about system performance and usage.

```python
# Request
GET /metrics
```

```text
# Response 200 OK
# HELP request_total Total request count
# TYPE request_total counter
request_total{method="GET",endpoint="/api/v1/health",status="200"} 42

# HELP request_latency_seconds Request latency
# TYPE request_latency_seconds histogram
request_latency_seconds_bucket{method="GET",endpoint="/api/v1/health",le="0.1"} 35
request_latency_seconds_bucket{method="GET",endpoint="/api/v1/health",le="0.5"} 40
request_latency_seconds_bucket{method="GET",endpoint="/api/v1/health",le="1.0"} 42

# HELP ai_request_total Total AI request count
# TYPE ai_request_total counter
ai_request_total{provider="openai",model="gpt-4",status="success"} 100
```

## Version Info

### `GET /version`

Returns detailed version information about the API.

```python
# Request
GET /version
```

```python
# Response 200 OK
{
    "version": "1.0.0",
    "api_versions": {
        "v1": {
            "status": "stable",
            "released": "2024-01-01T00:00:00Z"
        },
        "v2": {
            "status": "beta",
            "released": "2024-06-01T00:00:00Z"
        }
    },
    "environment": "production",
    "build_info": {
        "git_commit": "abc123",
        "build_date": "2024-01-01T00:00:00Z"
    }
}
```

## Status

### `GET /status`

Returns the current system status and performance metrics.

```python
# Request
GET /status
```

```python
# Response 200 OK
{
    "status": "operational",
    "uptime": "5d 12h 34m",
    "load": {
        "cpu": 45.2,
        "memory": 62.8,
        "disk": 38.1
    },
    "response_times": {
        "p50": 120,
        "p95": 350,
        "p99": 600
    },
    "active_connections": 42,
    "error_rate": 0.01
}
```

## Rate Limits

All core endpoints use the following rate limits:

| Endpoint | Rate Limit | Burst |
|----------|------------|--------|
| `/health` | 60/minute | 100 |
| `/metrics` | 10/minute | 20 |
| `/version` | 60/minute | 100 |
| `/status` | 60/minute | 100 |

Rate limit headers are included in all responses:
```
X-RateLimit-Limit: 60
X-RateLimit-Remaining: 59
X-RateLimit-Reset: 1699700000
```

## Error Responses

Core endpoints use standard error responses:

```python
# Response 503 Service Unavailable
{
    "success": false,
    "message": "Service unhealthy",
    "error": {
        "code": "service_unhealthy",
        "details": {
            "component": "database",
            "reason": "connection_failed"
        }
    }
}
```

## Monitoring Integration

Core endpoints support standard monitoring tools:

- Prometheus metrics scraping
- Health check integration for load balancers
- Status page integration
- Logging in JSON format

## Usage Example

```python
import requests
import time

def monitor_health():
    while True:
        response = requests.get("http://api.example.com/health")
        status = response.json()
        
        if status["status"] != "healthy":
            print(f"Service unhealthy: {status['details']}")
        
        time.sleep(60)  # Check every minute
```

For more details on monitoring and maintenance, see the [Architecture Documentation](../architecture/README.md).
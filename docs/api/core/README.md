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

Reference implementation:

````1603:1659:README-full.md
# app/core/health.py
from dataclasses import dataclass
from typing import Dict, Any
from redis import Redis
from sqlalchemy import text
from app.core.db import engine
from app.core.ai import AIService

@dataclass
class HealthStatus:
    status: str
    details: Dict[str, Any]
    
    @property
    def is_healthy(self) -> bool:
        return self.status == "healthy"

class HealthChecker:
    def check_database(self) -> bool:
        try:
            with engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            return True
        except Exception:
            return False

    def check_redis(self) -> bool:
        try:
            redis = Redis.from_url(settings.REDIS_URL)
            return redis.ping()
        except Exception:
            return False

    def check_ai_service(self) -> bool:
        try:
            return AIService().test_connection()
        except Exception:
            return False

    def get_status(self) -> HealthStatus:
        db_healthy = self.check_database()
        redis_healthy = self.check_redis()
        ai_healthy = self.check_ai_service()
        
        all_healthy = all([db_healthy, redis_healthy, ai_healthy])
        
        return HealthStatus(
            status="healthy" if all_healthy else "unhealthy",
            details={
                "database": "healthy" if db_healthy else "unhealthy",
                "redis": "healthy" if redis_healthy else "unhealthy",
                "ai_service": "healthy" if ai_healthy else "unhealthy",
                "version": settings.API_VERSION,
                "environment": settings.ENVIRONMENT
            }
        )
```
````


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

Reference implementation:

````1664:1750:README-full.md
# app/core/metrics.py
from prometheus_client import Counter, Histogram, Info
from functools import wraps
import time

# Metrics
REQUEST_COUNT = Counter(
    'request_total',
    'Total request count',
    ['method', 'endpoint', 'status']
)

REQUEST_LATENCY = Histogram(
    'request_latency_seconds',
    'Request latency',
    ['method', 'endpoint']
)

AI_REQUEST_COUNT = Counter(
    'ai_request_total',
    'Total AI request count',
    ['provider', 'model', 'status']
)

AI_TOKEN_COUNT = Counter(
    'ai_token_total',
    'Total AI tokens used',
    ['provider', 'model']
)

# Decorators
def track_request_metrics():
    def decorator(f):
        @wraps(f)
        def wrapped(*args, **kwargs):
            start_time = time.time()
            try:
                response = f(*args, **kwargs)
                status = response.status_code
            except Exception as e:
                status = 500
                raise e
            finally:
                REQUEST_COUNT.labels(
                    method=request.method,
                    endpoint=request.endpoint,
                    status=status
                ).inc()
                
                REQUEST_LATENCY.labels(
                    method=request.method,
                    endpoint=request.endpoint
                ).observe(time.time() - start_time)
            
            return response
        return wrapped
    return decorator

def track_ai_metrics():
    def decorator(f):
        @wraps(f)
        async def wrapped(*args, **kwargs):
            try:
                response = await f(*args, **kwargs)
                AI_REQUEST_COUNT.labels(
                    provider=kwargs.get('provider', 'default'),
                    model=kwargs.get('model', 'default'),
                    status='success'
                ).inc()
                
                if hasattr(response, 'usage'):
                    AI_TOKEN_COUNT.labels(
                        provider=kwargs.get('provider', 'default'),
                        model=kwargs.get('model', 'default')
                    ).inc(response.usage.get('total_tokens', 0))
                
                return response
            except Exception as e:
                AI_REQUEST_COUNT.labels(
                    provider=kwargs.get('provider', 'default'),
                    model=kwargs.get('model', 'default'),
                    status='error'
                ).inc()
                raise e
        return wrapped
    return decorator
```
````


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

Reference implementation:

````2324:2396:README-full.md
### 8.2 API Versioning

```python
# app/core/versioning.py
from dataclasses import dataclass
from typing import Dict, Set
from datetime import datetime

@dataclass
class APIVersion:
    version: str
    released: datetime
    supported: bool
    sunset_date: Optional[datetime] = None
    
    @property
    def is_deprecated(self) -> bool:
        return self.sunset_date is not None

class VersionManager:
    VERSIONS: Dict[str, APIVersion] = {
        'v1': APIVersion(
            version='v1',
            released=datetime(2024, 1, 1),
            supported=True
        ),
        'v2': APIVersion(
            version='v2',
            released=datetime(2024, 6, 1),
            supported=True
        ),
        'v0': APIVersion(
            version='v0',
            released=datetime(2023, 1, 1),
            supported=False,
            sunset_date=datetime(2024, 1, 1)
        )
    }
    
    @classmethod
    def get_supported_versions(cls) -> Set[str]:
        return {
            v.version
            for v in cls.VERSIONS.values()
            if v.supported
        }
    
    @classmethod
    def get_latest_version(cls) -> str:
        supported = sorted([
            v for v in cls.VERSIONS.values()
            if v.supported
        ], key=lambda x: x.released, reverse=True)
        return supported[0].version if supported else None

# Middleware for version handling
@app.before_request
def handle_version():
    version = request.headers.get('API-Version')
    if not version:
        version = VersionManager.get_latest_version()
    
    if version not in VersionManager.get_supported_versions():
        raise APIError(
            message=f"API version {version} not supported",
            details={
                'supported_versions': list(VersionManager.get_supported_versions()),
                'latest_version': VersionManager.get_latest_version()
            }
        )
    
    g.api_version = version
```
````


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

Reference implementation:

````1754:1798:README-full.md
```python
# app/core/logging.py
import logging
import json
from datetime import datetime
from pythonjsonlogger import jsonlogger

class CustomJsonFormatter(jsonlogger.JsonFormatter):
    def add_fields(self, log_record, record, message_dict):
        super(CustomJsonFormatter, self).add_fields(log_record, record, message_dict)
        log_record['timestamp'] = datetime.utcnow().isoformat()
        log_record['level'] = record.levelname
        log_record['environment'] = settings.ENVIRONMENT

def setup_logging():
    logger = logging.getLogger()
    handler = logging.StreamHandler()
    formatter = CustomJsonFormatter(
        '%(timestamp)s %(level)s %(name)s %(message)s'
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(settings.LOG_LEVEL)

    # Add request ID to all logs within a request
    @app.before_request
    def before_request():
        g.request_id = request.headers.get('X-Request-ID') or str(uuid.uuid4())
        
    # Log all requests
    @app.after_request
    def after_request(response):
        logger.info(
            'Request processed',
            extra={
                'request_id': g.request_id,
                'method': request.method,
                'path': request.path,
                'status': response.status_code,
                'duration': g.get('request_duration'),
                'ip': request.remote_addr
            }
        )
        return response
```
````


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
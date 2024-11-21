# Deployment Guide

This guide covers the essential steps to deploy the Flask API Boilerplate in production.

## Quick Start (Docker)

1. Clone and configure:
```bash
git clone https://github.com/your/repo.git
cd repo
cp .env.example .env.prod
```

2. Configure essential environment variables in `.env.prod`:
```env
# Required
DATABASE_URL=postgresql://user:secure_password@db:5432/api_prod
REDIS_URL=redis://redis:6379/0
SECRET_KEY=your-very-secure-secret-key
JWT_SECRET_KEY=your-very-secure-jwt-key

# Optional but recommended
RATE_LIMIT_ENABLED=true
AI_PROVIDER=openai
AI_API_KEY=your-production-api-key
```

3. Deploy with Docker:
```bash
# Build and start services
docker-compose --workdir /app/src -f docker-compose.prod.yml up -d

# Run migrations and create admin
docker-compose --workdir /app/src -f docker-compose.prod.yml exec api flask db upgrade
docker-compose --workdir /app/src -f docker-compose.prod.yml exec api flask users create-admin
```

## Local Development

1. Install dependencies:
```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

2. Configure `.env`:
```env
DATABASE_URL=postgresql://user:password@localhost:5432/api_dev
REDIS_URL=redis://localhost:6379/0
SECRET_KEY=dev-secret-key
JWT_SECRET_KEY=dev-jwt-key
```

3. Run the application:
```bash
flask run --debug
```

## Advanced Configuration

For production deployments, consider these additional settings:

```env
# Performance
GUNICORN_WORKERS=4
GUNICORN_THREADS=2
DB_POOL_SIZE=20
REDIS_MAX_CONNECTIONS=100

# Security
CORS_ORIGINS=https://your-frontend.com
ALLOWED_HOSTS=api.your-domain.com
SSL_CERT_PATH=/etc/certs/fullchain.pem
SSL_KEY_PATH=/etc/certs/privkey.pem

# Monitoring
LOG_LEVEL=INFO
SENTRY_DSN=your-sentry-dsn
PROMETHEUS_ENABLED=true
```

## Production Checklist

Essential steps before going live:

- [ ] Set strong SECRET_KEY and JWT_SECRET_KEY
- [ ] Enable HTTPS/TLS
- [ ] Configure proper CORS settings
- [ ] Enable rate limiting
- [ ] Set up logging
- [ ] Configure database backups
- [ ] Set up monitoring

## Troubleshooting

Common issues and solutions:

### Database Connection Failed
```python
# Verify connection
import psycopg2
from app.core.config import settings

def test_db():
    try:
        conn = psycopg2.connect(settings.DATABASE_URL)
        print("Database connection successful")
    except Exception as e:
        print(f"Database connection failed: {e}")
```

### Memory Issues
```bash
# Monitor container memory
docker stats api_container
```

For more detailed configuration options and deployment scenarios, see the [Architecture Documentation](../architecture/README.md).
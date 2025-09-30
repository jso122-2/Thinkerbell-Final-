# Railway Environment Variables Configuration

Set these environment variables in your Railway project dashboard:

## Core Application Settings
```
THINKERBELL_ENV=production
PORT=8000
HOST=0.0.0.0
```

## Model Configuration
```
THINKERBELL_MODEL_DIR=/app/models/thinkerbell-encoder-best
```

## Python Settings
```
PYTHONUNBUFFERED=1
PYTHONDONTWRITEBYTECODE=1
```

## Performance Settings
```
WEB_CONCURRENCY=2
MAX_WORKERS=2
```

## Railway-specific optimizations
```
RAILWAY_STATIC_URL=https://your-app.railway.app
RAILWAY_PUBLIC_DOMAIN=your-app.railway.app
```

## Optional: External Services
```
# REDIS_URL=redis://your-redis-url:6379
# DATABASE_URL=postgresql://user:pass@host:port/db
```

## How to Set Environment Variables in Railway:
1. Go to your Railway project dashboard
2. Click on your service
3. Go to the "Variables" tab
4. Add each variable name and value
5. Deploy your changes

## Railway CLI Method:
```bash
# Install Railway CLI
npm install -g @railway/cli

# Login to Railway
railway login

# Set environment variables
railway variables set THINKERBELL_ENV=production
railway variables set PORT=8000
railway variables set HOST=0.0.0.0
railway variables set THINKERBELL_MODEL_DIR=/app/models/thinkerbell-encoder-best
railway variables set PYTHONUNBUFFERED=1
railway variables set PYTHONDONTWRITEBYTECODE=1
railway variables set WEB_CONCURRENCY=1

# Deploy
railway up
```

## Production Security Variables:
```
# Add these for production security
CORS_ORIGINS=https://yourdomain.com,https://www.yourdomain.com
API_KEY_REQUIRED=false
RATE_LIMIT_ENABLED=true
RATE_LIMIT_REQUESTS=100
RATE_LIMIT_WINDOW=3600
```

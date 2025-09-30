# Railway Deployment Guide for Thinkerbell

## Prerequisites
- GitHub repository with your Thinkerbell code
- Railway account (free tier available)
- Model files committed to your repository (or use Git LFS for large files)

## Step 1: Prepare Your Repository

### 1.1 Ensure Required Files
Make sure these files are in your repository root:
- `backend_api_server.py` (main application)
- `requirements_production.txt` (dependencies)
- `Dockerfile.railway` (Railway-optimized Docker config)
- `railway.toml` (Railway configuration)
- `models/` directory with your trained model

### 1.2 Git LFS for Large Model Files (Recommended)
```bash
# Initialize Git LFS
git lfs install

# Track model files
git lfs track "models/**/*.safetensors"
git lfs track "models/**/*.bin"
git lfs track "models/**/*.pt"

# Add and commit
git add .gitattributes
git add models/
git commit -m "Add model files with Git LFS"
git push origin main
```

## Step 2: Deploy to Railway

### 2.1 Connect GitHub Repository
1. Go to [Railway.app](https://railway.app)
2. Sign up/Login with GitHub
3. Click "New Project"
4. Select "Deploy from GitHub repo"
5. Choose your Thinkerbell repository

### 2.2 Configure Railway Settings

#### Build Configuration:
- **Builder**: Dockerfile
- **Dockerfile Path**: `Dockerfile.railway`
- **Build Command**: (leave empty - Docker handles this)

#### Deploy Configuration:
- **Start Command**: `python backend_api_server.py`
- **Port**: `8000` (Railway will auto-detect from $PORT)
- **Health Check Path**: `/health`
- **Health Check Timeout**: `300` seconds

### 2.3 Set Environment Variables
In Railway dashboard → Your Service → Variables tab, add:

```
THINKERBELL_ENV=production
PORT=8000
HOST=0.0.0.0
THINKERBELL_MODEL_DIR=/app/models/thinkerbell-encoder-best
PYTHONUNBUFFERED=1
PYTHONDONTWRITEBYTECODE=1
WEB_CONCURRENCY=1
```

## Step 3: Railway-Specific Optimizations

### 3.1 Resource Limits (Railway Free Tier)
- **Memory**: 512MB - 1GB
- **CPU**: Shared vCPU
- **Execution Time**: 500 hours/month (free tier)
- **Build Time**: 10 minutes max

### 3.2 Optimize for Railway Constraints

#### Memory Optimization:
```python
# In your backend_api_server.py, add memory monitoring
import psutil
import os

def get_memory_usage():
    process = psutil.Process(os.getpid())
    return process.memory_info().rss / 1024 / 1024  # MB

# Add to health endpoint
@app.get("/health")
async def health():
    memory_mb = get_memory_usage()
    return {
        "status": "healthy",
        "memory_usage_mb": memory_mb,
        "model_loaded": model_service.model is not None
    }
```

#### Startup Optimization:
```python
# Lazy load heavy models
class ModelService:
    def __init__(self):
        self.model = None
        self._model_loading = False
    
    def ensure_model_loaded(self):
        if not self.model and not self._model_loading:
            self._model_loading = True
            self.load_model()
            self._model_loading = False
```

### 3.3 Domain Configuration
1. Railway provides a free domain: `your-app.railway.app`
2. For custom domain:
   - Go to Settings → Domains
   - Add your custom domain
   - Configure DNS CNAME record

## Step 4: Frontend Deployment Options

### Option A: Deploy Frontend Separately
1. Create new Railway service for frontend
2. Use Node.js buildpack
3. Set build command: `npm run build`
4. Set start command: `npm run preview`

### Option B: Serve Frontend from Backend
```python
# Add to backend_api_server.py
from fastapi.staticfiles import StaticFiles

# Serve built frontend
app.mount("/", StaticFiles(directory="thinkerbell/dist", html=True), name="static")
```

## Step 5: Monitoring and Logs

### 5.1 View Logs
```bash
# Install Railway CLI
npm install -g @railway/cli

# Login and view logs
railway login
railway logs
```

### 5.2 Health Monitoring
Railway automatically monitors your `/health` endpoint:
- **Healthy**: Returns 200 status
- **Unhealthy**: Returns non-200 or times out
- **Auto-restart**: Railway restarts unhealthy services

## Step 6: Production Optimizations

### 6.1 Enable Railway Pro Features (Optional)
- **Persistent Storage**: For model caching
- **Custom Metrics**: Advanced monitoring
- **Priority Support**: Faster builds
- **Higher Limits**: More memory/CPU

### 6.2 Performance Tuning
```yaml
# railway.toml
[build]
builder = "dockerfile"

[deploy]
startCommand = "python backend_api_server.py"
healthcheckPath = "/health"
healthcheckTimeout = 300
restartPolicyType = "always"

[environments.production]
variables = { 
  THINKERBELL_ENV = "production",
  WEB_CONCURRENCY = "1",
  MAX_WORKERS = "1"
}
```

## Troubleshooting

### Common Issues:

1. **Build Timeout**: Model files too large
   - Solution: Use Git LFS or external model storage

2. **Memory Limit Exceeded**: Model too large for Railway
   - Solution: Use smaller model or optimize loading

3. **Slow Cold Starts**: Model loading takes time
   - Solution: Implement model warming endpoint

4. **Port Binding Issues**: Not using Railway's $PORT
   - Solution: Ensure `HOST=0.0.0.0` and `PORT=$PORT`

### Debug Commands:
```bash
# Check Railway status
railway status

# View environment variables
railway variables

# Connect to service shell
railway shell
```

## Cost Estimation

### Railway Free Tier:
- 500 execution hours/month
- 1GB RAM
- 1GB disk
- Community support

### Railway Pro ($5/month):
- Unlimited execution hours
- Up to 8GB RAM
- 100GB disk
- Priority support
- Custom domains included

## Security Considerations

1. **Environment Variables**: Never commit secrets to Git
2. **CORS Configuration**: Restrict origins in production
3. **API Rate Limiting**: Implement rate limiting for public APIs
4. **HTTPS**: Railway provides free SSL certificates
5. **Model Security**: Ensure model files are properly secured

## Next Steps After Deployment

1. **Custom Domain**: Configure your domain
2. **Monitoring**: Set up uptime monitoring
3. **Analytics**: Add usage analytics
4. **Backup**: Regular model and data backups
5. **CI/CD**: Automate deployments with GitHub Actions

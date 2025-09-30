# 🐳 Docker Hub Deployment Guide

Complete guide for pushing Thinkerbell to Docker Hub and deploying from there.

## 🚀 Quick Start

### 1. Push to Docker Hub

```bash
# Set your Docker Hub username
export DOCKER_HUB_USERNAME="your-dockerhub-username"

# Build and push to Docker Hub
./docker-hub-deploy.sh --username $DOCKER_HUB_USERNAME --tag latest --version 1.0.0

# Or with multi-architecture support
./docker-hub-deploy.sh --username $DOCKER_HUB_USERNAME --multi-arch --tag production
```

### 2. Deploy from Docker Hub

```bash
# Use the generated Docker Hub compose file
docker compose -f docker-compose.hub.yml up -d

# Or run standalone
docker run -p 8000:8000 your-dockerhub-username/thinkerbell:latest
```

## 📋 Prerequisites

### Docker Hub Account
1. Create account at [hub.docker.com](https://hub.docker.com)
2. Create access token (recommended):
   - Go to Account Settings → Security
   - Create new Access Token
   - Export as environment variable:
     ```bash
     export DOCKER_HUB_TOKEN="your-access-token"
     ```

### Local Setup
```bash
# Ensure Docker is running
docker --version
docker compose version

# Login to Docker Hub (if not using token)
docker login
```

## 🛠️ Deployment Options

### Option 1: Full Deployment
```bash
# Build, tag, and push everything
./docker-hub-deploy.sh --username myuser --repo thinkerbell --tag v1.0.0
```

### Option 2: Build Only (for testing)
```bash
# Build images locally without pushing
./docker-hub-deploy.sh --build-only --username myuser
```

### Option 3: Multi-Architecture
```bash
# Build for AMD64 and ARM64
./docker-hub-deploy.sh --username myuser --multi-arch --tag production
```

### Option 4: Push Existing Images
```bash
# Push already built images
./docker-hub-deploy.sh --push-only --username myuser --tag latest
```

## 🏷️ Image Tags

The script creates multiple tags for flexibility:

- `latest` - Latest stable release
- `v1.0.0` - Specific version number
- `production` - Production-ready build
- `v1.0.0-abc1234` - Version with git commit hash

## 📦 Using Docker Hub Images

### Docker Compose (Recommended)
```yaml
# docker-compose.hub.yml (auto-generated)
services:
  thinkerbell:
    image: your-username/thinkerbell:latest
    ports:
      - "8000:8000"
    environment:
      - THINKERBELL_ENV=production
```

### Docker Run
```bash
# Basic run
docker run -p 8000:8000 your-username/thinkerbell:latest

# With environment variables
docker run -p 8000:8000 \
  -e THINKERBELL_ENV=production \
  -e PORT=8000 \
  -v ./data:/app/data \
  -v ./logs:/app/logs \
  your-username/thinkerbell:latest
```

### Kubernetes Deployment
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: thinkerbell
spec:
  replicas: 3
  selector:
    matchLabels:
      app: thinkerbell
  template:
    metadata:
      labels:
        app: thinkerbell
    spec:
      containers:
      - name: thinkerbell
        image: your-username/thinkerbell:latest
        ports:
        - containerPort: 8000
        env:
        - name: THINKERBELL_ENV
          value: "production"
```

## 🔧 Configuration

### Environment Variables
```bash
# Required for deployment
export DOCKER_HUB_USERNAME="your-username"

# Optional
export DOCKER_HUB_TOKEN="your-access-token"
export DOCKER_HUB_REPO="thinkerbell"
export IMAGE_TAG="latest"
export VERSION="1.0.0"
```

### Script Options
```bash
./docker-hub-deploy.sh --help
```

Available options:
- `--username <username>` - Docker Hub username
- `--repo <repo>` - Repository name (default: thinkerbell)
- `--tag <tag>` - Image tag (default: latest)
- `--version <version>` - Version tag (default: 1.0.0)
- `--build-only` - Only build, don't push
- `--push-only` - Only push existing images
- `--multi-arch` - Build for multiple architectures
- `--help` - Show help message

## 🌐 Production Deployment

### Cloud Platforms

#### AWS ECS
```bash
# Create task definition with Docker Hub image
aws ecs register-task-definition --cli-input-json file://task-definition.json
```

#### Google Cloud Run
```bash
# Deploy to Cloud Run
gcloud run deploy thinkerbell \
  --image your-username/thinkerbell:latest \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated
```

#### Azure Container Instances
```bash
# Deploy to ACI
az container create \
  --resource-group myResourceGroup \
  --name thinkerbell \
  --image your-username/thinkerbell:latest \
  --ports 8000
```

### Docker Swarm
```bash
# Deploy as a service
docker service create \
  --name thinkerbell \
  --replicas 3 \
  --publish 8000:8000 \
  your-username/thinkerbell:latest
```

## 📊 Monitoring Docker Hub Images

### Image Information
```bash
# Check image details
docker inspect your-username/thinkerbell:latest

# View image layers
docker history your-username/thinkerbell:latest

# Check image size
docker images your-username/thinkerbell
```

### Security Scanning
```bash
# Scan for vulnerabilities (if available)
docker scout cves your-username/thinkerbell:latest
```

## 🔄 CI/CD Integration

### GitHub Actions
```yaml
name: Build and Push to Docker Hub
on:
  push:
    branches: [main]
    tags: ['v*']

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3
    
    - name: Build and push
      env:
        DOCKER_HUB_USERNAME: ${{ secrets.DOCKER_HUB_USERNAME }}
        DOCKER_HUB_TOKEN: ${{ secrets.DOCKER_HUB_TOKEN }}
      run: |
        ./docker-hub-deploy.sh --username $DOCKER_HUB_USERNAME --tag ${GITHUB_REF#refs/tags/}
```

### GitLab CI
```yaml
build:
  stage: build
  script:
    - ./docker-hub-deploy.sh --username $DOCKER_HUB_USERNAME --tag $CI_COMMIT_TAG
  only:
    - tags
```

## 🚨 Troubleshooting

### Common Issues

#### Authentication Failed
```bash
# Re-login to Docker Hub
docker logout
docker login

# Or use access token
echo $DOCKER_HUB_TOKEN | docker login --username $DOCKER_HUB_USERNAME --password-stdin
```

#### Build Failed
```bash
# Check Docker daemon
docker info

# Clean up build cache
docker builder prune

# Check disk space
df -h
```

#### Push Failed
```bash
# Check network connectivity
curl -I https://hub.docker.com

# Retry with verbose output
docker push your-username/thinkerbell:latest --debug
```

#### Image Too Large
```bash
# Check image size
docker images your-username/thinkerbell

# Use multi-stage builds (already implemented)
# Consider using .dockerignore to exclude unnecessary files
```

### Debug Commands
```bash
# Test local build
docker build -t test-thinkerbell .
docker run -p 8000:8000 test-thinkerbell

# Check running containers
docker ps

# View container logs
docker logs container-name

# Execute into container
docker exec -it container-name /bin/bash
```

## 📚 Best Practices

### Security
- Use access tokens instead of passwords
- Regularly update base images
- Scan images for vulnerabilities
- Use specific tags in production (not `latest`)

### Performance
- Use multi-stage builds (already implemented)
- Optimize layer caching
- Use `.dockerignore` file
- Consider image size vs functionality trade-offs

### Versioning
- Use semantic versioning (v1.0.0, v1.1.0, etc.)
- Tag with git commit hash for traceability
- Maintain `latest` tag for development
- Use specific tags for production deployments

## 🎯 Next Steps

1. **Push your first image**:
   ```bash
   ./docker-hub-deploy.sh --username your-username
   ```

2. **Test deployment**:
   ```bash
   docker run -p 8000:8000 your-username/thinkerbell:latest
   ```

3. **Set up automated builds** with CI/CD

4. **Configure monitoring** and alerts

5. **Plan scaling strategy** for production

---

**"Where scientific enquiry meets hardcore creativity – Measured Magic"** 🚀


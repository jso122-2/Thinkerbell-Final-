# 🐳 Thinkerbell Docker Deployment Guide

Complete guide for deploying Thinkerbell Legal Text Generator using Docker in production environments.

## 📋 Table of Contents

- [Prerequisites](#prerequisites)
- [Quick Start](#quick-start)
- [Architecture Overview](#architecture-overview)
- [Configuration](#configuration)
- [Deployment Options](#deployment-options)
- [Management](#management)
- [Monitoring](#monitoring)
- [Security](#security)
- [Troubleshooting](#troubleshooting)
- [Production Considerations](#production-considerations)

## 🔧 Prerequisites

### System Requirements

- **OS**: Linux (Ubuntu 20.04+ recommended), macOS, or Windows with WSL2
- **CPU**: 2+ cores (4+ recommended for production)
- **RAM**: 4GB minimum (8GB+ recommended for production)
- **Storage**: 10GB+ free space
- **Network**: Internet access for pulling images

### Software Requirements

```bash
# Docker Engine 20.10+
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Docker Compose 2.0+
sudo apt-get update
sudo apt-get install docker-compose-plugin

# Verify installation
docker --version
docker compose version
```

### User Permissions

```bash
# Add user to docker group (logout/login required)
sudo usermod -aG docker $USER

# Or run with sudo (not recommended for production)
```

## 🚀 Quick Start

### 1. Clone and Setup

```bash
# Clone repository
git clone <repository-url>
cd Thinkerbell

# Make scripts executable
chmod +x docker-deploy.sh docker-manage.sh

# Create necessary directories
mkdir -p logs data temp backups
```

### 2. Deploy Basic Setup

```bash
# Deploy core services (Thinkerbell + Nginx + Redis)
./docker-deploy.sh

# Or deploy with monitoring
./docker-deploy.sh --with-monitoring
```

### 3. Verify Deployment

```bash
# Check service status
./docker-manage.sh status

# Check health
./docker-manage.sh health

# View logs
./docker-manage.sh logs
```

### 4. Access Application

- **Web Application**: http://localhost/
- **API Server**: http://localhost:8000/
- **API Documentation**: http://localhost:8000/docs
- **Grafana Dashboard**: http://localhost:3000/ (admin/admin123)
- **Prometheus**: http://localhost:9090/

## 🏗️ Architecture Overview

### Service Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│     Nginx       │    │   Thinkerbell   │    │     Redis       │
│  Reverse Proxy  │◄──►│   Application   │◄──►│     Cache       │
│   Port: 80/443  │    │   Port: 8000    │    │   Port: 6379    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         │              ┌─────────────────┐              │
         │              │   Prometheus    │              │
         └──────────────►│   Monitoring   │◄─────────────┘
                        │   Port: 9090    │
                        └─────────────────┘
                                 │
                        ┌─────────────────┐
                        │     Grafana     │
                        │  Visualization  │
                        │   Port: 3000    │
                        └─────────────────┘
```

### Container Details

| Service | Image | Purpose | Resources |
|---------|-------|---------|-----------|
| thinkerbell | Custom | Main application | 2-4GB RAM, 1-2 CPU |
| nginx | nginx:alpine | Reverse proxy | 256MB RAM, 0.5 CPU |
| redis | redis:7-alpine | Caching | 512MB RAM, 0.5 CPU |
| prometheus | prom/prometheus | Monitoring | 1GB RAM, 0.5 CPU |
| grafana | grafana/grafana | Visualization | 512MB RAM, 0.5 CPU |

## ⚙️ Configuration

### Environment Variables

Create `.env` file for custom configuration:

```bash
# Application Settings
THINKERBELL_ENV=production
THINKERBELL_MODEL_DIR=/app/models/thinkerbell-encoder-best
PORT=8000
HOST=0.0.0.0

# Security
REDIS_PASSWORD=your_secure_password_here
GRAFANA_ADMIN_PASSWORD=your_admin_password_here

# Resource Limits
THINKERBELL_MAX_MEMORY=4g
THINKERBELL_MAX_CPU=2.0

# Logging
LOG_LEVEL=INFO
LOG_FORMAT=json
```

### Custom Configuration Files

#### Nginx Configuration
- `docker/nginx/nginx.conf` - Main Nginx configuration
- `docker/nginx/conf.d/thinkerbell.conf` - Virtual host configuration

#### Redis Configuration
- `docker/redis/redis.conf` - Redis server configuration

#### Monitoring Configuration
- `docker/prometheus/prometheus.yml` - Prometheus configuration
- `docker/grafana/provisioning/` - Grafana dashboards and datasources

### SSL/TLS Configuration

```bash
# Generate self-signed certificates (development)
mkdir -p docker/ssl
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout docker/ssl/thinkerbell.key \
  -out docker/ssl/thinkerbell.crt

# For production, use Let's Encrypt or your CA certificates
```

## 🚀 Deployment Options

### Option 1: Basic Deployment

```bash
# Core services only
docker-compose up -d thinkerbell nginx redis
```

### Option 2: Full Stack with Monitoring

```bash
# All services including monitoring
docker-compose --profile monitoring up -d
```

### Option 3: Custom Deployment

```bash
# Selective service deployment
docker-compose up -d thinkerbell  # Application only
docker-compose up -d nginx        # Add reverse proxy
docker-compose up -d redis        # Add caching
```

### Option 4: Production Deployment

```bash
# Use production deployment script
./docker-deploy.sh --with-monitoring

# Or with custom environment
env $(cat .env | xargs) ./docker-deploy.sh
```

## 🛠️ Management

### Daily Operations

```bash
# Start services
./docker-manage.sh start

# Stop services
./docker-manage.sh stop

# Restart services
./docker-manage.sh restart

# View status
./docker-manage.sh status

# View logs
./docker-manage.sh logs [service_name]

# Open shell in container
./docker-manage.sh shell [service_name]
```

### Maintenance Operations

```bash
# Update services
./docker-manage.sh update

# Backup data
./docker-manage.sh backup

# Restore from backup
./docker-manage.sh restore backup_20231201_120000.tar.gz

# Clean up resources
./docker-manage.sh cleanup

# Scale services
./docker-manage.sh scale thinkerbell 3
```

### Health Monitoring

```bash
# Check service health
./docker-manage.sh health

# Monitor resource usage
./docker-manage.sh monitor

# View detailed status
docker-compose ps
docker stats
```

## 📊 Monitoring

### Prometheus Metrics

Access Prometheus at http://localhost:9090/

Key metrics to monitor:
- `thinkerbell_requests_total` - Total API requests
- `thinkerbell_request_duration_seconds` - Request latency
- `thinkerbell_model_inference_duration_seconds` - Model inference time
- `thinkerbell_batch_jobs_total` - Batch processing jobs
- `container_memory_usage_bytes` - Memory usage
- `container_cpu_usage_seconds_total` - CPU usage

### Grafana Dashboards

Access Grafana at http://localhost:3000/ (admin/admin123)

Pre-configured dashboards:
- **Thinkerbell Overview** - Application metrics
- **System Resources** - Container resource usage
- **API Performance** - Request metrics and latency
- **Model Performance** - ML model inference metrics

### Log Management

```bash
# View application logs
docker-compose logs -f thinkerbell

# View all logs
docker-compose logs -f

# Export logs
docker-compose logs --no-color > thinkerbell.log

# Log rotation (add to crontab)
0 0 * * * docker-compose logs --no-color --tail=1000 > /backup/logs/thinkerbell-$(date +\%Y\%m\%d).log
```

## 🔒 Security

### Network Security

```bash
# Use custom network
docker network create thinkerbell-secure

# Restrict external access
# Edit docker-compose.yml to remove port mappings for internal services
```

### Container Security

```bash
# Run as non-root user (already configured in Dockerfile)
# Use read-only filesystems where possible
# Limit container capabilities
```

### Data Security

```bash
# Encrypt data at rest
# Use secrets management for sensitive data
# Regular security updates

# Update base images
docker-compose pull
docker-compose up -d --force-recreate
```

### SSL/TLS Configuration

```yaml
# Add to docker-compose.yml for HTTPS
nginx:
  ports:
    - "443:443"
  volumes:
    - ./docker/ssl:/etc/nginx/ssl:ro
```

## 🔧 Troubleshooting

### Common Issues

#### Service Won't Start

```bash
# Check logs
docker-compose logs service_name

# Check resource usage
docker stats

# Check disk space
df -h

# Restart service
docker-compose restart service_name
```

#### Out of Memory

```bash
# Check memory usage
docker stats

# Increase memory limits in docker-compose.yml
# Or add swap space
sudo fallocate -l 2G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
```

#### Model Loading Issues

```bash
# Check model files
ls -la models/

# Check container logs
docker-compose logs thinkerbell

# Verify model path
docker-compose exec thinkerbell ls -la /app/models/
```

#### Network Issues

```bash
# Check network connectivity
docker-compose exec thinkerbell ping google.com

# Check port bindings
docker-compose ps
netstat -tlnp | grep :8000
```

### Debug Mode

```bash
# Enable debug logging
export LOG_LEVEL=DEBUG
docker-compose up -d

# Run in foreground for debugging
docker-compose up thinkerbell
```

### Performance Issues

```bash
# Check resource limits
docker-compose config

# Monitor performance
docker stats

# Check model performance
curl http://localhost:8000/metrics
```

## 🏭 Production Considerations

### High Availability

```yaml
# docker-compose.prod.yml
services:
  thinkerbell:
    deploy:
      replicas: 3
      restart_policy:
        condition: on-failure
        max_attempts: 3
      resources:
        limits:
          memory: 4G
          cpus: '2.0'
```

### Load Balancing

```bash
# Use multiple replicas
docker-compose up -d --scale thinkerbell=3

# Configure Nginx upstream
# Edit docker/nginx/conf.d/thinkerbell.conf
```

### Data Persistence

```yaml
# Ensure data persistence
volumes:
  - ./data:/app/data
  - ./logs:/app/logs
  - ./models:/app/models:ro
```

### Backup Strategy

```bash
# Automated backup script
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
tar -czf /backup/thinkerbell_$DATE.tar.gz data/ logs/ docker/

# Add to crontab for daily backups
0 2 * * * /path/to/backup-script.sh
```

### Monitoring and Alerting

```bash
# Set up alerting rules in Prometheus
# Configure notification channels in Grafana
# Monitor key metrics:
# - API response time
# - Error rates
# - Resource usage
# - Model inference time
```

### Security Hardening

```bash
# Use secrets for sensitive data
# Implement proper authentication
# Regular security updates
# Network segmentation
# Log monitoring and analysis
```

## 📚 Additional Resources

- [Docker Documentation](https://docs.docker.com/)
- [Docker Compose Documentation](https://docs.docker.com/compose/)
- [Nginx Documentation](https://nginx.org/en/docs/)
- [Redis Documentation](https://redis.io/documentation)
- [Prometheus Documentation](https://prometheus.io/docs/)
- [Grafana Documentation](https://grafana.com/docs/)

## 🆘 Support

For issues and support:

1. Check the troubleshooting section above
2. Review container logs: `./docker-manage.sh logs`
3. Check service health: `./docker-manage.sh health`
4. Create an issue in the repository with:
   - Error logs
   - System information
   - Steps to reproduce

---

**"Where scientific enquiry meets hardcore creativity – Measured Magic"** 🚀


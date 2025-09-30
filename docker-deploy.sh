#!/bin/bash
# Thinkerbell Docker Deployment Script
# Comprehensive production deployment with Docker
# ==============================================

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
COMPOSE_FILE="docker-compose.yml"
PROJECT_NAME="thinkerbell"
BACKUP_DIR="./backups"
LOG_FILE="./logs/deployment.log"

# Functions
log() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')] $1${NC}" | tee -a "$LOG_FILE"
}

warn() {
    echo -e "${YELLOW}[$(date +'%Y-%m-%d %H:%M:%S')] WARNING: $1${NC}" | tee -a "$LOG_FILE"
}

error() {
    echo -e "${RED}[$(date +'%Y-%m-%d %H:%M:%S')] ERROR: $1${NC}" | tee -a "$LOG_FILE"
    exit 1
}

info() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')] INFO: $1${NC}" | tee -a "$LOG_FILE"
}

# Check prerequisites
check_prerequisites() {
    log "Checking prerequisites..."
    
    # Check Docker
    if ! command -v docker &> /dev/null; then
        error "Docker is not installed or not in PATH"
    fi
    
    # Check Docker Compose
    if ! docker compose version &> /dev/null; then
        error "Docker Compose is not installed or not in PATH"
    fi
    
    # Check if running as root (not recommended)
    if [[ $EUID -eq 0 ]]; then
        warn "Running as root is not recommended for Docker deployments"
    fi
    
    # Check available disk space (minimum 5GB)
    available_space=$(df . | awk 'NR==2 {print $4}')
    if [[ $available_space -lt 5242880 ]]; then
        warn "Less than 5GB disk space available"
    fi
    
    log "Prerequisites check completed"
}

# Create necessary directories
create_directories() {
    log "Creating necessary directories..."
    
    mkdir -p logs data temp backups
    mkdir -p docker/{nginx/conf.d,redis,prometheus,grafana/provisioning/{dashboards,datasources},ssl}
    
    # Set proper permissions
    chmod 755 logs data temp backups
    chmod -R 755 docker/
    
    log "Directories created successfully"
}

# Backup existing data
backup_data() {
    if [[ -d "data" ]] && [[ "$(ls -A data)" ]]; then
        log "Backing up existing data..."
        
        backup_name="backup_$(date +%Y%m%d_%H%M%S)"
        mkdir -p "$BACKUP_DIR"
        tar -czf "$BACKUP_DIR/${backup_name}.tar.gz" data/ logs/ 2>/dev/null || true
        
        log "Backup created: $BACKUP_DIR/${backup_name}.tar.gz"
    fi
}

# Build Docker images
build_images() {
    log "Building Docker images..."
    
    # Build main application image
    docker build -t thinkerbell:latest . || error "Failed to build Thinkerbell image"
    
    # Tag for production
    docker tag thinkerbell:latest thinkerbell:production
    
    log "Docker images built successfully"
}

# Deploy services
deploy_services() {
    log "Deploying services..."
    
    # Pull external images
    docker compose pull nginx redis prometheus grafana || error "Failed to pull external images"
    
    # Start core services
    docker compose up -d thinkerbell nginx redis || error "Failed to start core services"
    
    # Wait for services to be healthy
    log "Waiting for services to be healthy..."
    sleep 30
    
    # Check service health
    if ! docker-compose ps | grep -q "Up (healthy)"; then
        warn "Some services may not be healthy yet"
    fi
    
    log "Core services deployed successfully"
}

# Deploy monitoring (optional)
deploy_monitoring() {
    if [[ "${1:-}" == "--with-monitoring" ]]; then
        log "Deploying monitoring services..."
        
        docker compose --profile monitoring up -d prometheus grafana || warn "Failed to start monitoring services"
        
        log "Monitoring services deployed"
    fi
}

# Validate deployment
validate_deployment() {
    log "Validating deployment..."
    
    # Check if containers are running
    if ! docker compose ps | grep -q "Up"; then
        error "No containers are running"
    fi
    
    # Test API endpoint
    sleep 10
    if curl -f http://localhost:8000/health &>/dev/null; then
        log "API health check passed"
    else
        warn "API health check failed"
    fi
    
    # Test web interface
    if curl -f http://localhost/ &>/dev/null; then
        log "Web interface accessible"
    else
        warn "Web interface not accessible"
    fi
    
    log "Deployment validation completed"
}

# Show deployment info
show_info() {
    log "Deployment completed successfully!"
    echo
    info "🚀 Thinkerbell is now running!"
    echo
    info "Access points:"
    info "  • Web Application: http://localhost/"
    info "  • API Server: http://localhost:8000/"
    info "  • API Documentation: http://localhost:8000/docs"
    info "  • Health Check: http://localhost:8000/health"
    
    if docker compose ps | grep -q "grafana"; then
        info "  • Grafana Dashboard: http://localhost:3000/ (admin/admin123)"
        info "  • Prometheus: http://localhost:9090/"
    fi
    
    echo
    info "Management commands:"
    info "  • View logs: docker compose logs -f"
    info "  • Stop services: docker compose down"
    info "  • Restart: docker compose restart"
    info "  • Update: ./docker-deploy.sh --update"
    echo
}

# Update deployment
update_deployment() {
    log "Updating deployment..."
    
    # Backup current data
    backup_data
    
    # Pull latest images
    docker compose pull
    
    # Rebuild application image
    build_images
    
    # Rolling update
    docker compose up -d --force-recreate
    
    # Validate update
    validate_deployment
    
    log "Update completed successfully"
}

# Cleanup old images and containers
cleanup() {
    log "Cleaning up old images and containers..."
    
    # Remove unused images
    docker image prune -f
    
    # Remove unused containers
    docker container prune -f
    
    # Remove unused volumes (be careful!)
    # docker volume prune -f
    
    log "Cleanup completed"
}

# Main deployment function
main() {
    log "Starting Thinkerbell Docker deployment..."
    
    # Parse arguments
    case "${1:-}" in
        --update)
            update_deployment
            exit 0
            ;;
        --cleanup)
            cleanup
            exit 0
            ;;
        --help)
            echo "Usage: $0 [--update|--cleanup|--with-monitoring|--help]"
            echo "  --update: Update existing deployment"
            echo "  --cleanup: Clean up unused Docker resources"
            echo "  --with-monitoring: Deploy with monitoring services"
            echo "  --help: Show this help message"
            exit 0
            ;;
    esac
    
    # Run deployment steps
    check_prerequisites
    create_directories
    backup_data
    build_images
    deploy_services
    deploy_monitoring "$@"
    validate_deployment
    show_info
    
    log "Deployment script completed successfully"
}

# Trap errors and cleanup
trap 'error "Deployment failed at line $LINENO"' ERR

# Run main function
main "$@"

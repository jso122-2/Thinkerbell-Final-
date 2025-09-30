#!/bin/bash
# Thinkerbell Docker Management Script
# Easy management of Docker services
# ==================================

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
PROJECT_NAME="thinkerbell"
COMPOSE_FILE="docker compose.yml"

# Functions
log() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')] $1${NC}"
}

warn() {
    echo -e "${YELLOW}[$(date +'%Y-%m-%d %H:%M:%S')] WARNING: $1${NC}"
}

error() {
    echo -e "${RED}[$(date +'%Y-%m-%d %H:%M:%S')] ERROR: $1${NC}"
    exit 1
}

info() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')] INFO: $1${NC}"
}

# Show usage
show_usage() {
    echo "Thinkerbell Docker Management Script"
    echo "Usage: $0 <command> [options]"
    echo
    echo "Commands:"
    echo "  start                 Start all services"
    echo "  stop                  Stop all services"
    echo "  restart               Restart all services"
    echo "  status                Show service status"
    echo "  logs [service]        Show logs (all services or specific service)"
    echo "  shell [service]       Open shell in service container"
    echo "  update                Update and restart services"
    echo "  backup                Backup data and logs"
    echo "  restore <backup>      Restore from backup"
    echo "  cleanup               Clean up unused resources"
    echo "  health                Check service health"
    echo "  scale <service> <n>   Scale service to n replicas"
    echo "  monitor               Show real-time resource usage"
    echo
    echo "Examples:"
    echo "  $0 start"
    echo "  $0 logs thinkerbell"
    echo "  $0 shell thinkerbell"
    echo "  $0 scale thinkerbell 3"
}

# Start services
start_services() {
    log "Starting Thinkerbell services..."
    
    if [[ "${1:-}" == "--monitoring" ]]; then
        docker compose --profile monitoring up -d
    else
        docker compose up -d
    fi
    
    log "Services started successfully"
    show_status
}

# Stop services
stop_services() {
    log "Stopping Thinkerbell services..."
    
    docker compose down
    
    log "Services stopped successfully"
}

# Restart services
restart_services() {
    log "Restarting Thinkerbell services..."
    
    docker compose restart
    
    log "Services restarted successfully"
    show_status
}

# Show service status
show_status() {
    log "Service Status:"
    echo
    docker compose ps
    echo
    
    # Show resource usage
    info "Resource Usage:"
    docker stats --no-stream --format "table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.NetIO}}\t{{.BlockIO}}"
}

# Show logs
show_logs() {
    local service="${1:-}"
    
    if [[ -n "$service" ]]; then
        log "Showing logs for service: $service"
        docker compose logs -f "$service"
    else
        log "Showing logs for all services"
        docker compose logs -f
    fi
}

# Open shell in container
open_shell() {
    local service="${1:-thinkerbell}"
    
    log "Opening shell in $service container..."
    
    if docker compose ps "$service" | grep -q "Up"; then
        docker compose exec "$service" /bin/bash
    else
        error "Service $service is not running"
    fi
}

# Update services
update_services() {
    log "Updating Thinkerbell services..."
    
    # Backup current data
    backup_data
    
    # Pull latest images
    docker compose pull
    
    # Rebuild and restart
    docker compose up -d --build --force-recreate
    
    # Wait for services to be healthy
    sleep 30
    
    log "Services updated successfully"
    show_status
}

# Backup data
backup_data() {
    log "Creating backup..."
    
    local backup_name="backup_$(date +%Y%m%d_%H%M%S)"
    local backup_dir="./backups"
    
    mkdir -p "$backup_dir"
    
    # Stop services temporarily for consistent backup
    docker compose stop
    
    # Create backup
    tar -czf "$backup_dir/${backup_name}.tar.gz" data/ logs/ docker/ 2>/dev/null || true
    
    # Restart services
    docker compose start
    
    log "Backup created: $backup_dir/${backup_name}.tar.gz"
}

# Restore from backup
restore_backup() {
    local backup_file="${1:-}"
    
    if [[ -z "$backup_file" ]]; then
        error "Please specify backup file to restore"
    fi
    
    if [[ ! -f "$backup_file" ]]; then
        error "Backup file not found: $backup_file"
    fi
    
    log "Restoring from backup: $backup_file"
    
    # Stop services
    docker compose down
    
    # Extract backup
    tar -xzf "$backup_file"
    
    # Start services
    docker compose up -d
    
    log "Restore completed successfully"
}

# Cleanup unused resources
cleanup_resources() {
    log "Cleaning up unused Docker resources..."
    
    # Remove unused images
    docker image prune -f
    
    # Remove unused containers
    docker container prune -f
    
    # Remove unused networks
    docker network prune -f
    
    # Show disk usage
    info "Docker disk usage:"
    docker system df
    
    log "Cleanup completed"
}

# Check service health
check_health() {
    log "Checking service health..."
    echo
    
    # Check container health
    for container in $(docker compose ps -q); do
        container_name=$(docker inspect --format='{{.Name}}' "$container" | sed 's/\///')
        health_status=$(docker inspect --format='{{.State.Health.Status}}' "$container" 2>/dev/null || echo "no healthcheck")
        
        if [[ "$health_status" == "healthy" ]]; then
            echo -e "${GREEN}✓${NC} $container_name: $health_status"
        elif [[ "$health_status" == "unhealthy" ]]; then
            echo -e "${RED}✗${NC} $container_name: $health_status"
        else
            echo -e "${YELLOW}?${NC} $container_name: $health_status"
        fi
    done
    
    echo
    
    # Test API endpoints
    if curl -f http://localhost:8000/health &>/dev/null; then
        echo -e "${GREEN}✓${NC} API health endpoint: accessible"
    else
        echo -e "${RED}✗${NC} API health endpoint: not accessible"
    fi
    
    if curl -f http://localhost/ &>/dev/null; then
        echo -e "${GREEN}✓${NC} Web interface: accessible"
    else
        echo -e "${RED}✗${NC} Web interface: not accessible"
    fi
}

# Scale service
scale_service() {
    local service="${1:-}"
    local replicas="${2:-}"
    
    if [[ -z "$service" ]] || [[ -z "$replicas" ]]; then
        error "Usage: scale <service> <replicas>"
    fi
    
    log "Scaling $service to $replicas replicas..."
    
    docker compose up -d --scale "$service=$replicas"
    
    log "Service scaled successfully"
    show_status
}

# Monitor resources
monitor_resources() {
    log "Monitoring resource usage (Press Ctrl+C to exit)..."
    echo
    
    docker stats --format "table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.NetIO}}\t{{.BlockIO}}"
}

# Main function
main() {
    local command="${1:-}"
    
    case "$command" in
        start)
            start_services "${2:-}"
            ;;
        stop)
            stop_services
            ;;
        restart)
            restart_services
            ;;
        status)
            show_status
            ;;
        logs)
            show_logs "${2:-}"
            ;;
        shell)
            open_shell "${2:-}"
            ;;
        update)
            update_services
            ;;
        backup)
            backup_data
            ;;
        restore)
            restore_backup "${2:-}"
            ;;
        cleanup)
            cleanup_resources
            ;;
        health)
            check_health
            ;;
        scale)
            scale_service "${2:-}" "${3:-}"
            ;;
        monitor)
            monitor_resources
            ;;
        help|--help|-h)
            show_usage
            ;;
        "")
            show_usage
            ;;
        *)
            error "Unknown command: $command"
            ;;
    esac
}

# Run main function
main "$@"

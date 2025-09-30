#!/bin/bash
# Thinkerbell Docker Hub Deployment Script
# Build, tag, and push images to Docker Hub
# =========================================

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
DOCKER_HUB_USERNAME="${DOCKER_HUB_USERNAME:-}"
DOCKER_HUB_REPO="${DOCKER_HUB_REPO:-thinkerbell}"
IMAGE_TAG="${IMAGE_TAG:-latest}"
BUILD_DATE=$(date -u +'%Y-%m-%dT%H:%M:%SZ')
GIT_COMMIT=$(git rev-parse --short HEAD 2>/dev/null || echo "unknown")
VERSION="${VERSION:-1.0.0}"

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
    echo "Thinkerbell Docker Hub Deployment Script"
    echo "Usage: $0 [options]"
    echo
    echo "Options:"
    echo "  --username <username>    Docker Hub username (or set DOCKER_HUB_USERNAME)"
    echo "  --repo <repo>           Docker Hub repository name (default: thinkerbell)"
    echo "  --tag <tag>             Image tag (default: latest)"
    echo "  --version <version>     Version tag (default: 1.0.0)"
    echo "  --build-only            Only build images, don't push"
    echo "  --push-only             Only push existing images, don't build"
    echo "  --multi-arch            Build multi-architecture images"
    echo "  --help                  Show this help message"
    echo
    echo "Environment Variables:"
    echo "  DOCKER_HUB_USERNAME     Docker Hub username"
    echo "  DOCKER_HUB_TOKEN        Docker Hub access token (recommended)"
    echo
    echo "Examples:"
    echo "  $0 --username myuser --repo thinkerbell --tag v1.0.0"
    echo "  $0 --build-only"
    echo "  $0 --multi-arch --tag production"
}

# Check prerequisites
check_prerequisites() {
    log "Checking prerequisites..."
    
    # Check Docker
    if ! command -v docker &> /dev/null; then
        error "Docker is not installed or not in PATH"
    fi
    
    # Check Docker Buildx for multi-arch builds
    if [[ "${MULTI_ARCH:-false}" == "true" ]]; then
        if ! docker buildx version &> /dev/null; then
            error "Docker Buildx is required for multi-architecture builds"
        fi
    fi
    
    # Check Git (for commit hash)
    if ! command -v git &> /dev/null; then
        warn "Git not found, using 'unknown' for commit hash"
    fi
    
    # Check Docker Hub credentials
    if [[ "${PUSH_ONLY:-false}" != "true" ]] && [[ "${BUILD_ONLY:-false}" != "true" ]]; then
        if [[ -z "$DOCKER_HUB_USERNAME" ]]; then
            error "Docker Hub username is required. Use --username or set DOCKER_HUB_USERNAME"
        fi
    fi
    
    log "Prerequisites check completed"
}

# Docker Hub login
docker_hub_login() {
    if [[ "${BUILD_ONLY:-false}" == "true" ]]; then
        return 0
    fi
    
    log "Logging into Docker Hub..."
    
    if [[ -n "${DOCKER_HUB_TOKEN:-}" ]]; then
        echo "$DOCKER_HUB_TOKEN" | docker login --username "$DOCKER_HUB_USERNAME" --password-stdin
    else
        docker login --username "$DOCKER_HUB_USERNAME"
    fi
    
    log "Successfully logged into Docker Hub"
}

# Build images
build_images() {
    if [[ "${PUSH_ONLY:-false}" == "true" ]]; then
        return 0
    fi
    
    log "Building Thinkerbell images..."
    
    local build_args=(
        --build-arg BUILD_DATE="$BUILD_DATE"
        --build-arg GIT_COMMIT="$GIT_COMMIT"
        --build-arg VERSION="$VERSION"
    )
    
    if [[ "${MULTI_ARCH:-false}" == "true" ]]; then
        log "Building multi-architecture images..."
        
        # Create and use buildx builder
        docker buildx create --name thinkerbell-builder --use 2>/dev/null || docker buildx use thinkerbell-builder
        
        # Build for multiple architectures
        docker buildx build \
            "${build_args[@]}" \
            --platform linux/amd64,linux/arm64 \
            --tag "$DOCKER_HUB_USERNAME/$DOCKER_HUB_REPO:$IMAGE_TAG" \
            --tag "$DOCKER_HUB_USERNAME/$DOCKER_HUB_REPO:$VERSION" \
            --tag "$DOCKER_HUB_USERNAME/$DOCKER_HUB_REPO:latest" \
            --push \
            .
    else
        log "Building single-architecture image..."
        
        # Build main application image
        docker build \
            "${build_args[@]}" \
            --tag "$DOCKER_HUB_USERNAME/$DOCKER_HUB_REPO:$IMAGE_TAG" \
            --tag "$DOCKER_HUB_USERNAME/$DOCKER_HUB_REPO:$VERSION" \
            --tag "$DOCKER_HUB_USERNAME/$DOCKER_HUB_REPO:latest" \
            .
    fi
    
    log "Images built successfully"
}

# Tag images
tag_images() {
    if [[ "${PUSH_ONLY:-false}" == "true" ]] || [[ "${MULTI_ARCH:-false}" == "true" ]]; then
        return 0
    fi
    
    log "Tagging images..."
    
    # Tag with different versions
    docker tag "thinkerbell:latest" "$DOCKER_HUB_USERNAME/$DOCKER_HUB_REPO:$IMAGE_TAG"
    docker tag "thinkerbell:latest" "$DOCKER_HUB_USERNAME/$DOCKER_HUB_REPO:$VERSION"
    docker tag "thinkerbell:latest" "$DOCKER_HUB_USERNAME/$DOCKER_HUB_REPO:latest"
    
    # Tag with build metadata
    docker tag "thinkerbell:latest" "$DOCKER_HUB_USERNAME/$DOCKER_HUB_REPO:$VERSION-$GIT_COMMIT"
    
    log "Images tagged successfully"
}

# Push images to Docker Hub
push_images() {
    if [[ "${BUILD_ONLY:-false}" == "true" ]] || [[ "${MULTI_ARCH:-false}" == "true" ]]; then
        return 0
    fi
    
    log "Pushing images to Docker Hub..."
    
    # Push all tags
    docker push "$DOCKER_HUB_USERNAME/$DOCKER_HUB_REPO:$IMAGE_TAG"
    docker push "$DOCKER_HUB_USERNAME/$DOCKER_HUB_REPO:$VERSION"
    docker push "$DOCKER_HUB_USERNAME/$DOCKER_HUB_REPO:latest"
    docker push "$DOCKER_HUB_USERNAME/$DOCKER_HUB_REPO:$VERSION-$GIT_COMMIT"
    
    log "Images pushed successfully"
}

# Create Docker Hub repository description
create_repo_description() {
    cat > docker-hub-description.md << EOF
# Thinkerbell Legal Text Generator

🤖 **Intelligent Legal Document Generation with Auto-Detection**

Transform rough legal text examples into professional, comprehensive legal templates using AI-powered analysis and generation.

## Features

- **🤖 Smart Auto-Detection**: Automatically detects document type, style, and optimal length
- **📦 Batch Processing**: Process multiple documents simultaneously with progress tracking
- **📄 Professional Output**: Download results as organized .txt files or ZIP archives
- **⚡ Real-Time Analysis**: Live parameter detection as you type
- **🎨 Multiple Styles**: Professional, formal, business, and detailed options
- **📊 Performance Metrics**: 96.4% accuracy, 84.5% Recall@5

## Quick Start

\`\`\`bash
# Run with Docker
docker run -p 8000:8000 $DOCKER_HUB_USERNAME/$DOCKER_HUB_REPO:latest

# Or use Docker Compose
curl -O https://raw.githubusercontent.com/your-org/thinkerbell/main/docker-compose.yml
docker compose up -d
\`\`\`

## Access Points

- **Web Application**: http://localhost/
- **API Server**: http://localhost:8000/
- **API Documentation**: http://localhost:8000/docs

## Tags

- \`latest\` - Latest stable release
- \`v1.0.0\` - Specific version
- \`production\` - Production-ready build

## Architecture

- **Base**: Python 3.11 slim
- **Framework**: FastAPI
- **ML**: Sentence Transformers
- **Frontend**: HTML/CSS/JavaScript
- **Size**: ~2GB (includes AI models)

## Environment Variables

- \`THINKERBELL_MODEL_DIR\` - Path to model directory
- \`PORT\` - API server port (default: 8000)
- \`HOST\` - API server host (default: 0.0.0.0)

## Support

- **Documentation**: https://github.com/your-org/thinkerbell
- **Issues**: https://github.com/your-org/thinkerbell/issues

---

**"Where scientific enquiry meets hardcore creativity – Measured Magic"** 🚀
EOF
    
    info "Repository description created: docker-hub-description.md"
}

# Show deployment summary
show_summary() {
    log "Deployment completed successfully!"
    echo
    info "🚀 Thinkerbell images are now available on Docker Hub!"
    echo
    info "Docker Hub Repository: https://hub.docker.com/r/$DOCKER_HUB_USERNAME/$DOCKER_HUB_REPO"
    echo
    info "Available tags:"
    info "  • $DOCKER_HUB_USERNAME/$DOCKER_HUB_REPO:latest"
    info "  • $DOCKER_HUB_USERNAME/$DOCKER_HUB_REPO:$VERSION"
    info "  • $DOCKER_HUB_USERNAME/$DOCKER_HUB_REPO:$IMAGE_TAG"
    info "  • $DOCKER_HUB_USERNAME/$DOCKER_HUB_REPO:$VERSION-$GIT_COMMIT"
    echo
    info "Usage examples:"
    info "  # Run standalone"
    info "  docker run -p 8000:8000 $DOCKER_HUB_USERNAME/$DOCKER_HUB_REPO:latest"
    echo
    info "  # Run with Docker Compose"
    info "  # Update docker-compose.yml to use: $DOCKER_HUB_USERNAME/$DOCKER_HUB_REPO:latest"
    echo
    info "Next steps:"
    info "  1. Update your docker-compose.yml to use Docker Hub images"
    info "  2. Test the deployment: docker run -p 8000:8000 $DOCKER_HUB_USERNAME/$DOCKER_HUB_REPO:latest"
    info "  3. Update repository description on Docker Hub"
    echo
}

# Update docker-compose.yml for Docker Hub
update_compose_for_hub() {
    log "Creating Docker Hub version of docker-compose.yml..."
    
    cp docker-compose.yml docker-compose.hub.yml
    
    # Replace build context with Docker Hub image
    sed -i "s|build:|# build:|g" docker-compose.hub.yml
    sed -i "s|context: \.|# context: \.|g" docker-compose.hub.yml
    sed -i "s|dockerfile: Dockerfile|# dockerfile: Dockerfile|g" docker-compose.hub.yml
    sed -i "s|target: production|# target: production|g" docker-compose.hub.yml
    
    # Add image reference
    sed -i "/container_name: thinkerbell-app/i\\    image: $DOCKER_HUB_USERNAME/$DOCKER_HUB_REPO:$IMAGE_TAG" docker-compose.hub.yml
    
    log "Created docker-compose.hub.yml for Docker Hub deployment"
}

# Main function
main() {
    # Parse arguments
    while [[ $# -gt 0 ]]; do
        case $1 in
            --username)
                DOCKER_HUB_USERNAME="$2"
                shift 2
                ;;
            --repo)
                DOCKER_HUB_REPO="$2"
                shift 2
                ;;
            --tag)
                IMAGE_TAG="$2"
                shift 2
                ;;
            --version)
                VERSION="$2"
                shift 2
                ;;
            --build-only)
                BUILD_ONLY="true"
                shift
                ;;
            --push-only)
                PUSH_ONLY="true"
                shift
                ;;
            --multi-arch)
                MULTI_ARCH="true"
                shift
                ;;
            --help)
                show_usage
                exit 0
                ;;
            *)
                error "Unknown option: $1"
                ;;
        esac
    done
    
    log "Starting Thinkerbell Docker Hub deployment..."
    
    # Run deployment steps
    check_prerequisites
    docker_hub_login
    build_images
    tag_images
    push_images
    create_repo_description
    update_compose_for_hub
    show_summary
    
    log "Docker Hub deployment completed successfully"
}

# Trap errors
trap 'error "Deployment failed at line $LINENO"' ERR

# Run main function
main "$@"

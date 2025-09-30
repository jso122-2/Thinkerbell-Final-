# Thinkerbell Production Dockerfile
# Multi-stage build for optimized production image
# ================================================

# Stage 1: Base Python environment
FROM python:3.11-slim as base

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    DEBIAN_FRONTEND=noninteractive

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    git \
    wget \
    unzip \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user
RUN groupadd -r thinkerbell && useradd -r -g thinkerbell thinkerbell

# Set working directory
WORKDIR /app

# Stage 2: Dependencies installation
FROM base as dependencies

# Copy requirements first for better caching
COPY requirements_production.txt ./

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements_production.txt

# Stage 3: Application build
FROM dependencies as application

# Copy application files
COPY backend_api_server.py ./
COPY simple_webapp.html ./
COPY config/ ./config/
COPY style_profiles/ ./style_profiles/
COPY requirements/ ./requirements/

# Copy model files (these will be handled by Git LFS)
COPY models/ ./models/

# Copy startup scripts
COPY start_*.sh ./
COPY deploy.sh ./
COPY validate_production.sh ./

# Make scripts executable
RUN chmod +x *.sh

# Create necessary directories
RUN mkdir -p logs data temp

# Set proper ownership
RUN chown -R thinkerbell:thinkerbell /app

# Stage 4: Production image
FROM python:3.11-slim as production

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    THINKERBELL_ENV=production \
    THINKERBELL_MODEL_DIR=/app/models/thinkerbell-encoder-best \
    PORT=8000 \
    HOST=0.0.0.0

# Install minimal runtime dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Create non-root user
RUN groupadd -r thinkerbell && useradd -r -g thinkerbell thinkerbell

# Set working directory
WORKDIR /app

# Copy Python dependencies from dependencies stage
COPY --from=dependencies /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=dependencies /usr/local/bin /usr/local/bin

# Copy application from application stage
COPY --from=application --chown=thinkerbell:thinkerbell /app /app

# Create volume mount points
VOLUME ["/app/logs", "/app/data", "/app/models"]

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Switch to non-root user
USER thinkerbell

# Default command
CMD ["python", "backend_api_server.py"]

# Labels for metadata
LABEL maintainer="Thinkerbell Team" \
      version="1.0.0" \
      description="Thinkerbell Legal Text Generator - Production Ready" \
      org.opencontainers.image.title="Thinkerbell" \
      org.opencontainers.image.description="AI-powered legal document generation with auto-detection" \
      org.opencontainers.image.version="1.0.0" \
      org.opencontainers.image.created="2025-09-30" \
      org.opencontainers.image.source="https://github.com/your-org/thinkerbell" \
      org.opencontainers.image.licenses="Proprietary"
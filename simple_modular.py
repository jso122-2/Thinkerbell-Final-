#!/usr/bin/env python3
"""
Simplified modular app - minimal working version
"""

import os
import time
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuration
HOST = os.environ.get("HOST", "0.0.0.0")
PORT = int(os.environ.get("PORT", 8000))
ENV = os.environ.get("THINKERBELL_ENV", "production")

# Track server start time
start_time = time.time()

# Simple request/response models
class HealthResponse(BaseModel):
    status: str
    uptime_seconds: float
    environment: str

class EmbedRequest(BaseModel):
    texts: List[str]
    normalize: bool = True

# Create FastAPI app
app = FastAPI(
    title="Thinkerbell Enhanced API",
    version="2.0.0",
    description="AI-powered legal document generation (Simplified Modular)",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files if they exist
static_dir = Path("static")
if static_dir.exists():
    app.mount("/assets", StaticFiles(directory=static_dir / "assets"), name="assets")
    app.mount("/static", StaticFiles(directory=static_dir), name="static")

# Health check endpoint (most important for Railway)
@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint for Railway"""
    return HealthResponse(
        status="healthy",
        uptime_seconds=time.time() - start_time,
        environment=ENV
    )

@app.get("/status")
async def detailed_status():
    """Detailed status for debugging"""
    return {
        "server": {
            "status": "running",
            "uptime_seconds": time.time() - start_time,
            "host": HOST,
            "port": PORT,
            "env": ENV
        },
        "app_info": {
            "name": "Thinkerbell Enhanced API",
            "version": "2.0.0",
            "description": "Simplified Modular Version"
        }
    }

# Basic ML endpoints (placeholder)
@app.post("/embed")
async def embed_texts(request: EmbedRequest):
    """Placeholder embed endpoint"""
    return {
        "message": "Embed endpoint available",
        "texts_count": len(request.texts),
        "note": "ML functionality will be added when dependencies are available"
    }

@app.get("/model/info")
async def get_model_info():
    """Model info endpoint"""
    return {
        "model_loaded": False,
        "note": "Model loading will be implemented when ML dependencies are available"
    }

# Frontend serving
@app.get("/")
async def serve_frontend():
    """Serve the React frontend at root"""
    index_file = static_dir / "index.html"
    
    if index_file.exists():
        return FileResponse(str(index_file))
    else:
        return {
            "message": "Thinkerbell Enhanced API",
            "version": "2.0.0",
            "description": "Simplified Modular Version",
            "note": "Frontend not available - API only mode",
            "endpoints": ["/health", "/status", "/embed", "/model/info"]
        }

# Catch-all for SPA routing (defined last)
@app.get("/{path:path}")
async def serve_spa_routes(path: str):
    """Serve React SPA for frontend routes"""
    # Exclude API endpoints
    excluded_paths = {"health", "status", "embed", "model", "assets", "static"}
    
    if any(path.startswith(excluded) for excluded in excluded_paths):
        raise HTTPException(status_code=404, detail="API endpoint not found")
    
    index_file = static_dir / "index.html"
    if index_file.exists():
        return FileResponse(str(index_file))
    else:
        raise HTTPException(status_code=404, detail="Frontend not available")

def main():
    """Main function to run the server"""
    logger.info("Starting Thinkerbell Enhanced API (Simplified Modular)")
    logger.info(f"Environment: {ENV}")
    logger.info(f"Server will run on {HOST}:{PORT}")
    
    uvicorn.run(
        app,
        host=HOST,
        port=PORT,
        log_level="info"
    )

if __name__ == "__main__":
    main()

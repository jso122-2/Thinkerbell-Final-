"""
Health check and system status endpoints
"""

import time
from fastapi import APIRouter

from ..core.config import settings
from ..core.dependencies import get_dependency_status
from ..services.model_service import model_service
from ..models.responses import HealthResponse

router = APIRouter()

# Track server start time
start_time = time.time()

@router.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint for Railway and monitoring"""
    try:
        # Always return healthy for server functionality
        model_info = model_service.get_model_info()
        
        return HealthResponse(
            status="healthy",
            model_loaded=model_info.get("model_loaded", False),
            model_path=model_info.get("model_path", settings.MODEL_DIR),
            model_dimension=model_info.get("dimension"),
            uptime_seconds=time.time() - start_time
        )
    except Exception as e:
        # Even if there's an error, return healthy for basic server function
        return HealthResponse(
            status="healthy",
            model_loaded=False,
            model_path=settings.MODEL_DIR,
            model_dimension=None,
            uptime_seconds=time.time() - start_time
        )

@router.get("/status")
async def detailed_status():
    """Detailed status for debugging"""
    return {
        "server": {
            "status": "running",
            "uptime_seconds": time.time() - start_time,
            "host": settings.HOST,
            "port": settings.PORT,
            "env": settings.ENV
        },
        "dependencies": get_dependency_status(),
        "model": model_service.get_model_info(),
        "app_info": {
            "name": settings.APP_NAME,
            "version": settings.VERSION,
            "description": settings.DESCRIPTION
        }
    }

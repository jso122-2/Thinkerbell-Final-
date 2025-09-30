"""
Frontend serving routes
"""

from pathlib import Path
from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from ..core.config import settings

router = APIRouter()

# Mount static assets
if settings.STATIC_DIR.exists():
    router.mount("/assets", StaticFiles(directory=settings.STATIC_DIR / "assets"), name="assets")
    router.mount("/static", StaticFiles(directory=settings.STATIC_DIR), name="static")

@router.get("/")
async def serve_frontend():
    """Serve the React frontend at root"""
    index_file = settings.STATIC_DIR / "index.html"
    
    if index_file.exists():
        return FileResponse(str(index_file))
    else:
        # Fallback to API info if frontend not available
        return {
            "message": settings.APP_NAME,
            "version": settings.VERSION,
            "description": settings.DESCRIPTION,
            "note": "Frontend not available - API only mode",
            "endpoints": [
                "/health", "/status", "/embed", "/similarity", "/search", 
                "/analyze", "/generate", "/model/info", "/batch/generate", 
                "/batch/status/{batch_id}", "/batch/download/{batch_id}", "/batch/list"
            ]
        }

@router.get("/{path:path}")
async def serve_spa_routes(path: str):
    """Serve React SPA for frontend routes (catch-all for client-side routing)"""
    # Explicitly exclude API endpoints and static assets
    excluded_paths = {
        "health", "status", "embed", "similarity", "search", "analyze", 
        "generate", "model", "batch", "assets", "static"
    }
    
    # Check if path starts with any excluded path
    if any(path.startswith(excluded) for excluded in excluded_paths):
        raise HTTPException(status_code=404, detail="API endpoint not found")
    
    # Serve frontend for all other routes
    index_file = settings.STATIC_DIR / "index.html"
    
    if index_file.exists():
        return FileResponse(str(index_file))
    else:
        raise HTTPException(status_code=404, detail="Frontend not available")

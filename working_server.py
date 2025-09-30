#!/usr/bin/env python3
"""
Working server that handles missing static directories gracefully
"""

import os
import sys
import time
from pathlib import Path
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
import uvicorn

# Railway environment
HOST = os.environ.get("HOST", "0.0.0.0")
PORT = int(os.environ.get("PORT", 8000))

print(f"=== WORKING SERVER ===")
print(f"Host: {HOST}")
print(f"Port: {PORT}")
print(f"Working dir: {os.getcwd()}")

# Check static directories
static_dir = Path("static")
assets_dir = static_dir / "assets"

print(f"Static dir exists: {static_dir.exists()}")
print(f"Assets dir exists: {assets_dir.exists()}")

if static_dir.exists():
    print(f"Static dir contents: {list(static_dir.iterdir())}")

# Create FastAPI app
app = FastAPI(
    title="Working Thinkerbell Server",
    version="2.0.0",
    description="Server that handles missing static files gracefully"
)

# Only mount static files if they exist
if static_dir.exists() and assets_dir.exists():
    try:
        app.mount("/assets", StaticFiles(directory="static/assets"), name="assets")
        print("✅ Assets mounted successfully")
    except Exception as e:
        print(f"⚠️ Could not mount assets: {e}")

if static_dir.exists():
    try:
        app.mount("/static", StaticFiles(directory="static"), name="static")
        print("✅ Static files mounted successfully")
    except Exception as e:
        print(f"⚠️ Could not mount static files: {e}")

# Health endpoint
@app.get("/health")
async def health():
    return JSONResponse({
        "status": "healthy",
        "timestamp": time.time(),
        "message": "Working server is healthy",
        "static_available": static_dir.exists(),
        "assets_available": assets_dir.exists()
    })

# Root endpoint
@app.get("/")
async def root():
    index_file = static_dir / "index.html"
    
    if index_file.exists():
        # Serve the frontend
        from fastapi.responses import FileResponse
        return FileResponse(str(index_file))
    else:
        # API mode
        return JSONResponse({
            "message": "Thinkerbell Enhanced API",
            "version": "2.0.0",
            "mode": "API only - frontend not available",
            "endpoints": ["/health", "/status", "/api-info"],
            "static_dir_exists": static_dir.exists(),
            "working_directory": str(Path.cwd())
        })

@app.get("/status")
async def status():
    return JSONResponse({
        "server": "running",
        "host": HOST,
        "port": PORT,
        "static_directory": {
            "exists": static_dir.exists(),
            "path": str(static_dir),
            "contents": list(static_dir.iterdir()) if static_dir.exists() else []
        },
        "assets_directory": {
            "exists": assets_dir.exists(),
            "path": str(assets_dir)
        }
    })

@app.get("/api-info")
async def api_info():
    return JSONResponse({
        "message": "Thinkerbell Enhanced API",
        "version": "2.0.0",
        "description": "AI-powered legal document generation",
        "available_endpoints": [
            "/health - Health check",
            "/status - Server status", 
            "/api-info - This endpoint"
        ],
        "note": "Full ML endpoints will be available when dependencies are installed"
    })

def main():
    print(f"🚀 Starting working server on {HOST}:{PORT}")
    print("This server handles missing static files gracefully")
    
    try:
        uvicorn.run(
            app,
            host=HOST,
            port=PORT,
            log_level="info"
        )
    except Exception as e:
        print(f"❌ Server failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()

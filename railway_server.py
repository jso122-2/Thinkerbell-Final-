#!/usr/bin/env python3
"""
Railway-optimized server with all Railway-specific handling
"""

import os
import sys
import time
import signal
import asyncio
from pathlib import Path

# Print everything for debugging
print("=== RAILWAY SERVER STARTING ===")
print(f"Python: {sys.version}")
print(f"Working dir: {os.getcwd()}")
print(f"Files in current dir: {list(Path('.').iterdir())}")

# Railway environment variables
HOST = os.environ.get("HOST", "0.0.0.0")
PORT = int(os.environ.get("PORT", 8000))
RAILWAY_ENVIRONMENT = os.environ.get("RAILWAY_ENVIRONMENT", "unknown")

print(f"HOST: {HOST}")
print(f"PORT: {PORT}")
print(f"RAILWAY_ENVIRONMENT: {RAILWAY_ENVIRONMENT}")

# Check if we're actually in Railway
print(f"All env vars starting with RAILWAY:")
for key, value in os.environ.items():
    if key.startswith("RAILWAY"):
        print(f"  {key}: {value}")

try:
    from fastapi import FastAPI
    from fastapi.responses import JSONResponse
    import uvicorn
    
    print("✅ All imports successful")
    
    # Create FastAPI app with Railway optimizations
    app = FastAPI(
        title="Railway Thinkerbell Server",
        version="2.0.0",
        description="Railway-optimized Thinkerbell server"
    )
    
    # Health endpoint (critical for Railway)
    @app.get("/health")
    async def health():
        return JSONResponse({
            "status": "healthy",
            "timestamp": time.time(),
            "environment": RAILWAY_ENVIRONMENT,
            "host": HOST,
            "port": PORT
        })
    
    # Root endpoint
    @app.get("/")
    async def root():
        return JSONResponse({
            "message": "Thinkerbell Railway Server",
            "status": "running",
            "version": "2.0.0",
            "environment": RAILWAY_ENVIRONMENT,
            "endpoints": ["/health", "/status", "/env"]
        })
    
    # Status endpoint for debugging
    @app.get("/status")
    async def status():
        return JSONResponse({
            "server": {
                "status": "running",
                "host": HOST,
                "port": PORT,
                "environment": RAILWAY_ENVIRONMENT
            },
            "system": {
                "python_version": sys.version,
                "working_directory": str(Path.cwd()),
                "files_count": len(list(Path('.').iterdir()))
            }
        })
    
    # Environment variables endpoint
    @app.get("/env")
    async def env_info():
        railway_vars = {k: v for k, v in os.environ.items() if k.startswith("RAILWAY")}
        return JSONResponse({
            "railway_vars": railway_vars,
            "host": HOST,
            "port": PORT,
            "python_path": sys.path[:3]  # First 3 entries
        })
    
    print("✅ FastAPI app configured")
    
    # Graceful shutdown handling
    def signal_handler(signum, frame):
        print(f"Received signal {signum}, shutting down gracefully...")
        sys.exit(0)
    
    signal.signal(signal.SIGTERM, signal_handler)
    signal.signal(signal.SIGINT, signal_handler)
    
    # Start server with Railway-optimized settings
    print(f"🚀 Starting Railway server on {HOST}:{PORT}")
    
    uvicorn.run(
        app,
        host=HOST,
        port=PORT,
        log_level="info",
        access_log=True,
        # Railway-specific optimizations
        workers=1,  # Single worker for Railway
        loop="asyncio",
        timeout_keep_alive=30
    )
    
except Exception as e:
    print(f"❌ CRITICAL FAILURE: {e}")
    import traceback
    traceback.print_exc()
    
    # Write detailed error log
    try:
        error_info = {
            "error": str(e),
            "traceback": traceback.format_exc(),
            "environment": dict(os.environ),
            "python_version": sys.version,
            "working_directory": str(Path.cwd()),
            "files": [str(f) for f in Path('.').iterdir()]
        }
        
        with open("railway_error.log", "w") as f:
            import json
            json.dump(error_info, f, indent=2)
        
        print("Detailed error written to railway_error.log")
    except Exception as log_error:
        print(f"Could not write error log: {log_error}")
    
    sys.exit(1)

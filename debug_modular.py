#!/usr/bin/env python3
"""
Debug version of modular app to identify startup issues
"""

import os
import sys
import traceback
import time
from pathlib import Path

print("=== MODULAR APP DEBUG START ===")
print(f"Python version: {sys.version}")
print(f"Working directory: {os.getcwd()}")
print(f"Python path: {sys.path}")

# Test basic imports first
print("\n=== Testing Basic Imports ===")
try:
    import fastapi
    print(f"✅ FastAPI imported: {fastapi.__version__}")
except Exception as e:
    print(f"❌ FastAPI import failed: {e}")
    sys.exit(1)

try:
    import uvicorn
    print(f"✅ Uvicorn imported: {uvicorn.__version__}")
except Exception as e:
    print(f"❌ Uvicorn import failed: {e}")
    sys.exit(1)

try:
    import pydantic
    print(f"✅ Pydantic imported: {pydantic.__version__}")
except Exception as e:
    print(f"❌ Pydantic import failed: {e}")
    sys.exit(1)

# Test app module imports
print("\n=== Testing App Module Imports ===")
try:
    from app.core.config import settings
    print(f"✅ Config imported: {settings.APP_NAME}")
except Exception as e:
    print(f"❌ Config import failed: {e}")
    traceback.print_exc()

try:
    from app.core.dependencies import get_dependency_status
    deps = get_dependency_status()
    print(f"✅ Dependencies imported: {deps}")
except Exception as e:
    print(f"❌ Dependencies import failed: {e}")
    traceback.print_exc()

try:
    from app.services.model_service import model_service
    print("✅ Model service imported")
except Exception as e:
    print(f"❌ Model service import failed: {e}")
    traceback.print_exc()

try:
    from app.routes.health import router as health_router
    print("✅ Health router imported")
except Exception as e:
    print(f"❌ Health router import failed: {e}")
    traceback.print_exc()

# Test creating minimal FastAPI app
print("\n=== Testing FastAPI App Creation ===")
try:
    from fastapi import FastAPI
    
    app = FastAPI(title="Debug App", version="1.0.0")
    
    @app.get("/")
    async def root():
        return {"message": "Debug app working"}
    
    @app.get("/health")
    async def health():
        return {"status": "healthy", "uptime": time.time()}
    
    print("✅ Minimal FastAPI app created")
    
    # Test if we can start the server
    print("\n=== Testing Server Startup ===")
    HOST = os.environ.get("HOST", "0.0.0.0")
    PORT = int(os.environ.get("PORT", 8000))
    
    print(f"Starting server on {HOST}:{PORT}")
    
    import uvicorn
    uvicorn.run(
        app,
        host=HOST,
        port=PORT,
        log_level="info"
    )
    
except Exception as e:
    print(f"❌ FastAPI app creation failed: {e}")
    traceback.print_exc()
    sys.exit(1)

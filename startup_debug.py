#!/usr/bin/env python3
"""
Startup diagnostic script - shows exactly what happens during server startup
"""

import os
import sys
import time
import logging
import traceback
from pathlib import Path

# Configure detailed logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def main():
    print("=== STARTUP DIAGNOSTIC ===")
    print(f"Python version: {sys.version}")
    print(f"Working directory: {os.getcwd()}")
    print(f"Environment variables:")
    for key in ['HOST', 'PORT', 'THINKERBELL_ENV']:
        print(f"  {key}: {os.environ.get(key, 'NOT SET')}")
    
    # Check if static directory exists
    static_dir = Path("static")
    print(f"Static directory exists: {static_dir.exists()}")
    if static_dir.exists():
        print(f"Static directory contents: {list(static_dir.iterdir())}")
    
    print("\n=== TESTING BASIC IMPORTS ===")
    try:
        import fastapi
        import uvicorn
        import pydantic
        print("✅ Basic imports successful")
    except Exception as e:
        print(f"❌ Basic imports failed: {e}")
        return
    
    print("\n=== TESTING APP IMPORTS ===")
    try:
        from app.core.config import settings
        print(f"✅ Config loaded: {settings.APP_NAME}")
        print(f"  Host: {settings.HOST}")
        print(f"  Port: {settings.PORT}")
        print(f"  Environment: {settings.ENV}")
    except Exception as e:
        print(f"❌ Config import failed: {e}")
        traceback.print_exc()
        return
    
    try:
        from app.main import create_app
        print("✅ Main app import successful")
    except Exception as e:
        print(f"❌ Main app import failed: {e}")
        traceback.print_exc()
        return
    
    print("\n=== CREATING FASTAPI APP ===")
    try:
        app = create_app()
        print("✅ FastAPI app created successfully")
    except Exception as e:
        print(f"❌ FastAPI app creation failed: {e}")
        traceback.print_exc()
        return
    
    print("\n=== TESTING HEALTH ENDPOINT ===")
    try:
        # Test if we can access the health endpoint function
        from app.routes.health import health_check
        import asyncio
        
        # Run the health check function
        result = asyncio.run(health_check())
        print(f"✅ Health check function works: {result}")
    except Exception as e:
        print(f"❌ Health check function failed: {e}")
        traceback.print_exc()
    
    print("\n=== STARTING SERVER ===")
    try:
        import uvicorn
        
        HOST = settings.HOST
        PORT = settings.PORT
        
        print(f"Starting server on {HOST}:{PORT}")
        print("Server should be accessible for health checks...")
        
        # Start the server
        uvicorn.run(
            app,
            host=HOST,
            port=PORT,
            log_level="debug",
            access_log=True
        )
        
    except Exception as e:
        print(f"❌ Server startup failed: {e}")
        traceback.print_exc()

if __name__ == "__main__":
    main()

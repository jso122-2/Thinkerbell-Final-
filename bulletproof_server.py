#!/usr/bin/env python3
"""
Bulletproof minimal server - guaranteed to work
"""

import os
import sys
import time
import json
import traceback

print("=== BULLETPROOF SERVER STARTING ===")
print(f"Python version: {sys.version}")
print(f"Working directory: {os.getcwd()}")

# Get environment variables
HOST = os.environ.get("HOST", "0.0.0.0")
PORT = int(os.environ.get("PORT", 8000))

print(f"HOST: {HOST}")
print(f"PORT: {PORT}")

try:
    # Import FastAPI and Uvicorn
    print("Importing FastAPI...")
    from fastapi import FastAPI
    print("✅ FastAPI imported")
    
    print("Importing Uvicorn...")
    import uvicorn
    print("✅ Uvicorn imported")
    
    # Create the simplest possible FastAPI app
    print("Creating FastAPI app...")
    app = FastAPI(
        title="Bulletproof Server",
        version="1.0.0",
        description="Minimal working server"
    )
    print("✅ FastAPI app created")
    
    # Add health endpoint
    @app.get("/health")
    async def health():
        return {
            "status": "healthy",
            "timestamp": time.time(),
            "message": "Bulletproof server is running"
        }
    
    @app.get("/")
    async def root():
        return {
            "message": "Bulletproof server is working!",
            "host": HOST,
            "port": PORT,
            "python_version": sys.version,
            "working_directory": os.getcwd()
        }
    
    @app.get("/env")
    async def env_vars():
        return {
            "HOST": HOST,
            "PORT": PORT,
            "PYTHONPATH": os.environ.get("PYTHONPATH", "Not set"),
            "PWD": os.environ.get("PWD", "Not set")
        }
    
    print("✅ Routes defined")
    
    # Start the server
    print(f"Starting server on {HOST}:{PORT}...")
    print("This should work!")
    
    uvicorn.run(
        app,
        host=HOST,
        port=PORT,
        log_level="info"
    )
    
except Exception as e:
    print(f"❌ FATAL ERROR: {e}")
    print("Full traceback:")
    traceback.print_exc()
    
    # Try to write error to a file for debugging
    try:
        with open("error.log", "w") as f:
            f.write(f"Error: {e}\n")
            f.write(f"Traceback: {traceback.format_exc()}\n")
            f.write(f"Environment: {dict(os.environ)}\n")
        print("Error written to error.log")
    except:
        pass
    
    # Exit with error code
    sys.exit(1)

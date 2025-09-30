#!/usr/bin/env python3
"""
Debug health check issues - logs everything
"""

import os
import sys
import time
import asyncio
import signal
from fastapi import FastAPI
import uvicorn

# Railway environment
HOST = os.environ.get("HOST", "0.0.0.0")
PORT = int(os.environ.get("PORT", 8000))

print(f"=== HEALTH CHECK DEBUG ===")
print(f"Host: {HOST}")
print(f"Port: {PORT}")
print(f"Time: {time.strftime('%Y-%m-%d %H:%M:%S')}")

# Create FastAPI app
app = FastAPI(title="Health Check Debug")

# Track requests
request_count = 0
start_time = time.time()

@app.middleware("http")
async def log_requests(request, call_next):
    global request_count
    request_count += 1
    
    print(f"📥 Request #{request_count}: {request.method} {request.url}")
    print(f"   Headers: {dict(request.headers)}")
    print(f"   Client: {request.client}")
    
    start = time.time()
    response = await call_next(request)
    duration = time.time() - start
    
    print(f"📤 Response #{request_count}: {response.status_code} ({duration:.3f}s)")
    return response

@app.get("/health")
async def health():
    uptime = time.time() - start_time
    response = {
        "status": "healthy",
        "timestamp": time.time(),
        "uptime_seconds": uptime,
        "request_count": request_count,
        "message": "Health check endpoint working"
    }
    print(f"🏥 Health check called - returning: {response}")
    return response

@app.get("/")
async def root():
    response = {
        "message": "Debug server running",
        "uptime_seconds": time.time() - start_time,
        "request_count": request_count,
        "host": HOST,
        "port": PORT
    }
    print(f"🏠 Root endpoint called - returning: {response}")
    return response

@app.get("/ping")
async def ping():
    print("🏓 Ping endpoint called")
    return {"ping": "pong", "timestamp": time.time()}

# Graceful shutdown
def signal_handler(signum, frame):
    print(f"🛑 Received signal {signum} - shutting down")
    sys.exit(0)

signal.signal(signal.SIGTERM, signal_handler)
signal.signal(signal.SIGINT, signal_handler)

def main():
    print(f"🚀 Starting debug server...")
    print(f"   Endpoints: /health, /, /ping")
    print(f"   All requests will be logged")
    
    try:
        uvicorn.run(
            app,
            host=HOST,
            port=PORT,
            log_level="debug",
            access_log=True
        )
    except Exception as e:
        print(f"❌ Server failed to start: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()

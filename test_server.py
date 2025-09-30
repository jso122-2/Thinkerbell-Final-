#!/usr/bin/env python3
"""
Minimal test server for Railway debugging
"""

import os
import time
from fastapi import FastAPI
import uvicorn

# Configuration
PORT = int(os.environ.get("PORT", 8000))
HOST = os.environ.get("HOST", "0.0.0.0")

# Create minimal FastAPI app
app = FastAPI(title="Test Server", version="1.0.0")

start_time = time.time()

@app.get("/")
async def root():
    return {"message": "Test server is running!", "uptime": time.time() - start_time}

@app.get("/health")
async def health():
    return {"status": "healthy", "uptime": time.time() - start_time}

def main():
    print(f"Starting test server on {HOST}:{PORT}")
    uvicorn.run(
        "test_server:app",
        host=HOST,
        port=PORT,
        reload=False,
        log_level="info"
    )

if __name__ == "__main__":
    main()

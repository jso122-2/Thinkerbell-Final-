#!/usr/bin/env python3
"""
Minimal port binding test
"""

import os
import socket
import time
from fastapi import FastAPI
import uvicorn

# Get Railway environment
HOST = os.environ.get("HOST", "0.0.0.0")
PORT = int(os.environ.get("PORT", 8000))

print(f"=== PORT BINDING TEST ===")
print(f"Host: {HOST}")
print(f"Port: {PORT}")

# Test if port is available
def test_port_binding():
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.bind((HOST, PORT))
        sock.close()
        print(f"✅ Port {PORT} is available for binding")
        return True
    except Exception as e:
        print(f"❌ Cannot bind to port {PORT}: {e}")
        return False

# Create minimal FastAPI app
app = FastAPI(title="Port Test")

@app.get("/")
async def root():
    return {"message": "Port test server running", "host": HOST, "port": PORT}

@app.get("/health")
async def health():
    return {"status": "healthy", "timestamp": time.time()}

def main():
    print("Testing port availability...")
    if not test_port_binding():
        return
    
    print("Starting minimal server...")
    try:
        uvicorn.run(
            app,
            host=HOST,
            port=PORT,
            log_level="info"
        )
    except Exception as e:
        print(f"Server failed to start: {e}")

if __name__ == "__main__":
    main()

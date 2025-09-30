#!/usr/bin/env python3
"""
Most basic HTTP server possible - no FastAPI, just Python stdlib
"""

import os
import sys
import time
import json
from http.server import HTTPServer, BaseHTTPRequestHandler
import threading

# Get Railway environment
HOST = os.environ.get("HOST", "0.0.0.0")
PORT = int(os.environ.get("PORT", 8000))

print(f"=== BASIC HTTP SERVER ===")
print(f"Python: {sys.version}")
print(f"Host: {HOST}")
print(f"Port: {PORT}")
print(f"Working dir: {os.getcwd()}")

class HealthHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        print(f"Received GET request: {self.path}")
        
        if self.path == "/health":
            response = {
                "status": "healthy",
                "timestamp": time.time(),
                "message": "Basic HTTP server working"
            }
        elif self.path == "/":
            response = {
                "message": "Basic HTTP server is running",
                "host": HOST,
                "port": PORT,
                "python": sys.version
            }
        else:
            self.send_response(404)
            self.end_headers()
            return
        
        # Send response
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(response).encode())
    
    def log_message(self, format, *args):
        print(f"HTTP: {format % args}")

def run_server():
    try:
        server = HTTPServer((HOST, PORT), HealthHandler)
        print(f"✅ HTTP server created successfully")
        print(f"🚀 Starting server on {HOST}:{PORT}")
        print("Server should respond to /health and / endpoints")
        server.serve_forever()
    except Exception as e:
        print(f"❌ HTTP server failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    run_server()

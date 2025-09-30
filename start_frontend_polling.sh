#!/bin/bash

# Thinkerbell Frontend with Polling Mode
# Uses polling instead of file watchers to avoid ENOSPC errors

echo "🎨 Starting Thinkerbell Frontend (Polling Mode)"
echo "=============================================="

# Check if we're in the right directory
if [ ! -d "thinkerbell" ]; then
    echo "❌ Error: thinkerbell directory not found. Please run from the Thinkerbell root directory."
    exit 1
fi

cd thinkerbell

# Check if package.json exists
if [ ! -f "package.json" ]; then
    echo "❌ Error: package.json not found in thinkerbell directory."
    exit 1
fi

# Check if node_modules exists
if [ ! -d "node_modules" ]; then
    echo "📦 Installing frontend dependencies..."
    npm install
fi

echo ""
echo "🔗 Frontend will connect to backend at: http://localhost:8000"
echo "⚠️  Make sure the backend API server is running first!"
echo ""
echo "🔄 Using polling mode to avoid file watcher limits..."
echo "🚀 Starting frontend development server..."
echo ""

# Set environment variable to use polling and start Vite
CHOKIDAR_USEPOLLING=true npm run dev

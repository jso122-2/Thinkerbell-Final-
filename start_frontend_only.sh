#!/bin/bash

# Thinkerbell Frontend Development Server Launcher
# Starts only the React frontend (requires backend to be running separately)

echo "🎨 Starting Thinkerbell Frontend Development Server"
echo "================================================="

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
echo "🚀 Starting frontend development server..."
echo ""

# Start the frontend development server
npm run dev


#!/bin/bash

# Thinkerbell Full-Stack Development Launcher
# Starts both backend API and frontend React app

echo "🚀 Starting Thinkerbell Full-Stack Development Environment"
echo "=========================================================="

# Check if we're in the right directory
if [ ! -f "backend_api_server.py" ]; then
    echo "❌ Error: backend_api_server.py not found. Please run from the Thinkerbell root directory."
    exit 1
fi

# Check if thinkerberll environment is available
if ! command -v mamba &> /dev/null; then
    echo "⚠️  Warning: mamba not found. Using conda/pip instead."
    PYTHON_CMD="python3"
else
    echo "🔄 Activating thinkerberll environment..."
    source ~/.bashrc
    mamba activate thinkerberll 2>/dev/null || {
        echo "⚠️  Warning: Could not activate thinkerberll environment. Using system python."
        PYTHON_CMD="python3"
    }
    PYTHON_CMD="python3"
fi

# Function to cleanup background processes
cleanup() {
    echo ""
    echo "🛑 Shutting down services..."
    
    # Kill backend if running
    if [ ! -z "$BACKEND_PID" ]; then
        echo "   Stopping backend API (PID: $BACKEND_PID)..."
        kill $BACKEND_PID 2>/dev/null
    fi
    
    # Kill frontend if running
    if [ ! -z "$FRONTEND_PID" ]; then
        echo "   Stopping frontend dev server (PID: $FRONTEND_PID)..."
        kill $FRONTEND_PID 2>/dev/null
    fi
    
    echo "✅ All services stopped."
    exit 0
}

# Set up signal handlers
trap cleanup SIGINT SIGTERM

# Start Backend API Server
echo ""
echo "🔧 Starting Backend API Server..."
echo "   Model: /home/black-cat/Documents/Thinkerbell/Thinkerbell_template_pipeline/training/models/thinkerbell-encoder-best"
echo "   Port: 8000"

$PYTHON_CMD backend_api_server.py &
BACKEND_PID=$!

# Wait a moment for backend to start
sleep 3

# Check if backend started successfully
if ! ps -p $BACKEND_PID > /dev/null; then
    echo "❌ Backend failed to start. Check the logs above."
    exit 1
fi

echo "✅ Backend API running at http://localhost:8000"

# Start Frontend Development Server
echo ""
echo "🎨 Starting Frontend Development Server..."
echo "   Port: 5173 (Vite default)"

cd thinkerbell

# Check if node_modules exists
if [ ! -d "node_modules" ]; then
    echo "📦 Installing frontend dependencies..."
    npm install
fi

# Start the frontend
npm run dev &
FRONTEND_PID=$!

cd ..

# Wait a moment for frontend to start
sleep 3

echo ""
echo "🎉 Full-Stack Development Environment Ready!"
echo "=========================================="
echo ""
echo "🔗 Services:"
echo "   📡 Backend API:  http://localhost:8000"
echo "   🌐 Frontend:     http://localhost:5173"
echo "   📚 API Docs:     http://localhost:8000/docs"
echo ""
echo "🧪 Quick Tests:"
echo "   curl http://localhost:8000/health"
echo "   curl http://localhost:8000/model/info"
echo ""
echo "💡 Features Available:"
echo "   ✅ Text Similarity Comparison"
echo "   ✅ Document Search & Ranking"
echo "   ✅ Content Analysis (Influencer Agreements)"
echo "   ✅ Real-time Model Inference"
echo "   ✅ Interactive Testing Interface"
echo ""
echo "Press Ctrl+C to stop all services"
echo ""

# Keep the script running and monitor processes
while true; do
    # Check if backend is still running
    if ! ps -p $BACKEND_PID > /dev/null; then
        echo "❌ Backend process died. Restarting..."
        $PYTHON_CMD backend_api_server.py &
        BACKEND_PID=$!
        sleep 2
    fi
    
    # Check if frontend is still running
    if ! ps -p $FRONTEND_PID > /dev/null; then
        echo "❌ Frontend process died. Restarting..."
        cd thinkerbell
        npm run dev &
        FRONTEND_PID=$!
        cd ..
        sleep 2
    fi
    
    sleep 5
done


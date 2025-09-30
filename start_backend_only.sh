#!/bin/bash

# Thinkerbell Backend API Server Launcher
# Starts only the backend API server for testing

echo "🔧 Starting Thinkerbell Backend API Server"
echo "=========================================="

# Check if we're in the right directory
if [ ! -f "backend_api_server.py" ]; then
    echo "❌ Error: backend_api_server.py not found. Please run from the Thinkerbell root directory."
    exit 1
fi

# Check if thinkerberll environment is available
if command -v mamba &> /dev/null; then
    echo "🔄 Activating thinkerberll environment..."
    source ~/.bashrc
    mamba activate thinkerberll 2>/dev/null || {
        echo "⚠️  Warning: Could not activate thinkerberll environment. Using system python."
    }
fi

echo ""
echo "📊 Model Information:"
echo "   Path: /home/black-cat/Documents/Thinkerbell/Thinkerbell_template_pipeline/training/models/thinkerbell-encoder-best"
echo "   Performance: 96.4% accuracy, 84.5% Recall@5"
echo "   Dimension: 384"
echo ""
echo "🚀 Starting server on http://localhost:8000..."
echo ""

# Start the backend server
python3 backend_api_server.py


#!/bin/bash

# Thinkerbell Production Deployment Script
# Deploys the clean production version of Thinkerbell

set -e  # Exit on any error

echo "🚀 Thinkerbell Production Deployment"
echo "===================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if we're in the right directory
if [ ! -f "backend_api_server.py" ]; then
    print_error "backend_api_server.py not found. Please run from the Thinkerbell root directory."
    exit 1
fi

print_status "Checking system requirements..."

# Check Python version
if ! command -v python3 &> /dev/null; then
    print_error "Python 3 is required but not installed."
    exit 1
fi

PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
print_success "Python $PYTHON_VERSION found"

# Check if model exists
if [ ! -d "models/thinkerbell-encoder-best" ] && [ ! -d "models/optimum-model" ]; then
    print_warning "No model found in models/ directory. Please ensure model is available."
fi

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    print_status "Creating virtual environment..."
    python3 -m venv venv
    print_success "Virtual environment created"
fi

# Activate virtual environment
print_status "Activating virtual environment..."
source venv/bin/activate

# Install production requirements
print_status "Installing production dependencies..."
if [ -f "requirements_production.txt" ]; then
    pip install -r requirements_production.txt
elif [ -f "requirements/prod.txt" ]; then
    pip install -r requirements/prod.txt
elif [ -f "requirements/base.txt" ]; then
    pip install -r requirements/base.txt
else
    print_error "No requirements file found. Please ensure requirements_production.txt exists."
    exit 1
fi
print_success "Dependencies installed"

# Create logs directory
mkdir -p logs

# Set environment variables for production
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
export THINKERBELL_ENV="production"

# Function to check if port is available
check_port() {
    local port=$1
    if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null ; then
        return 1
    else
        return 0
    fi
}

# Check if port 8000 is available
if ! check_port 8000; then
    print_warning "Port 8000 is already in use. Attempting to stop existing process..."
    pkill -f "backend_api_server.py" || true
    sleep 2
fi

print_status "Starting Thinkerbell backend server..."

# Start the backend server in production mode
nohup python3 backend_api_server.py > logs/backend.log 2>&1 &
BACKEND_PID=$!

# Wait a moment for server to start
sleep 3

# Check if server started successfully
if ps -p $BACKEND_PID > /dev/null; then
    print_success "Backend server started successfully (PID: $BACKEND_PID)"
    echo $BACKEND_PID > logs/backend.pid
else
    print_error "Failed to start backend server. Check logs/backend.log for details."
    exit 1
fi

# Test the server
print_status "Testing server health..."
sleep 2

if curl -s http://localhost:8000/health > /dev/null; then
    print_success "Server is responding to health checks"
else
    print_error "Server health check failed"
    exit 1
fi

# Display deployment information
echo ""
echo "🎉 Deployment Complete!"
echo "======================"
echo ""
echo "📡 Backend API:     http://localhost:8000"
echo "📚 API Docs:        http://localhost:8000/docs"
echo "🌐 Webapp:          Open simple_webapp.html in your browser"
echo ""
echo "📊 Status:"
echo "   Backend PID:     $BACKEND_PID"
echo "   Log file:        logs/backend.log"
echo "   PID file:        logs/backend.pid"
echo ""
echo "🔧 Management Commands:"
echo "   Stop server:     kill \$(cat logs/backend.pid)"
echo "   View logs:       tail -f logs/backend.log"
echo "   Restart:         ./deploy.sh"
echo ""
echo "💡 Quick Test:"
echo "   curl http://localhost:8000/health"
echo ""

# Create a simple stop script
cat > stop.sh << 'EOF'
#!/bin/bash
echo "🛑 Stopping Thinkerbell server..."
if [ -f logs/backend.pid ]; then
    PID=$(cat logs/backend.pid)
    if ps -p $PID > /dev/null; then
        kill $PID
        echo "✅ Server stopped (PID: $PID)"
        rm -f logs/backend.pid
    else
        echo "⚠️  Server not running"
        rm -f logs/backend.pid
    fi
else
    echo "⚠️  No PID file found"
    pkill -f "backend_api_server.py" || echo "No backend processes found"
fi
EOF

chmod +x stop.sh
print_success "Created stop.sh script for easy server management"

echo ""
print_success "Thinkerbell is now running in production mode! 🚀"

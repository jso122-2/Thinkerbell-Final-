#!/bin/bash
# Thinkerbell Production Docker Build and Push Commands
# Copy and paste these commands one by one or run the entire script

echo "🐳 Thinkerbell Production Docker Build & Push Script"
echo "=================================================="

# Navigate to project directory
echo "📁 Navigating to project directory..."
cd /home/black-cat/Documents/Thinkerbell

# Check if we're in the right directory
if [ ! -f "backend_api_server.py" ]; then
    echo "❌ Error: backend_api_server.py not found. Make sure you're in the right directory."
    exit 1
fi

echo "✅ Found backend_api_server.py - we're in the right directory"

# Build the production Docker image
echo "🔨 Building production Docker image (this will take 10-15 minutes)..."
echo "Building with full AI dependencies (PyTorch, sentence-transformers, etc.)"
docker build -f Dockerfile.production -t jacksono/thinkerbell:production -t jacksono/thinkerbell:latest .

# Check if build was successful
if [ $? -eq 0 ]; then
    echo "✅ Docker build completed successfully!"
else
    echo "❌ Docker build failed. Check the error messages above."
    exit 1
fi

# List the built images
echo "📋 Listing built images..."
docker images | grep jacksono/thinkerbell

# Test the image locally (optional - uncomment to run)
# echo "🧪 Testing image locally..."
# docker run -d -p 8000:8000 --name thinkerbell-test jacksono/thinkerbell:latest
# echo "Test container started. Visit http://localhost:8000 to test"
# echo "Stop test container with: docker stop thinkerbell-test && docker rm thinkerbell-test"

# Login to Docker Hub
echo "🔐 Logging into Docker Hub..."
echo "Please enter your Docker Hub credentials when prompted"
docker login

# Push both tags to Docker Hub
echo "🚀 Pushing production tag to Docker Hub..."
docker push jacksono/thinkerbell:production

echo "🚀 Pushing latest tag to Docker Hub..."
docker push jacksono/thinkerbell:latest

# Verify the push
echo "✅ Verifying images on Docker Hub..."
docker search jacksono/thinkerbell

echo ""
echo "🎉 SUCCESS! Your production image is now available on Docker Hub:"
echo "   - jacksono/thinkerbell:production"
echo "   - jacksono/thinkerbell:latest"
echo ""
echo "🚂 For Railway deployment, use:"
echo "   Image: jacksono/thinkerbell:latest"
echo "   Port: 8000"
echo "   Environment variables: See railway-env-vars.md"
echo ""
echo "📖 Next steps:"
echo "   1. Deploy on Railway using the Docker image"
echo "   2. Set environment variables from railway-env-vars.md"
echo "   3. Test the deployment"

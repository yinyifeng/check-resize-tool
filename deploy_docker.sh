#!/bin/bash
"""
Docker deployment script for Check Resizer Tool
"""

echo "🐳 Check Resizer - Docker Deployment"
echo "===================================="

# Build the Docker image
echo "📦 Building Docker image..."
docker build -t check-resizer:latest .

if [ $? -eq 0 ]; then
    echo "✅ Docker image built successfully!"
    
    echo "🚀 Starting Check Resizer container..."
    docker run -d \
        --name check-resizer \
        -p 8501:8501 \
        --restart unless-stopped \
        check-resizer:latest
    
    if [ $? -eq 0 ]; then
        echo "✅ Check Resizer is now running!"
        echo "🌐 Access the application at: http://localhost:8501"
        echo ""
        echo "📋 Container Management Commands:"
        echo "  Stop:    docker stop check-resizer"
        echo "  Start:   docker start check-resizer"
        echo "  Remove:  docker rm -f check-resizer"
        echo "  Logs:    docker logs check-resizer"
    else
        echo "❌ Failed to start container"
    fi
else
    echo "❌ Failed to build Docker image"
fi
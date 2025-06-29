#!/bin/bash

# Fix Docker deployment issues

set -e

echo "Fixing Docker deployment..."

# Stop any running containers
echo "Stopping containers..."
docker-compose down

# Train model locally first
echo "Training Rasa model..."
cd backend
if [ ! -f "models/*.tar.gz" ]; then
    rasa train
fi
cd ..

# Rebuild containers without cache
echo "Rebuilding containers..."
docker-compose build --no-cache

# Start services
echo "Starting services..."
docker-compose up -d

# Wait and check status
sleep 10
echo "Service status:"
docker-compose ps

echo ""
echo "If issues persist, check logs with:"
echo "docker-compose logs rasa-server"
echo "docker-compose logs rasa-actions"
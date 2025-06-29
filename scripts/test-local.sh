#!/bin/bash

# Local testing script

set -e

echo "Starting local Docker testing..."

# Check if .env exists
if [ ! -f .env ]; then
    echo "Creating .env from template..."
    cp .env.docker .env
    echo "Please edit .env with your OPENWEATHER_API_KEY"
    exit 1
fi

# Build and start services
echo "Building services..."
docker-compose build

echo "Starting services..."
docker-compose up -d

# Wait for services to start
echo "Waiting for services to start..."
sleep 10

# Check service status
echo "Service status:"
docker-compose ps

echo ""
echo "Testing complete!"
echo "Frontend: http://localhost:3000"
echo "Rasa API: http://localhost:5005"
echo ""
echo "To stop: docker-compose down"
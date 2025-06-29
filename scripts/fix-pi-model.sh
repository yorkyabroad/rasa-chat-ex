#!/bin/bash

# Fix missing model issue on Raspberry Pi

echo "Fixing Rasa model issue on Pi..."

# Stop services
docker-compose -f docker-compose.pi.yml down

# Rebuild Rasa server with model training
echo "Rebuilding Rasa server (this may take 10-15 minutes on Pi)..."
docker-compose -f docker-compose.pi.yml build --no-cache rasa-server

# Start services
docker-compose -f docker-compose.pi.yml up -d

# Wait for startup
echo "Waiting for services to start..."
sleep 30

# Check model
echo "Checking if model exists..."
docker-compose -f docker-compose.pi.yml exec rasa-server ls -la models/

echo ""
echo "If model exists, test with:"
echo "curl -X POST http://localhost:5005/webhooks/rest/webhook -H 'Content-Type: application/json' -d '{\"sender\":\"test\",\"message\":\"hello\"}'"
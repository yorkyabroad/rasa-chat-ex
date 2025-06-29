#!/bin/bash

# Test weather functionality end-to-end

echo "Testing weather functionality..."

# Test Rasa API with weather query
echo "Sending weather query to Rasa..."
curl -X POST http://localhost:5005/webhooks/rest/webhook \
  -H "Content-Type: application/json" \
  -d '{"sender":"test","message":"current weather in Stockholm"}' \
  -w "\nHTTP Status: %{http_code}\n"

echo ""
echo "If you see a response with weather data, the system is working!"
echo "If you see an error about actions server, check:"
echo "1. docker-compose logs rasa-actions"
echo "2. docker-compose ps (ensure all services are running)"
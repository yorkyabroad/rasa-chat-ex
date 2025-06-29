#!/bin/bash

# Test connection between services

echo "Checking Docker containers..."
docker-compose ps

echo ""
echo "Checking if Rasa server is ready..."
for i in {1..30}; do
    if curl -s http://localhost:5005 > /dev/null 2>&1; then
        echo "Rasa server is responding"
        break
    fi
    echo "Waiting for Rasa server... ($i/30)"
    sleep 2
done

echo ""
echo "Testing Rasa API endpoint..."
curl -X POST http://localhost:5005/webhooks/rest/webhook \
  -H "Content-Type: application/json" \
  -d '{"sender":"test","message":"hello"}' \
  -w "\nHTTP Status: %{http_code}\n" \
  --connect-timeout 10

echo ""
echo "Testing actions server..."
# Check if actions server port is open (avoid HEAD request which isn't supported)
if nc -z localhost 5055 2>/dev/null; then
    echo "Actions server port 5055 is open"
else
    echo "Actions server port 5055 is not accessible"
fi

echo ""
echo "Testing frontend..."
curl -I http://localhost:3000

echo ""
echo "If issues persist:"
echo "1. Check logs: docker-compose logs rasa-server"
echo "2. Check actions logs: docker-compose logs rasa-actions"
echo "3. Check if model trained: docker-compose exec rasa-server ls -la models/"
echo "4. Restart services: docker-compose restart"
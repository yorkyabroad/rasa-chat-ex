#!/bin/bash

# Quick E2E test with single query

echo "Starting quick E2E test..."

# Start servers in background
echo "Starting Rasa actions server..."
rasa run actions --debug &
ACTIONS_PID=$!

echo "Starting Rasa server..."
rasa run --enable-api --port 5005 &
RASA_PID=$!

# Wait for startup
echo "Waiting for servers to start (actions server takes 3-4 minutes)..."
sleep 240  # 4 minutes

# Test single query
echo "Testing single weather query..."
curl -X POST http://localhost:5005/webhooks/rest/webhook \
  -H "Content-Type: application/json" \
  -d '{"sender":"test","message":"current weather in Paris"}' \
  --max-time 10

echo -e "\n\nStopping servers..."
kill $RASA_PID $ACTIONS_PID 2>/dev/null || true

echo "Quick test complete."
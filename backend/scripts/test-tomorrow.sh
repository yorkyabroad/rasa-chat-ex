#!/bin/bash

# Test tomorrow entity extraction

echo "Testing tomorrow entity extraction..."

# Test precipitation queries
echo "1. Testing precipitation tomorrow:"
curl -X POST http://localhost:5005/webhooks/rest/webhook \
  -H "Content-Type: application/json" \
  -d '{"sender":"test","message":"will it rain in Stockholm tomorrow?"}' \
  | jq '.[].text' || echo "No response"

echo -e "\n2. Testing chance of rain tomorrow:"
curl -X POST http://localhost:5005/webhooks/rest/webhook \
  -H "Content-Type: application/json" \
  -d '{"sender":"test","message":"what is the chance of rain in London tomorrow?"}' \
  | jq '.[].text' || echo "No response"

echo -e "\n3. Testing wind tomorrow:"
curl -X POST http://localhost:5005/webhooks/rest/webhook \
  -H "Content-Type: application/json" \
  -d '{"sender":"test","message":"wind in Stockholm tomorrow"}' \
  | jq '.[].text' || echo "No response"

echo -e "\nCheck the Rasa server logs for debug information about time_period extraction."
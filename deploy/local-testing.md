# Local Docker Testing Guide

## Prerequisites
- Docker and Docker Compose installed
- OpenWeather API key

## Local Testing Steps

### 1. Prepare Environment
```bash
# Copy environment template
cp .env.docker .env

# Edit with your API key
nano .env
# Set: OPENWEATHER_API_KEY=your_actual_api_key
```

### 2. Build and Test Locally
```bash
# Build all services
docker-compose build

# Start services for testing
docker-compose up -d

# Check all services are running
docker-compose ps
```

### 3. Test Application
- Frontend: http://localhost:3000
- Rasa API: http://localhost:5005
- Actions server: http://localhost:5055

### 4. Test Production Configuration
```bash
# Test production setup locally
docker-compose -f docker-compose.prod.yml build
docker-compose -f docker-compose.prod.yml up -d

# Access on port 80
# Frontend: http://localhost
```

### 5. Cleanup
```bash
# Stop services
docker-compose down

# Remove images (optional)
docker-compose down --rmi all
```

## Troubleshooting

### Common Issues

**"rasa: executable file not found"**
```bash
# Rebuild containers to ensure Rasa is installed
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

**"Connection reset by peer" / Server not ready**
```bash
# Check container status
docker-compose ps

# Check Rasa server logs
docker-compose logs rasa-server

# Wait for server to fully start (can take 2-3 minutes)
./scripts/test-connection.sh

# If still failing, restart with fresh build
docker-compose down
docker-compose build --no-cache rasa-server
docker-compose up -d
```

**"Could not connect to the chatbot" / CORS Issues**
```bash
# Check if Rasa server is accessible
curl http://localhost:5005/webhooks/rest/webhook -X POST -H "Content-Type: application/json" -d '{"sender":"test","message":"hello"}'

# If that works, rebuild frontend to pick up environment changes
docker-compose build frontend
docker-compose up -d
```

**"Cannot connect to host localhost:5055" / Actions server not reachable**
```bash
# Check if actions server is running
docker-compose ps
docker-compose logs rasa-actions

# Restart actions server
docker-compose restart rasa-actions

# If still failing, rebuild both servers
docker-compose down
docker-compose build rasa-actions rasa-server
docker-compose up -d
```

**Check if model exists**
```bash
# Train model locally first
cd backend
rasa train

# Then rebuild containers
docker-compose build
```

### General Debugging
```bash
# View logs
docker-compose logs [service-name]

# Rebuild specific service
docker-compose build [service-name]

# Access container shell
docker-compose exec [service-name] /bin/bash

# Check if rasa is installed in container
docker-compose exec rasa-server which rasa
```
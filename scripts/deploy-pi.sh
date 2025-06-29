#!/bin/bash

# Deployment script for Raspberry Pi 4

set -e

# Configuration
PI_IP=${1:-"192.168.1.200"}
PI_USER=${2:-"pi"}
PROJECT_DIR="/home/pi/rasa-chat"

echo "Deploying to Raspberry Pi: $PI_IP"

# Create deployment package
echo "Creating deployment package..."
tar -czf rasa-chat-pi-deploy.tar.gz \
    --exclude='.git' \
    --exclude='node_modules' \
    --exclude='__pycache__' \
    --exclude='.rasa' \
    --exclude='models' \
    --exclude='venv' \
    --exclude='.env' \
    --exclude='htmlcov' \
    --exclude='test-results' \
    --exclude='playwright-report' \
    --exclude='*.tar.gz' \
    .

# Copy to Pi
echo "Copying files to Pi..."
scp rasa-chat-pi-deploy.tar.gz $PI_USER@$PI_IP:/tmp/

# Deploy on Pi
echo "Deploying on Pi..."
ssh $PI_USER@$PI_IP << EOF
    cd /tmp
    mkdir -p $PROJECT_DIR
    tar -xzf rasa-chat-pi-deploy.tar.gz -C $PROJECT_DIR
    cd $PROJECT_DIR
    
    # Set environment
    cp .env.docker .env
    sed -i "s/NAS_IP=.*/PI_IP=$PI_IP/" .env
    echo "PI_IP=$PI_IP" >> .env
    
    # Build frontend with correct URL first
    docker-compose -f docker-compose.pi.yml --env-file .env build frontend
    
    # Deploy with Pi-specific compose
    docker-compose -f docker-compose.pi.yml --env-file .env up -d
    
    # Cleanup
    rm /tmp/rasa-chat-pi-deploy.tar.gz
EOF

# Cleanup local
rm rasa-chat-pi-deploy.tar.gz

echo "Deployment complete!"
echo "Frontend: http://$PI_IP"
echo "API: http://$PI_IP:5005"
echo ""
echo "Note: Initial startup may take 5-10 minutes on Raspberry Pi"
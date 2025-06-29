#!/bin/bash

# Deployment script for Synology NAS

set -e

# Configuration
NAS_IP=${1:-"192.168.1.100"}
NAS_USER=${2:-"admin"}
PROJECT_DIR="/volume1/docker/rasa-chat"

echo "Deploying to NAS: $NAS_IP"

# Create deployment package
echo "Creating deployment package..."
tar -czf rasa-chat-deploy.tar.gz \
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

# Copy to NAS
echo "Copying files to NAS..."
scp rasa-chat-deploy.tar.gz $NAS_USER@$NAS_IP:/tmp/

# Deploy on NAS
echo "Deploying on NAS..."
ssh $NAS_USER@$NAS_IP << EOF
    cd /tmp
    sudo mkdir -p $PROJECT_DIR
    sudo tar -xzf rasa-chat-deploy.tar.gz -C $PROJECT_DIR
    cd $PROJECT_DIR
    
    # Set environment
    cp .env.docker .env
    sed -i "s/192.168.1.100/$NAS_IP/g" .env
    
    # Deploy
    docker-compose -f docker-compose.prod.yml --env-file .env up -d
    
    # Cleanup
    rm /tmp/rasa-chat-deploy.tar.gz
EOF

# Cleanup local
rm rasa-chat-deploy.tar.gz

echo "Deployment complete!"
echo "Frontend: http://$NAS_IP"
echo "API: http://$NAS_IP:5005"
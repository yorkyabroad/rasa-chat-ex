# Synology NAS Deployment Guide

## Prerequisites
- Synology NAS with Docker package installed
- SSH access to NAS
- Git package installed (optional, for direct deployment)

## Deployment Steps

### 1. Prepare Files on NAS
```bash
# SSH into your NAS
ssh admin@your-nas-ip

# Create project directory
mkdir -p /volume1/docker/rasa-chat
cd /volume1/docker/rasa-chat

# Copy project files (via SCP, Git, or File Station)
```

### 2. Configure Environment
```bash
# Copy and edit environment file
cp .env.docker .env
nano .env

# Set your values:
# OPENWEATHER_API_KEY=your_actual_api_key
# NAS_IP=your_nas_ip_address
```

### 3. Deploy with Docker Compose
```bash
# For production deployment
docker-compose -f docker-compose.prod.yml --env-file .env up -d

# Check status
docker-compose -f docker-compose.prod.yml ps
```

### 4. Access Application
- Frontend: http://your-nas-ip
- Rasa API: http://your-nas-ip:5005

## Synology Container Manager
Alternatively, use Synology's Container Manager GUI:
1. Import docker-compose.prod.yml
2. Set environment variables in the interface
3. Deploy the project

## Troubleshooting
```bash
# View logs
docker-compose -f docker-compose.prod.yml logs

# Restart services
docker-compose -f docker-compose.prod.yml restart

# Update deployment
docker-compose -f docker-compose.prod.yml pull
docker-compose -f docker-compose.prod.yml up -d
```
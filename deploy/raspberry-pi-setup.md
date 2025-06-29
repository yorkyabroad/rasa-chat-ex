# Raspberry Pi 4 Deployment Guide

## Prerequisites
- Raspberry Pi 4 (4GB+ RAM recommended)
- Raspberry Pi OS (64-bit) or Ubuntu Server
- Docker and Docker Compose installed
- SSH access enabled

## Initial Setup

### 1. Install Docker
```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Fix locale warnings (optional)
sudo locale-gen en_GB.UTF-8
export LC_ALL=en_GB.UTF-8
export LANG=en_GB.UTF-8

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER

# Install Docker Compose
sudo apt install docker-compose -y

# Reboot to apply group changes
sudo reboot
```

### 2. Optimize for ARM64
```bash
# Increase swap (recommended for Rasa)
sudo dphys-swapfile swapoff
sudo sed -i 's/CONF_SWAPSIZE=100/CONF_SWAPSIZE=2048/' /etc/dphys-swapfile
sudo dphys-swapfile setup
sudo dphys-swapfile swapon

# Enable memory cgroup
sudo sed -i '$ s/$/ cgroup_enable=memory cgroup_memory=1/' /boot/cmdline.txt
sudo reboot
```

## Deployment Steps

### 1. Prepare Files
```bash
# Option 1: Use deployment script (recommended)
./scripts/deploy-pi.sh YOUR_PI_IP

# Option 2: Manual copy (excludes unnecessary files)
scp -r --exclude='node_modules' --exclude='venv' --exclude='.git' \
    rasa-chat/ pi@raspberry-pi-ip:/home/pi/

# Option 3: Git clone on Pi
ssh pi@raspberry-pi-ip
git clone <your-repo> /home/pi/rasa-chat
cd /home/pi/rasa-chat
```

### 2. Configure Environment
```bash
# Copy and edit environment file
cp .env.docker .env
nano .env

# Set your values:
# OPENWEATHER_API_KEY=your_actual_api_key
# NAS_IP=your_pi_ip_address
```

### 3. Deploy Services
```bash
# Use production compose file
docker-compose -f docker-compose.prod.yml --env-file .env up -d

# Monitor startup (Rasa takes time on Pi)
docker-compose -f docker-compose.prod.yml logs -f
```

### 4. Access Application
- Frontend: http://your-pi-ip
- Rasa API: http://your-pi-ip:5005

## Performance Optimization

### Memory Management
```bash
# Monitor memory usage
docker stats

# Restart services if needed
docker-compose -f docker-compose.prod.yml restart
```

### Auto-start on Boot
```bash
# Create systemd service
sudo nano /etc/systemd/system/rasa-chat.service
```

Add service configuration:
```ini
[Unit]
Description=Rasa Chat Application
Requires=docker.service
After=docker.service

[Service]
Type=oneshot
RemainAfterExit=yes
WorkingDirectory=/home/pi/rasa-chat
ExecStart=/usr/bin/docker-compose -f docker-compose.prod.yml --env-file .env up -d
ExecStop=/usr/bin/docker-compose -f docker-compose.prod.yml down
User=pi

[Install]
WantedBy=multi-user.target
```

Enable service:
```bash
sudo systemctl enable rasa-chat.service
sudo systemctl start rasa-chat.service
```

## Troubleshooting

### Common Issues
```bash
# Check system resources
free -h
df -h

# View container logs
docker-compose -f docker-compose.prod.yml logs [service-name]

# Restart specific service
docker-compose -f docker-compose.prod.yml restart [service-name]

# Clean up Docker resources
docker system prune -f
```

### Model Training Issues
```bash
# If "No valid model found" error
docker-compose -f docker-compose.pi.yml logs rasa-server

# Rebuild Rasa server to ensure model is trained
docker-compose -f docker-compose.pi.yml build --no-cache rasa-server
docker-compose -f docker-compose.pi.yml up -d

# Check if model exists
docker-compose -f docker-compose.pi.yml exec rasa-server ls -la models/
```

### Frontend Connection Issues
```bash
# If frontend shows "localhost:5005" error, rebuild with correct IP
PI_IP=192.168.1.200  # Your Pi's IP
echo "PI_IP=$PI_IP" >> .env
docker-compose -f docker-compose.pi.yml --env-file .env build frontend
docker-compose -f docker-compose.pi.yml --env-file .env up -d
```

### Performance Tips
- Use external storage (USB 3.0 SSD) for better I/O
- Monitor temperature: `vcgencmd measure_temp`
- Consider using lighter base images for ARM64
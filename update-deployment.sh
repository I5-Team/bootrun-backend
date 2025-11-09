#!/bin/bash
# Quick update script for EC2 dev server
# Run this ON YOUR EC2 INSTANCE when you push new changes

set -e

echo "=========================================="
echo "🔄 Updating BootRun API on EC2"
echo "=========================================="

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Navigate to project directory
cd /home/ubuntu/bootrun-backend

# Stash any local changes
echo -e "${BLUE} Stashing local changes...${NC}"
git stash

# Pull latest changes
echo -e "${BLUE} Pulling latest changes from Git...${NC}"
git pull origin main

# Rebuild containers
echo -e "${BLUE}  Rebuilding containers...${NC}"
docker-compose down
docker-compose up -d --build

# Wait for services
echo -e "${BLUE} Waiting for services to start...${NC}"
sleep 10

# Run migrations
echo -e "${BLUE} Running database migrations...${NC}"
docker-compose exec -T app alembic upgrade head || echo -e "${YELLOW}⚠️  No migrations to run${NC}"

# Show status
echo -e "${BLUE} Service status:${NC}"
docker-compose ps

# Get public IP
PUBLIC_IP=$(curl -s http://169.254.169.254/latest/meta-data/public-ipv4)

echo ""
echo "=========================================="
echo -e "${GREEN} Update Complete!${NC}"
echo "=========================================="
echo -e "${GREEN} API: http://$PUBLIC_IP:8000${NC}"
echo -e "${GREEN} Docs: http://$PUBLIC_IP:8000/docs${NC}"
echo ""
echo -e "${BLUE}View logs:${NC} docker-compose logs -f app"
echo "=========================================="

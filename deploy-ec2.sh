#!/bin/bash
# EC2 Development Server Deployment Script
set -e

echo "=========================================="
echo "BootRun API - EC2 Dev Deployment"
echo "=========================================="

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Update system
echo -e "${BLUE} Updating system packages...${NC}"
sudo apt-get update
sudo apt-get upgrade -y

# Install Docker
echo -e "${BLUE} Installing Docker...${NC}"
if ! command -v docker &> /dev/null; then
    curl -fsSL https://get.docker.com -o get-docker.sh
    sudo sh get-docker.sh
    sudo usermod -aG docker $USER
    rm get-docker.sh
    echo -e "${GREEN} Docker installed${NC}"
else
    echo -e "${GREEN} Docker already installed${NC}"
fi

# Install Docker Compose
echo -e "${BLUE} Installing Docker Compose...${NC}"
if ! command -v docker-compose &> /dev/null; then
    sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    sudo chmod +x /usr/local/bin/docker-compose
    echo -e "${GREEN} Docker Compose installed${NC}"
else
    echo -e "${GREEN} Docker Compose already installed${NC}"
fi

# Install Git
echo -e "${BLUE} Installing Git...${NC}"
sudo apt-get install -y git

# Clone or pull repository
REPO_DIR="/home/ubuntu/bootrun-backend"
if [ -d "$REPO_DIR" ]; then
    echo -e "${BLUE} Updating existing repository...${NC}"
    cd $REPO_DIR
    git pull
else
    echo -e "${BLUE} Cloning repository...${NC}"
    echo "Please enter your repository URL:"
    read REPO_URL
    git clone $REPO_URL $REPO_DIR
    cd $REPO_DIR
fi

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo -e "${RED}  .env file not found!${NC}"
    echo -e "${BLUE}Creating .env from .env.example...${NC}"
    cp .env.example .env
    echo -e "${RED}  IMPORTANT: Edit .env file with your actual credentials!${NC}"
    echo "Press Enter to edit .env file now, or Ctrl+C to exit and edit manually"
    read
    nano .env
fi

# Stop existing containers
echo -e "${BLUE} Stopping existing containers...${NC}"
docker-compose down || true

# Build and start containers
echo -e "${BLUE}  Building and starting containers...${NC}"
docker-compose up -d --build

# Wait for services to be ready
echo -e "${BLUE} Waiting for services to start...${NC}"
sleep 10

# Check container status
echo -e "${BLUE} Container status:${NC}"
docker-compose ps

# Get EC2 public IP
PUBLIC_IP=$(curl -s http://169.254.169.254/latest/meta-data/public-ipv4)

echo ""
echo "=========================================="
echo -e "${GREEN} Deployment Complete!${NC}"
echo "=========================================="
echo ""
echo -e "${GREEN} API URL: http://$PUBLIC_IP:8000${NC}"
echo -e "${GREEN} API Docs: http://$PUBLIC_IP:8000/docs${NC}"
echo -e "${GREEN} Health Check: http://$PUBLIC_IP:8000/health${NC}"
echo ""
echo -e "${BLUE} Share this with your frontend team:${NC}"
echo "   Base URL: http://$PUBLIC_IP:8000"
echo ""
echo -e "${BLUE} Useful commands:${NC}"
echo "   View logs: docker-compose logs -f"
echo "   Restart: docker-compose restart"
echo "   Stop: docker-compose down"
echo "   Rebuild: docker-compose up -d --build"
echo ""
echo "=========================================="

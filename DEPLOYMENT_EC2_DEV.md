# AWS EC2 Development Server Deployment Guide

Complete guide to deploy BootRun API to AWS EC2 for development and frontend collaboration.

---

## Prerequisites

- AWS Account with EC2 access
- AWS Access Keys (you have these)
- SSH client (PuTTY for Windows, or WSL/Git Bash)
- Git repository for your code (GitHub, GitLab, etc.)

---

## Step 1: Launch EC2 Instance

### 1.1 Go to AWS Console
1. Log in to [AWS Console](https://console.aws.amazon.com/)
2. Go to **EC2 Dashboard**
3. Click **Launch Instance**

### 1.2 Configure Instance

**Basic Settings:**
- **Name**: `bootrun-api-dev`
- **OS**: Ubuntu Server 22.04 LTS (Free tier eligible)
- **Instance Type**: `t2.medium` or `t3.medium` (recommended for dev)
  - For testing: `t2.small` (minimum)
  - For better performance: `t2.medium` or higher

**Key Pair:**
- Create new key pair or use existing
- **Name**: `bootrun-dev-key`
- **Type**: RSA
- **Format**: `.pem` (for Mac/Linux) or `.ppk` (for PuTTY)
- **Download and save securely!**

**Network Settings:**
- Create security group: `bootrun-dev-sg`
- **Inbound rules** (IMPORTANT):
  ```
  SSH          | TCP | 22   | Your IP        | For SSH access
  Custom TCP   | TCP | 8000 | 0.0.0.0/0      | API access
  PostgreSQL   | TCP | 5432 | Your IP        | (Optional) DB access
  ```

**Storage:**
- **Size**: 20 GB (minimum)
- **Type**: gp3 (recommended) or gp2

### 1.3 Launch Instance
- Click **Launch Instance**
- Wait for instance to be in "Running" state
- Note the **Public IPv4 address** (e.g., `3.35.123.456`)

---

## Step 2: Connect to EC2 Instance

### Option A: Using Git Bash / WSL (Windows)
```bash
# Set permissions for key file
chmod 400 bootrun-dev-key.pem

# Connect to EC2
ssh -i bootrun-dev-key.pem ubuntu@YOUR_EC2_PUBLIC_IP
```

### Option B: Using PuTTY (Windows)
1. Convert `.pem` to `.ppk` using PuTTYgen
2. Open PuTTY
3. Host: `ubuntu@YOUR_EC2_PUBLIC_IP`
4. Connection > SSH > Auth > Private key: Select your `.ppk` file
5. Click **Open**

---

## Step 3: Push Your Code to Git (Run Locally)

```bash
# Initialize git if not already done
git init
git add .
git commit -m "Initial commit for EC2 deployment"

# Create GitHub repository and push
git remote add origin YOUR_GITHUB_REPO_URL
git branch -M main
git push -u origin main
```

---

## Step 4: Deploy on EC2 (Automated)

### 4.1 Upload deployment script
```bash
# On your EC2 instance
curl -O https://raw.githubusercontent.com/YOUR_USERNAME/YOUR_REPO/main/deploy-ec2.sh
chmod +x deploy-ec2.sh
```

**OR** copy the script manually:
```bash
nano deploy-ec2.sh
# Paste the contents from deploy-ec2.sh
# Save: Ctrl+X, then Y, then Enter

chmod +x deploy-ec2.sh
```

### 4.2 Run deployment
```bash
./deploy-ec2.sh
```

The script will:
- Install Docker & Docker Compose
- Clone your repository
- Set up environment variables
- Start all services

### 4.3 Configure Environment Variables

When prompted, edit `.env` file:
```bash
cd /home/ubuntu/bootrun-backend
nano .env
```

**Required changes:**
1. **FERNET_KEY**: Generate with:
   ```bash
   python3 -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
   ```

2. **AWS Credentials**: Add your actual AWS keys
   ```
   AWS_ACCESS_KEY_ID=YOUR_ACTUAL_AWS_ACCESS_KEY
   AWS_SECRET_ACCESS_KEY=YOUR_ACTUAL_AWS_SECRET_KEY
   ```

3. **CORS_ORIGINS**: Add your EC2 IP
   ```
   CORS_ORIGINS=http://localhost:3000,http://YOUR_EC2_PUBLIC_IP:3000
   ```

4. **Database Passwords**: Change default passwords
   ```
   DATABASE_PASSWORD=strong_random_password_here
   REDIS_PASSWORD=another_strong_password_here
   ```

Save: `Ctrl+X`, then `Y`, then `Enter`

---

## Step 5: Start Services

```bash
cd /home/ubuntu/bootrun-backend

# Start all services
docker-compose up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f app
```

Expected output:
```
✅ bootrun_postgres - healthy
✅ bootrun_redis - healthy
✅ bootrun_api - running
```

---

## Step 6: Run Database Migrations

```bash
# Enter the app container
docker-compose exec app bash

# Run migrations
alembic upgrade head

# Exit container
exit
```

---

## Step 7: Test Your API

### 7.1 Health Check
```bash
curl http://YOUR_EC2_PUBLIC_IP:8000/health
```

Expected response:
```json
{
  "status": "healthy",
  "service": "BootRun API",
  "version": "1.0.0"
}
```

### 7.2 API Documentation
Open in browser:
```
http://YOUR_EC2_PUBLIC_IP:8000/docs
```

### 7.3 Test from local machine
```bash
curl http://YOUR_EC2_PUBLIC_IP:8000/
```

---

## Step 8: Share with Frontend Team

**Send them:**
- **Base URL**: `http://YOUR_EC2_PUBLIC_IP:8000`
- **API Docs**: `http://YOUR_EC2_PUBLIC_IP:8000/docs`
- **Health Check**: `http://YOUR_EC2_PUBLIC_IP:8000/health`

**Frontend CORS Setup:**
They can now make requests from:
- `http://localhost:3000` (React default)
- `http://localhost:5173` (Vite default)
- Any other origin you added to `CORS_ORIGINS`

---

## Useful Commands

### Container Management
```bash
# View running containers
docker-compose ps

# View logs
docker-compose logs -f app
docker-compose logs -f postgres
docker-compose logs -f redis

# Restart services
docker-compose restart

# Stop services
docker-compose down

# Rebuild and restart
docker-compose up -d --build

# Remove everything (including volumes)
docker-compose down -v
```

### Database Access
```bash
# Connect to PostgreSQL
docker-compose exec postgres psql -U bootrun_user -d bootrun_db

# Backup database
docker-compose exec postgres pg_dump -U bootrun_user bootrun_db > backup.sql
```

### Redis Access
```bash
# Connect to Redis CLI
docker-compose exec redis redis-cli -a YOUR_REDIS_PASSWORD

# Check Redis keys
docker-compose exec redis redis-cli -a YOUR_REDIS_PASSWORD KEYS "*"
```

### Application Management
```bash
# Enter app container
docker-compose exec app bash

# Run Python commands
docker-compose exec app python -c "print('Hello')"

# Run database migrations
docker-compose exec app alembic upgrade head

# Create new migration
docker-compose exec app alembic revision -m "migration message"
```

---

## Updating Your Code

When you make changes and want to deploy:

```bash
# On EC2 instance
cd /home/ubuntu/bootrun-backend

# Pull latest changes
git pull

# Rebuild and restart
docker-compose up -d --build

# Check logs
docker-compose logs -f app
```

---

## Troubleshooting

### Port 8000 not accessible
```bash
# Check if app is running
docker-compose ps

# Check app logs
docker-compose logs app

# Check if port is listening
sudo netstat -tlnp | grep 8000

# Verify EC2 Security Group allows port 8000
```

### Database connection error
```bash
# Check PostgreSQL is running
docker-compose ps postgres

# Check PostgreSQL logs
docker-compose logs postgres

# Verify environment variables
docker-compose exec app env | grep DATABASE
```

### Redis connection error
```bash
# Check Redis is running
docker-compose ps redis

# Test Redis connection
docker-compose exec redis redis-cli -a YOUR_REDIS_PASSWORD ping
```

### Container keeps restarting
```bash
# View logs for errors
docker-compose logs -f app

# Check environment variables
cat .env

# Verify all required env vars are set
```

---

## Security Notes for Dev Environment

⚠️ **Important**: This is a DEV setup, not production-ready!

**Current security limitations:**
- HTTP only (no HTTPS)
- Open CORS policy
- Port 8000 exposed to internet
- Debug mode enabled

**For production deployment, you need:**
- HTTPS/SSL certificates
- Strict CORS policy
- Nginx reverse proxy
- Firewall rules
- Secrets management (AWS Secrets Manager)
- Auto-scaling
- Load balancer
- Monitoring & logging

---

## Next Steps

1. ✅ Deploy to EC2
2. ✅ Test API endpoints
3. ✅ Share with frontend team
4. 📝 Set up CI/CD (optional)
5. 📊 Add monitoring (CloudWatch)
6. 🔐 Set up HTTPS (Let's Encrypt)

---

## Quick Reference

**EC2 Instance**: `YOUR_EC2_PUBLIC_IP`
**API Base URL**: `http://YOUR_EC2_PUBLIC_IP:8000`
**API Docs**: `http://YOUR_EC2_PUBLIC_IP:8000/docs`

**SSH**: `ssh -i bootrun-dev-key.pem ubuntu@YOUR_EC2_PUBLIC_IP`
**Project Dir**: `/home/ubuntu/bootrun-backend`

---

## Support

If you encounter issues:
1. Check logs: `docker-compose logs -f`
2. Verify environment: `cat .env`
3. Check security groups in AWS Console
4. Ensure all services are healthy: `docker-compose ps`

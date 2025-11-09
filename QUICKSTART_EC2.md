# 🚀 Quick Start - EC2 Dev Deployment

**Goal**: Get your FastAPI backend running on AWS EC2 for frontend collaboration in 30 minutes.

---

## ✅ Checklist

### Before You Start
- [ ] AWS account ready
- [ ] AWS access keys (you have these ✓)
- [ ] Code pushed to GitHub/GitLab
- [ ] SSH client installed (Git Bash, PuTTY, or WSL)

---

## 📋 5-Step Deployment

### **Step 1: Launch EC2 Instance** (10 min)

1. Go to [AWS EC2 Console](https://console.aws.amazon.com/ec2/)
2. Click **Launch Instance**
3. Configure:
   ```
   Name: bootrun-api-dev
   OS: Ubuntu 22.04 LTS
   Instance Type: t2.medium (or t2.small for testing)
   Key Pair: Create new → Download .pem file
   ```
4. **Security Group** - Add these inbound rules:
   ```
   Type          | Port | Source      | Description
   SSH           | 22   | My IP       | SSH access
   Custom TCP    | 8000 | 0.0.0.0/0   | API access
   ```
5. Click **Launch Instance**
6. **Copy Public IP** (e.g., `3.35.123.45`)

---

### **Step 2: Connect to EC2** (2 min)

**Windows (Git Bash):**
```bash
chmod 400 your-key.pem
ssh -i your-key.pem ubuntu@YOUR_EC2_IP
```

**Windows (PuTTY):**
- Convert `.pem` to `.ppk` using PuTTYgen
- Connect via PuTTY

---

### **Step 3: Push Code to Git** (3 min)

**On your local machine:**
```bash
git init
git add .
git commit -m "Deploy to EC2"
git remote add origin YOUR_GITHUB_REPO_URL
git push -u origin main
```

---

### **Step 4: Deploy on EC2** (10 min)

**On EC2 instance:**
```bash
# Download and run deployment script
wget https://raw.githubusercontent.com/YOUR_USERNAME/bootrun-backend/main/deploy-ec2.sh
chmod +x deploy-ec2.sh
./deploy-ec2.sh
```

When prompted for repository URL, enter:
```
https://github.com/YOUR_USERNAME/bootrun-backend.git
```

**Configure .env:**
```bash
cd /home/ubuntu/bootrun-backend
nano .env
```

**MUST CHANGE:**
1. **Generate FERNET_KEY:**
   ```bash
   python3 -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
   ```
   Copy output and paste into `.env`

2. **Add AWS credentials:**
   ```
   AWS_ACCESS_KEY_ID=YOUR_ACTUAL_KEY
   AWS_SECRET_ACCESS_KEY=YOUR_ACTUAL_SECRET
   ```

3. **Update CORS (replace YOUR_EC2_IP):**
   ```
   CORS_ORIGINS=http://localhost:3000,http://YOUR_EC2_IP:3000
   ```

4. **Change passwords:**
   ```
   DATABASE_PASSWORD=choose_strong_password
   REDIS_PASSWORD=another_strong_password
   ```

Save: `Ctrl+X` → `Y` → `Enter`

---

### **Step 5: Start & Test** (5 min)

```bash
cd /home/ubuntu/bootrun-backend

# Start services
docker-compose up -d

# Check status
docker-compose ps

# Run migrations
docker-compose exec app alembic upgrade head

# Test API
curl http://YOUR_EC2_IP:8000/health
```

**Open in browser:**
```
http://YOUR_EC2_IP:8000/docs
```

✅ **Success!** If you see Swagger docs, you're done!

---

## 📤 Share with Frontend Team

**Send them:**
```
API Base URL: http://YOUR_EC2_IP:8000
API Docs: http://YOUR_EC2_IP:8000/docs
Health Check: http://YOUR_EC2_IP:8000/health
```

**Example frontend request:**
```javascript
// React example
const API_BASE_URL = 'http://YOUR_EC2_IP:8000';

fetch(`${API_BASE_URL}/api/endpoint`)
  .then(res => res.json())
  .then(data => console.log(data));
```

---

## 🔄 Updating Your Code

**When you make changes:**

**1. Push to Git (local machine):**
```bash
git add .
git commit -m "Your changes"
git push
```

**2. Update EC2 (on EC2 instance):**
```bash
cd /home/ubuntu/bootrun-backend
./update-deployment.sh
```

Done! ✅

---

## 🛠️ Common Commands

```bash
# View logs
docker-compose logs -f app

# Restart services
docker-compose restart

# Stop everything
docker-compose down

# Rebuild after code changes
docker-compose up -d --build

# Access database
docker-compose exec postgres psql -U bootrun_user -d bootrun_db

# Access app container
docker-compose exec app bash
```

---

## 🐛 Troubleshooting

### Can't access API from browser
- ✅ Check EC2 Security Group allows port 8000
- ✅ Verify app is running: `docker-compose ps`
- ✅ Check logs: `docker-compose logs app`

### Database connection error
- ✅ Check DATABASE_HOST=postgres in .env
- ✅ Verify PostgreSQL is healthy: `docker-compose ps postgres`

### CORS error from frontend
- ✅ Add frontend URL to CORS_ORIGINS in .env
- ✅ Restart: `docker-compose restart app`

### "Connection refused" error
- ✅ Wait 30 seconds for services to start
- ✅ Check all services are healthy: `docker-compose ps`

---

## 📚 Full Documentation

For detailed guide, see: [DEPLOYMENT_EC2_DEV.md](./DEPLOYMENT_EC2_DEV.md)

---

## ⚡ Quick Reference

| What | Command |
|------|---------|
| **SSH to EC2** | `ssh -i your-key.pem ubuntu@YOUR_EC2_IP` |
| **Project Dir** | `cd /home/ubuntu/bootrun-backend` |
| **View Logs** | `docker-compose logs -f app` |
| **Restart** | `docker-compose restart` |
| **Update Code** | `./update-deployment.sh` |
| **API Docs** | `http://YOUR_EC2_IP:8000/docs` |

---

## 🎯 Success Criteria

✅ Can access `http://YOUR_EC2_IP:8000/docs` in browser
✅ Health check returns `{"status": "healthy"}`
✅ Frontend team can make API requests
✅ No CORS errors

**You're all set for frontend collaboration! 🎉**

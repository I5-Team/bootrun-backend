# 🚀 빠른 시작 - EC2 개발 배포 가이드

**목표**: 프론트엔드 협업을 위해 30분 안에 FastAPI 백엔드를 AWS EC2에 실행시키기

---

## ✅ 체크리스트

### 시작 전 준비
- [ ] AWS 계정 준비 완료  
- [ ] AWS 액세스 키 보유 (✓ 있음)  
- [ ] 코드가 GitHub 또는 GitLab에 업로드됨  
- [ ] SSH 클라이언트 설치됨 (Git Bash, PuTTY, 또는 WSL)

---

## 📋 5단계 배포 과정

### **1단계: EC2 인스턴스 생성** (약 10분)

1. [AWS EC2 콘솔](https://console.aws.amazon.com/ec2/) 접속  
2. **Launch Instance** 클릭  
3. 다음과 같이 설정:
   ```
   Name: bootrun-api-dev
   OS: Ubuntu 22.04 LTS
   Instance Type: t2.medium (테스트용으로는 t2.small 가능)
   Key Pair: 새로 생성 → .pem 파일 다운로드
   ```
4. **보안 그룹** - 인바운드 규칙 추가:
   ```
   유형          | 포트 | 소스        | 설명
   SSH           | 22   | My IP       | SSH 접근
   Custom TCP    | 8000 | 0.0.0.0/0   | API 접근
   ```
5. **Launch Instance** 클릭  
6. **공인 IP 복사** (예: `3.35.123.45`)

---

### **2단계: EC2 접속** (약 2분)

**Windows (Git Bash 사용 시):**
```bash
chmod 400 your-key.pem
ssh -i your-key.pem ubuntu@YOUR_EC2_IP
```

**Windows (PuTTY 사용 시):**
- `.pem` 파일을 PuTTYgen으로 `.ppk`로 변환  
- PuTTY로 접속

---

### **3단계: 코드 Git에 업로드** (약 3분)

**로컬 환경에서 실행:**
```bash
git init
git add .
git commit -m "Deploy to EC2"
git remote add origin YOUR_GITHUB_REPO_URL
git push -u origin main
```

---

### **4단계: EC2에서 배포 실행** (약 10분)

**EC2 내부에서 실행:**
```bash
# 배포 스크립트 다운로드 및 실행
wget https://raw.githubusercontent.com/YOUR_USERNAME/bootrun-backend/main/deploy-ec2.sh
chmod +x deploy-ec2.sh
./deploy-ec2.sh
```

요청 시 입력:
```
https://github.com/YOUR_USERNAME/bootrun-backend.git
```

**환경 변수(.env) 설정:**
```bash
cd /home/ubuntu/bootrun-backend
nano .env
```

**반드시 수정해야 하는 항목:**

1. **FERNET_KEY 생성:**
   ```bash
   python3 -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
   ```
   출력값을 `.env`에 복사하여 붙여넣기

2. **AWS 자격 증명 추가:**
   ```
   AWS_ACCESS_KEY_ID=YOUR_ACTUAL_KEY
   AWS_SECRET_ACCESS_KEY=YOUR_ACTUAL_SECRET
   ```

3. **CORS 수정 (YOUR_EC2_IP 교체):**
   ```
   CORS_ORIGINS=http://localhost:3000,http://YOUR_EC2_IP:3000
   ```

4. **비밀번호 변경:**
   ```
   DATABASE_PASSWORD=강력한_비밀번호
   REDIS_PASSWORD=또_다른_강력한_비밀번호
   ```

저장: `Ctrl+X` → `Y` → `Enter`

---

### **5단계: 실행 및 테스트** (약 5분)

```bash
cd /home/ubuntu/bootrun-backend

# 서비스 실행
docker-compose up -d

# 상태 확인
docker-compose ps

# 마이그레이션 실행
docker-compose exec app alembic upgrade head

# API 테스트
curl http://YOUR_EC2_IP:8000/health
```

**브라우저에서 확인:**
```
http://YOUR_EC2_IP:8000/docs
```

✅ **성공!** Swagger 문서가 보이면 완료입니다!

---

## 📤 프론트엔드 팀과 공유하기

**프론트엔드 팀에게 전달:**
```
API Base URL: http://YOUR_EC2_IP:8000
API Docs: http://YOUR_EC2_IP:8000/docs
Health Check: http://YOUR_EC2_IP:8000/health
```

**React 예시 요청:**
```javascript
const API_BASE_URL = 'http://YOUR_EC2_IP:8000';

fetch(`${API_BASE_URL}/api/endpoint`)
  .then(res => res.json())
  .then(data => console.log(data));
```

---

## 🔄 코드 업데이트

**변경사항 발생 시:**

**1. 로컬에서 푸시**
```bash
git add .
git commit -m "Your changes"
git push
```

**2. EC2에서 업데이트**
```bash
cd /home/ubuntu/bootrun-backend
./update-deployment.sh
```

✅ 완료!

---

## 🛠️ 자주 쓰는 명령어

```bash
# 로그 보기
docker-compose logs -f app

# 서비스 재시작
docker-compose restart

# 전체 중지
docker-compose down

# 코드 수정 후 재빌드
docker-compose up -d --build

# DB 접속
docker-compose exec postgres psql -U bootrun_user -d bootrun_db

# 앱 컨테이너 접속
docker-compose exec app bash
```

---

## 🐛 문제 해결

### 브라우저에서 API 접근 불가
- ✅ EC2 보안 그룹이 8000 포트를 허용하는지 확인
- ✅ 앱 실행 중인지 확인: `docker-compose ps`
- ✅ 로그 확인: `docker-compose logs app`

### 데이터베이스 연결 오류
- ✅ `.env`의 DATABASE_HOST가 postgres로 설정되어 있는지 확인
- ✅ PostgreSQL이 실행 중인지 확인: `docker-compose ps postgres`

### 프론트엔드 CORS 오류
- ✅ `.env`의 CORS_ORIGINS에 프론트 URL 추가
- ✅ 앱 재시작: `docker-compose restart app`

### "Connection refused" 오류
- ✅ 서비스 시작 후 30초 정도 대기
- ✅ 모든 서비스 상태 확인: `docker-compose ps`

---

## 📚 전체 문서

자세한 내용은 [DEPLOYMENT_EC2_DEV.md](./DEPLOYMENT_EC2_DEV.md) 참고

---

## ⚡ 빠른 명령어 정리

| 항목 | 명령어 |
|------|--------|
| **EC2 접속** | `ssh -i your-key.pem ubuntu@YOUR_EC2_IP` |
| **프로젝트 경로** | `cd /home/ubuntu/bootrun-backend` |
| **로그 보기** | `docker-compose logs -f app` |
| **재시작** | `docker-compose restart` |
| **코드 업데이트** | `./update-deployment.sh` |
| **API 문서** | `http://YOUR_EC2_IP:8000/docs` |

---

## 🎯 성공 기준

✅ `http://YOUR_EC2_IP:8000/docs` 접속 가능  
✅ `/health` 엔드포인트가 `{"status": "healthy"}` 반환  
✅ 프론트엔드에서 API 요청 성공  
✅ CORS 오류 없음  

**이제 프론트엔드 협업 준비 완료! 🎉**

# AWS EC2 개발 서버 배포 가이드

BootRun API를 AWS EC2에 배포하여 프론트엔드와 협업하기 위한 완전한 단계별 가이드입니다.

---

## 사전 준비 사항

- EC2 접근 권한이 있는 **AWS 계정**
- **AWS Access Key** (이미 보유)
- **SSH 클라이언트** (Windows: PuTTY / WSL / Git Bash 등)
- **코드 저장용 Git 저장소** (GitHub, GitLab 등)

---

## 1단계: EC2 인스턴스 생성

### 1.1 AWS 콘솔 접속
1. [AWS 콘솔](https://console.aws.amazon.com/) 로그인  
2. **EC2 대시보드**로 이동  
3. **Launch Instance** 클릭  

### 1.2 인스턴스 설정

**기본 설정:**
- **이름**: `bootrun-api-dev`
- **운영체제(OS)**: Ubuntu Server 22.04 LTS (프리 티어 가능)
- **인스턴스 유형**:
  - 개발용 권장: `t2.medium` 또는 `t3.medium`
  - 최소 사양: `t2.small`
  - 더 높은 성능: `t2.medium` 이상

**키 페어:**
- 새로 생성 또는 기존 키 사용  
- **이름**: `bootrun-dev-key`  
- **타입**: RSA  
- **형식**: `.pem` (Mac/Linux), `.ppk` (PuTTY용)  
- **반드시 안전한 곳에 저장**

**네트워크 설정:**
- 새 보안 그룹 생성: `bootrun-dev-sg`
- **인바운드 규칙 (중요):**
  ```
  SSH          | TCP | 22   | Your IP        | SSH 접속용
  Custom TCP   | TCP | 8000 | 0.0.0.0/0      | API 접속용
  PostgreSQL   | TCP | 5432 | Your IP        | (선택) DB 접속용
  ```

**스토리지:**
- **크기**: 최소 20 GB  
- **유형**: gp3 (권장) 또는 gp2  

### 1.3 인스턴스 실행
- **Launch Instance** 클릭  
- “Running” 상태가 될 때까지 대기  
- **공인 IPv4 주소**를 확인 (예: `3.35.123.456`)

---

## 2단계: EC2 인스턴스 접속

### 옵션 A: Git Bash / WSL 사용 (Windows)
```bash
chmod 400 bootrun-dev-key.pem
ssh -i bootrun-dev-key.pem ubuntu@YOUR_EC2_PUBLIC_IP
```

### 옵션 B: PuTTY 사용 (Windows)
1. `.pem` 파일을 PuTTYgen으로 `.ppk`로 변환  
2. PuTTY 실행  
3. Host: `ubuntu@YOUR_EC2_PUBLIC_IP`  
4. Connection > SSH > Auth > Private key: `.ppk` 선택  
5. **Open** 클릭  

---

## 3단계: Git 저장소 푸시 (로컬에서 실행)

```bash
git init
git add .
git commit -m "Initial commit for EC2 deployment"
git remote add origin YOUR_GITHUB_REPO_URL
git branch -M main
git push -u origin main
```

---

## 4단계: EC2에 배포 (자동화)

### 4.1 배포 스크립트 업로드
```bash
curl -O https://raw.githubusercontent.com/YOUR_USERNAME/YOUR_REPO/main/deploy-ec2.sh
chmod +x deploy-ec2.sh
```

또는 수동 복사 후 저장 (`nano deploy-ec2.sh`)

### 4.2 배포 실행
```bash
./deploy-ec2.sh
```

자동으로 다음을 수행:
- Docker 및 Docker Compose 설치  
- 저장소 클론  
- 환경 변수 설정  
- 모든 서비스 실행  

### 4.3 환경 변수 설정
```bash
cd /home/ubuntu/bootrun-backend
nano .env
```

**필수 수정:**
```bash
python3 -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
AWS_ACCESS_KEY_ID=YOUR_ACTUAL_AWS_ACCESS_KEY
AWS_SECRET_ACCESS_KEY=YOUR_ACTUAL_AWS_SECRET_KEY
CORS_ORIGINS=http://localhost:3000,http://YOUR_EC2_PUBLIC_IP:3000
DATABASE_PASSWORD=랜덤비밀번호
REDIS_PASSWORD=랜덤비밀번호
```

---

## 5단계: 서비스 시작

```bash
cd /home/ubuntu/bootrun-backend
docker-compose up -d
docker-compose ps
docker-compose logs -f app
```

---

## 6단계: 데이터베이스 마이그레이션
```bash
docker-compose exec app bash
alembic upgrade head
exit
```

---

## 7단계: API 테스트
```bash
curl http://YOUR_EC2_PUBLIC_IP:8000/health
```

브라우저에서 `http://YOUR_EC2_PUBLIC_IP:8000/docs` 접속

---

## 8단계: 프론트엔드 공유
- Base URL: `http://YOUR_EC2_PUBLIC_IP:8000`
- Docs: `http://YOUR_EC2_PUBLIC_IP:8000/docs`
- Health: `http://YOUR_EC2_PUBLIC_IP:8000/health`

---

## 유용한 명령어

```bash
docker-compose ps
docker-compose logs -f app
docker-compose restart
docker-compose down
docker-compose up -d --build
docker-compose exec postgres psql -U bootrun_user -d bootrun_db
docker-compose exec redis redis-cli -a YOUR_REDIS_PASSWORD ping
```

---

## 코드 업데이트
```bash
cd /home/ubuntu/bootrun-backend
git pull
docker-compose up -d --build
docker-compose logs -f app
```

---

## 문제 해결
- 포트 8000 접근 불가: 보안 그룹 확인
- DB 연결 오류: `.env` 확인 및 postgres 로그 점검
- Redis 오류: `redis-cli ping` 테스트

---

## 보안 주의사항 ⚠️
이 설정은 개발용이며 운영 환경에는 적합하지 않습니다.

운영 환경에서는 다음을 추가로 구성해야 합니다:
- HTTPS / SSL
- 제한된 CORS 정책
- Nginx Reverse Proxy
- AWS Secrets Manager
- 오토스케일링 / 모니터링
- CloudWatch / 로드 밸런서

---

## 빠른 참조

**SSH 접속:** `ssh -i bootrun-dev-key.pem ubuntu@YOUR_EC2_PUBLIC_IP`  
**프로젝트 경로:** `/home/ubuntu/bootrun-backend`  
**API 문서:** `http://YOUR_EC2_PUBLIC_IP:8000/docs`  

---

## 문제 발생 시
1. 로그 확인: `docker-compose logs -f`
2. 환경 변수 확인: `cat .env`
3. 보안 그룹 규칙 점검
4. 서비스 상태 확인: `docker-compose ps`

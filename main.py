from fastapi import FastAPI

# FastAPI 애플리케이션 객체 생성
app = FastAPI()

# Health Check 엔드포인트 정의
@app.get("/health", tags=["System"])
def health_check():
    """
    애플리케이션의 상태를 확인합니다.
    """
    return {
        "status": "ok",
        "service": "bootrun-backend",
        # "database": db_status
    }
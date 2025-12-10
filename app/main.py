from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os
from app.core.redis import init_redis, close_redis
from app.core.config import settings
from contextlib import asynccontextmanager
from app.core.logging_config import configure_logging

logger = configure_logging()


# ============= FastAPI 앱 생성 =============

# 태그 메타데이터 정의
tags_metadata = [
    {
        "name": "인증",
        "description": "회원가입, 로그인, 소셜 로그인, 이메일 인증, 비밀번호 재설정 등 인증 관련 API",
    },
    {
        "name": "사용자",
        "description": "프로필 조회/수정, 비밀번호 변경, 이메일 변경, 회원 탈퇴, 알림 등 사용자 관련 API",
    },
    {
        "name": "강의",
        "description": "강의 목록 조회, 상세 조회, 챕터/강의 영상 조회 등 강의 관련 API",
    },
    {
        "name": "수강 등록 및 학습 진행",
        "description": "수강 등록, 내 강의실, 학습 진행 기록, 진행률 조회, 학습 통계 등 수강 관련 API",
    },
    {
        "name": "결제 및 환불",
        "description": "결제 생성/확인, 환불 요청, 결제 내역 조회 등 결제 관련 API",
    },
    {
        "name": "관리자 - 대시보드",
        "description": "전체 시스템 통계, 일별 통계, 매출 통계, 시스템 설정 등 관리자 대시보드 API",
    },
    {
        "name": "관리자 - 사용자 관리",
        "description": "사용자 목록 조회, 상세 조회, 활성화/비활성화, 학습 리포트 등 관리자 사용자 관리 API",
    },
    {
        "name": "관리자 - 강의 관리",
        "description": "강의 생성, 수정, 삭제, 챕터/강의 영상 관리 등 관리자 강의 관리 API",
    },
    {
        "name": "관리자 - 결제 및 환불 관리",
        "description": "결제 내역 조회, 환불 승인/거절 등 관리자 결제 관리 API",
    },
    {
        "name": "스토리지",
        "description": "Cloudflare R2 파일 스토리지 - 이미지/동영상/파일 업로드, 삭제, 목록 조회",
    },
    {
        "name": "⚠️ 테스트 전용",
        "description": "⚠️ 개발/테스트 전용 엔드포인트 - 프로덕션 배포 전 삭제 필요",
    },
]

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("=" * 60)
    logger.info(" BootRun API 서버 시작")
    logger.info("=" * 60)
    logger.info(f" 환경: {'개발' if settings.debug else '운영'}")
    logger.info(f" 문서: http://localhost:8000/docs")
    logger.info(f" ReDoc: http://localhost:8000/redoc")
    logger.info("=" * 60)
    await init_redis()
    yield
    await close_redis()
    logger.info("=" * 60)
    logger.info(" BootRun API 서버 종료")
    logger.info("=" * 60)
app = FastAPI(
    title="BootRun API",
    description="""
    BootRun - 온라인 교육 플랫폼 API

    BootRun은 온라인 강의 수강 및 관리를 위한 종합 교육 플랫폼입니다.

    """,
    version="1.0.0",
    openapi_tags=tags_metadata,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan,
    contact={
        "name": "BootRun 개발팀",
        "email": "support@bootrun.com",
    },
    license_info={
        "name": "MIT License",
    },
    swagger_ui_parameters={
        "persistAuthorization": True,
    }
)

# ============= CORS 미들웨어 설정 =============

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=settings.cors_allow_credentials,
    allow_methods=settings.cors_allow_methods.split(","),
    allow_headers=settings.cors_allow_headers.split(","),
)

from app.middleware.rate_limit import RateLimitMiddleware

app.add_middleware(
    RateLimitMiddleware,
    requests_per_minute=60,
    burst_size=10
)

# ============= 예외 핸들러 등록 =============

from app.exceptions.handlers import register_exception_handlers
register_exception_handlers(app)

# ============= 라우터 등록 =============

# 라우터 import
from app.routers.auth import router as auth_router
from app.routers.user import router as user_router
from app.routers.course import router as course_router
from app.routers.enrollment import router as enrollment_router
from app.routers.payment import router as payment_router

# 관리자 라우터 import
from app.routers.admin.dashboard import router as dashboard_router
from app.routers.admin.users import router as users_router
from app.routers.admin.courses import router as courses_router
from app.routers.admin.payments import router as payments_router
from app.routers.storage import router as storage_router

# ⚠️ 테스트 라우터 import (프로덕션 배포 전 삭제)
from app.routers._test_helpers import router as test_router


all_routers = [
    # 인증 및 사용자 API
    auth_router,
    user_router,
    # 일반 사용자 API
    course_router,
    enrollment_router,
    payment_router,
    # 관리자 API
    dashboard_router,
    users_router,
    courses_router,
    payments_router,
    # 스토리지 API
    storage_router,
    # ⚠️ 테스트 API (프로덕션 배포 전 삭제)
    test_router,
]

for router in all_routers:
    app.include_router(router)

logger.info(f"{len(all_routers)}개의 라우터가 등록되었습니다.")

# ============= 정적 파일 서빙 =============

# uploads 디렉토리가 없으면 생성
uploads_dir = "/app/uploads"
if not os.path.exists(uploads_dir):
    os.makedirs(uploads_dir)
    logger.info(f"'{uploads_dir}' 디렉토리를 생성했습니다.")

app.mount("/uploads", StaticFiles(directory=uploads_dir), name="uploads")
logger.info(f"정적 파일 서빙이 '/uploads' 경로에 마운트되었습니다.")

# ============= 기본 엔드포인트 =============

@app.get(
    "/",
    tags=["기본"],
    summary="루트 엔드포인트",
    description="API 상태를 확인합니다",
)
async def root():
    return {
        "message": "BootRun API 서버가 정상 작동 중입니다",
        "version": "1.0.0",
        "status": "healthy",
        "docs": "/docs",
        "redoc": "/redoc",
    }

@app.get("/health", tags=["기본"])
async def health_check():
    return {
        "status": "healthy",
        "service": "BootRun API",
        "version": "1.0.0",
    }

# ============= 메인 실행 =============

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=settings.debug, log_level="info")
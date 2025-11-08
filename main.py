from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os
from contextlib import asynccontextmanager

# 로거 설정
from core.logging_config import configure_logging

logger = configure_logging()

# 환경 변수에서 설정 읽기
IS_DEBUG = os.getenv('DEBUG', 'False').lower() in ('true', '1', 'yes')

# CORS 허용 origin 설정 (환경 변수에서 읽기)
ALLOWED_ORIGINS = os.getenv(
    'ALLOWED_ORIGINS',
    'http://localhost:3000,http://localhost:5173'  # 개발 환경 기본값
).split(',')

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
        "description": "수강 등록, 학습 진행 기록, 진행률 조회, 학습 통계 등 수강 관련 API",
    },
    {
        "name": "미션",
        "description": "미션 조회, 제출, 제출 내역 조회, 진행 현황 등 미션 관련 API",
    },
    {
        "name": "결제 및 환불",
        "description": "결제 생성/확인, 환불 요청, 결제 내역 조회 등 결제 관련 API",
    },
    {
        "name": "쿠폰",
        "description": "쿠폰 조회, 유효성 검증 등 쿠폰 관련 API",
    },
    {
        "name": "수료증",
        "description": "수료증 발급, 조회, PDF 생성, 진위 확인 등 수료증 관련 API",
    },
    {
        "name": "학습 Q&A",
        "description": "질문 작성, 답변 작성, 질문/답변 수정 및 삭제 등 학습 Q&A 관련 API",
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
        "name": "관리자 - 쿠폰 관리",
        "description": "쿠폰 생성, 수정, 삭제 등 관리자 쿠폰 관리 API",
    },
    {
        "name": "관리자 - 미션 관리",
        "description": "미션 생성, 수정, 삭제 등 관리자 미션 관리 API",
    },
]

# ============= Lifespan 이벤트 =============

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    애플리케이션 시작/종료 시 실행되는 이벤트
    """
    # 시작 시
    logger.info("=" * 60)
    logger.info("🚀 BootRun API 서버 시작")
    logger.info("=" * 60)
    logger.info(f"📝 환경: {'개발' if IS_DEBUG else '운영'}")
    logger.info(f"📚 문서: http://localhost:8000/docs")
    logger.info(f"📖 ReDoc: http://localhost:8000/redoc")
    logger.info("=" * 60)
    
    yield
    
    # 종료 시
    logger.info("=" * 60)
    logger.info("🛑 BootRun API 서버 종료")
    logger.info("=" * 60)


# FastAPI 앱 인스턴스 생성
app = FastAPI(
    title="BootRun API",
    description="""
    BootRun - 온라인 교육 플랫폼 API
    
    BootRun은 온라인 강의 수강 및 관리를 위한 종합 교육 플랫폼입니다.
    
    주요 기능
    
    사용자 기능
    * 인증 - 회원가입, 로그인, 소셜 로그인 (Google, Github)
    * 강의 관리 - 강의 검색, 필터링, 상세 조회
    * 수강 - 수강 등록, 학습 진행, 진도율 추적
    * 미션 - 중간/기말 미션 제출 및 자동 채점
    * 결제 - 강의 결제, 쿠폰 적용, 환불 요청
    * 수료증 - 수료증 발급 및 PDF 생성
    * Q&A - 학습 질문 및 답변
    
    관리자 기능
    * 대시보드 - 전체 통계, 매출 분석, 일별 현황
    * 사용자 관리 - 회원 조회, 활성화/비활성화, 학습 리포트
    * 강의 관리 - 강의 생성/수정, 챕터/영상 관리, 공개/비공개 설정
    * 결제 관리 - 결제 내역 조회, 환불 승인/거절
    * 쿠폰 관리 - 쿠폰 생성/수정, 사용 현황 조회
    * 미션 관리 - 미션 생성/수정, 문제 관리
    
    기술 스택
    - Framework: FastAPI 0.120.2+
    - Language: Python 3.11+
    - Validation: Pydantic v2
    - Database: PostgreSQL (계획)
    - Authentication: JWT Token

    인증 방식
    대부분의 API는 JWT 토큰 기반 인증을 사용합니다.
    
    1. 로그인 API로 토큰 발급
    2. Authorization 헤더에 `Bearer {token}` 형식으로 포함
    3. 토큰 만료 시 refresh API로 갱신
    
    에러 응답 형식
    모든 에러는 일관된 JSON 형식으로 반환됩니다:
    ```json
    {
        "error": "ERROR_CODE",
        "detail": "에러 상세 메시지",
        "path": "/auth/login"
    }
    ```
    
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
)


# ============= CORS 미들웨어 설정 =============

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization", "Accept", "Origin", "X-Requested-With"],
)

# ============= 예외 핸들러 등록 =============

from exceptions.handlers import register_exception_handlers

register_exception_handlers(app)


# ============= 라우터 등록 =============

# 라우터 import
from routers.auth import router as auth_router
from routers.user import router as user_router
from routers.course import router as course_router
from routers.enrollment import router as enrollment_router
from routers.mission import router as mission_router
from routers.payment import router as payment_router
from routers.coupon import router as coupon_router
from routers.certificate import router as certificate_router
from routers.question import router as question_router

# 관리자 라우터 import
from routers.admin.dashboard import router as dashboard_router
from routers.admin.users import router as users_router
from routers.admin.courses import router as courses_router
from routers.admin.payments import router as payments_router
from routers.admin.coupons import router as coupons_router
from routers.admin.missions import router as missions_router

# 모든 라우터 등록
all_routers = [
    # 인증 및 사용자 API
    auth_router,
    user_router,
    # 일반 사용자 API
    course_router,
    enrollment_router,
    mission_router,
    payment_router,
    coupon_router,
    certificate_router,
    question_router,
    # 관리자 API
    dashboard_router,
    users_router,
    courses_router,
    payments_router,
    coupons_router,
    missions_router,
]

for router in all_routers:
    app.include_router(router)

logger.info(f"{len(all_routers)}개의 라우터가 등록되었습니다.")


# ============= 기본 엔드포인트 =============

@app.get(
    "/",
    tags=["기본"],
    summary="루트 엔드포인트",
    description="API 상태를 확인합니다",
)
async def root():
    """
    # API 상태 확인
    
    API가 정상적으로 동작하는지 확인합니다.
    """
    return {
        "message": "BootRun API 서버가 정상 작동 중입니다 🚀",
        "version": "1.0.0",
        "status": "healthy",
        "docs": "/docs",
        "redoc": "/redoc",
    }


@app.get(
    "/health",
    tags=["기본"],
    summary="헬스 체크",
    description="서버 상태를 확인합니다 (모니터링용)",
)
async def health_check():
    return {
        "status": "healthy",
        "service": "BootRun API",
        "version": "1.0.0",
    }



# ============= 메인 실행 =============

if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=IS_DEBUG,  # 개발 환경에서만 자동 재시작
        log_level="info",
        log_config=None
    )
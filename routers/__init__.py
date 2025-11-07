"""
API Routers Package
모든 API 라우터를 중앙에서 관리
"""

# 인증 및 사용자 API
from .auth import router as auth_router
from .user import router as user_router

# 일반 사용자 API
from .course import router as course_router
from .enrollment import router as enrollment_router
from .mission import router as mission_router
from .payment import router as payment_router
from .certificate import router as certificate_router
from .question import router as question_router
from .coupon import router as coupon_router

# 관리자 API (admin 서브패키지에서 import)
from .admin.dashboard import router as dashboard_router
from .admin.users import router as users_router
from .admin.courses import router as courses_router
from .admin.payments import router as payments_router
from .admin.coupons import router as coupons_router
from .admin.missions import router as missions_router

# 모든 라우터 리스트 (FastAPI 앱에 등록할 때 사용)
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

__all__ = [
    # 인증 및 사용자 API
    "auth_router",
    "user_router",
    # 일반 사용자 API
    "course_router",
    "enrollment_router",
    "mission_router",
    "payment_router",
    "certificate_router",
    "question_router",
    "coupon_router",
    # 관리자 API
    "dashboard_router",
    "users_router",
    "courses_router",
    "payments_router",
    "coupons_router",
    "missions_router",
    # 전체 라우터 리스트
    "all_routers",
]
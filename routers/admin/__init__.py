"""
Admin Routers Package
관리자 전용 API 라우터
"""

from .dashboard import router as dashboard_router
from .users import router as users_router
from .courses import router as courses_router
from .payments import router as payments_router
from .coupons import router as coupons_router
from .missions import router as missions_router

__all__ = [
    "dashboard_router",
    "users_router",
    "courses_router",
    "payments_router",
    "coupons_router",
    "missions_router",
]
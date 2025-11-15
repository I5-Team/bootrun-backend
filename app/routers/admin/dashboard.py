from fastapi import APIRouter, Depends
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.admin import (
    DashboardStats, DailyStats, RevenueStats,
    CourseStats, CategoryStats, StatsQueryParams,
    CourseStatsQueryParams, SystemSettings
)
from app.schemas.common import SuccessResponse
from app.exceptions.responses import ADMIN_DASHBOARD_RESPONSES
from app.core.dependencies import get_current_admin, get_db
from app.models.user import User
from app.services.admin_dashboard_service import AdminDashboardService

router = APIRouter(prefix="/admin/dashboard", tags=["관리자 - 대시보드"])

@router.get(
    "/stats",
    response_model=SuccessResponse[DashboardStats],
    summary="대시보드 통계",
    description="관리자 대시보드의 주요 통계 데이터를 조회합니다.",
    responses={
        200: {"description": "통계 조회 성공"},
        **ADMIN_DASHBOARD_RESPONSES
    }
)
async def get_dashboard_stats(
    current_admin: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db)
):
    stats = await AdminDashboardService.get_stats(db)
    return SuccessResponse(data=stats)

@router.get(
    "/daily-stats",
    response_model=SuccessResponse[List[DailyStats]],
    summary="일별 통계",
    description="일별 접속자, 조회수, 매출 통계를 조회합니다.",
    responses={
        200: {"description": "일별 통계 조회 성공"},
        **ADMIN_DASHBOARD_RESPONSES
    }
)
async def get_daily_stats(
    params: StatsQueryParams = Depends(),
    current_admin: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db)
):
    stats = await AdminDashboardService.get_daily_stats(
        db,
        start_date=params.start_date,
        end_date=params.end_date
    )
    return SuccessResponse(data=stats)

@router.get(
    "/revenue-stats",
    response_model=SuccessResponse[List[RevenueStats]],
    summary="매출 통계",
    description="일별 매출, 환불, 순수익 통계를 조회합니다.",
    responses={
        200: {"description": "매출 통계 조회 성공"},
        **ADMIN_DASHBOARD_RESPONSES
    }
)
async def get_revenue_stats(
    params: StatsQueryParams = Depends(),
    current_admin: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db)
):
    stats = await AdminDashboardService.get_revenue_stats(
        db,
        start_date=params.start_date,
        end_date=params.end_date
    )
    return SuccessResponse(data=stats)

@router.get(
    "/course-stats",
    response_model=SuccessResponse[List[CourseStats]],
    summary="강의별 통계",
    description="강의별 수강 현황, 진행률, 완료율 통계를 조회합니다.",
    responses={
        200: {"description": "강의별 통계 조회 성공"},
        **ADMIN_DASHBOARD_RESPONSES
    }
)
async def get_course_stats(
    params: CourseStatsQueryParams = Depends(),
    current_admin: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db)
):
    stats = await AdminDashboardService.get_course_stats(
        db,
        category_type=params.category_type,
        start_date=params.start_date,
        end_date=params.end_date
    )
    return SuccessResponse(data=stats)

@router.get(
    "/category-stats",
    response_model=SuccessResponse[List[CategoryStats]],
    summary="카테고리별 통계",
    description="카테고리별 강의 수, 수강 현황, 매출 통계를 조회합니다.",
    responses={
        200: {"description": "카테고리별 통계 조회 성공"},
        **ADMIN_DASHBOARD_RESPONSES
    }
)
async def get_category_stats(
    current_admin: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db)
):
    stats = await AdminDashboardService.get_category_stats(db)
    return SuccessResponse(data=stats)

@router.get(
    "/settings",
    response_model=SuccessResponse[SystemSettings],
    summary="시스템 설정 조회",
    description="시스템 설정 정보를 조회합니다.",
    responses={
        200: {"description": "시스템 설정 조회 성공"},
        **ADMIN_DASHBOARD_RESPONSES
    }
)
async def get_system_settings(
    current_admin: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db)
):
    pass

@router.patch(
    "/settings",
    response_model=SuccessResponse[SystemSettings],
    summary="시스템 설정 수정",
    description="시스템 설정을 수정합니다.",
    responses={
        200: {"description": "시스템 설정 수정 완료"},
        **ADMIN_DASHBOARD_RESPONSES
    }
)
async def update_system_settings(
    data: SystemSettings,
    current_admin: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db)
):
    pass
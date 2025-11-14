from fastapi import APIRouter, Depends, Query
from typing import List, Optional
from datetime import date
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.admin import (
    DashboardStats, DailyStats, RevenueStats,
    CourseStats, CategoryStats, SystemSettings
)
from app.schemas.common import SuccessResponse
from app.schemas.course import CategoryType
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
    """
    대시보드 기본 통계 조회
    - 전체 사용자 수
    - 전체 강의 수
    - 전체 수강 등록 수
    - 활성 수강 수 (만료되지 않은)
    - 전체 매출
    - 대기 중인 환불 건수
    - 오늘 방문자 수
    - 오늘 조회수
    - 오늘 매출
    """
    service = AdminDashboardService(db)
    stats = await service.get_dashboard_stats()
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
    start_date: Optional[date] = Query(None, description="시작 날짜 (YYYY-MM-DD)"),
    end_date: Optional[date] = Query(None, description="종료 날짜 (YYYY-MM-DD)"),
    days: int = Query(30, ge=1, le=365, description="조회 기간 (일 수, 기본값: 30)"),
    current_admin: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db)
):
    """
    일별 통계 조회
    - date: 날짜
    - visitors: 방문자 수 (고유 IP 기준)
    - views: 조회수 (총 접속 수)
    - revenue: 매출
    - enrollments: 수강 등록 수
    - new_users: 신규 사용자 수

    조회 기간 지정 방법:
    1. start_date와 end_date를 모두 지정하면 해당 기간 조회
    2. 지정하지 않으면 days 파라미터만큼 과거 데이터 조회
    """
    service = AdminDashboardService(db)
    stats = await service.get_daily_stats(
        start_date=start_date,
        end_date=end_date,
        days=days
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
    start_date: Optional[date] = Query(None, description="시작 날짜 (YYYY-MM-DD)"),
    end_date: Optional[date] = Query(None, description="종료 날짜 (YYYY-MM-DD)"),
    days: int = Query(30, ge=1, le=365, description="조회 기간 (일 수, 기본값: 30)"),
    current_admin: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db)
):
    """
    매출 통계 조회
    - date: 날짜
    - revenue: 매출
    - payment_count: 결제 건수
    - refund_amount: 환불 금액
    - refund_count: 환불 건수
    - net_revenue: 순수익 (매출 - 환불금액)

    조회 기간 지정 방법:
    1. start_date와 end_date를 모두 지정하면 해당 기간 조회
    2. 지정하지 않으면 days 파라미터만큼 과거 데이터 조회
    """
    service = AdminDashboardService(db)
    stats = await service.get_revenue_stats(
        start_date=start_date,
        end_date=end_date,
        days=days
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
    category_type: Optional[CategoryType] = Query(None, description="카테고리 필터 (frontend, backend, data_analysis, ai, design, other)"),
    start_date: Optional[date] = Query(None, description="시작 날짜 (YYYY-MM-DD)"),
    end_date: Optional[date] = Query(None, description="종료 날짜 (YYYY-MM-DD)"),
    current_admin: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db)
):
    """
    강의별 통계 조회
    - course_id: 강의 ID
    - course_title: 강의명
    - category_name: 카테고리명
    - total_enrollments: 전체 수강 등록 수
    - active_enrollments: 활성 수강 수 (만료되지 않은)
    - avg_progress: 평균 진행률
    - completion_count: 완료 건수 (100% 진행률)
    - completion_rate: 완료율 (%)
    - total_revenue: 매출

    선택 파라미터:
    - category_type: 특정 카테고리만 조회 (생략 시 전체 강의 조회)
    """
    service = AdminDashboardService(db)
    stats = await service.get_course_stats(
        category_type=category_type,
        start_date=start_date,
        end_date=end_date
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
    """
    카테고리별 통계 조회
    - category_id: 카테고리 ID (frontend, backend, data_analysis, ai, design, other)
    - category_name: 카테고리명
    - course_count: 강의 수 (공개된 강의만)
    - total_enrollments: 전체 수강 등록 수
    - total_revenue: 전체 매출
    - avg_completion_rate: 평균 완료율 (%)
    """
    service = AdminDashboardService(db)
    stats = await service.get_category_stats()
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
    """
    시스템 설정 조회
    - site_name: 사이트 명
    - course_price: 기본 강의 가격
    - enrollment_period_years: 수강 기한 (년)
    - refund_period_days: 환불 가능 기간 (일)
    - refund_progress_limit: 환불 가능 진행률 (%)
    - passing_score_rate: 합격 점수 (%)
    """
    service = AdminDashboardService(db)
    settings = await service.get_system_settings()
    return SuccessResponse(data=settings)

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
    """
    시스템 설정 수정

    수정 가능한 설정:
    - site_name: 사이트 명
    - course_price: 기본 강의 가격
    - enrollment_period_years: 수강 기한 (년)
    - refund_period_days: 환불 가능 기간 (일)
    - refund_progress_limit: 환불 가능 진행률 (%)
    - passing_score_rate: 합격 점수 (%)
    """
    service = AdminDashboardService(db)
    updated_settings = await service.update_system_settings(data)
    return SuccessResponse(data=updated_settings)
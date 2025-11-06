"""
관리자 대시보드 API 라우터
전체 시스템 통계, 일별 통계, 매출 통계 등을 조회합니다.
"""

from fastapi import APIRouter, Depends
from typing import List
from schemas.admin import (
    DashboardStats, DailyStats, RevenueStats,
    CourseStats, CategoryStats, StatsQueryParams,
    CourseStatsQueryParams, SystemSettings
)
from exceptions import ADMIN_DASHBOARD_RESPONSES

router = APIRouter(prefix="/admin/dashboard", tags=["관리자 - 대시보드"])


@router.get(
    "/stats",
    response_model=DashboardStats,
    summary="대시보드 통계",
    description="관리자 대시보드의 주요 통계 데이터를 조회합니다.",
    responses={
        200: {"description": "통계 조회 성공"},
        **ADMIN_DASHBOARD_RESPONSES
    }
)
async def get_dashboard_stats():
    """
    # 대시보드 통계 API
    
    전체 시스템의 주요 지표를 조회합니다.
    
    ## 응답
    - 200: 통계 조회 성공
    - 401: 인증되지 않은 사용자
    - 403: 관리자 권한 필요
    
    ## 반환 정보
    - total_users: 전체 사용자 수
    - total_courses: 전체 강의 수
    - total_enrollments: 전체 수강 등록 수
    - active_enrollments: 활성 수강 등록 수
    - total_revenue: 총 매출
    - pending_refunds: 대기 중인 환불 수
    - today_visitors: 오늘 방문자 수
    - today_views: 오늘 조회수
    - today_revenue: 오늘 매출
    """
    pass


@router.get(
    "/daily-stats",
    response_model=List[DailyStats],
    summary="일별 통계",
    description="일별 접속자, 조회수, 매출 통계를 조회합니다.",
    responses={
        200: {"description": "일별 통계 조회 성공"},
        **ADMIN_DASHBOARD_RESPONSES
    }
)
async def get_daily_stats(params: StatsQueryParams = Depends()):
    """
    # 일별 통계 API
    
    일별 통계 데이터를 조회합니다.
    
    ## 쿼리 파라미터
    - period: 조회 기간 (day/week/month/year)
    - start_date: 시작 날짜 (선택)
    - end_date: 종료 날짜 (선택)
    
    ## 응답
    - 200: 통계 조회 성공
    - 401: 인증되지 않은 사용자
    - 403: 관리자 권한 필요
    
    ## 반환 정보
    - date: 날짜
    - visitors: 방문자 수 (동일 IP 1회)
    - views: 조회수 (동일 IP 다수 가능)
    - revenue: 매출
    - enrollments: 수강 등록 수
    - new_users: 신규 가입자 수
    """
    pass


@router.get(
    "/revenue-stats",
    response_model=List[RevenueStats],
    summary="매출 통계",
    description="일별 매출, 환불, 순수익 통계를 조회합니다.",
    responses={
        200: {"description": "매출 통계 조회 성공"},
        **ADMIN_DASHBOARD_RESPONSES
    }
)
async def get_revenue_stats(params: StatsQueryParams = Depends()):
    """
    # 매출 통계 API
    
    매출 관련 통계를 조회합니다.
    
    ## 쿼리 파라미터
    - period: 조회 기간 (day/week/month/year)
    - start_date: 시작 날짜 (선택)
    - end_date: 종료 날짜 (선택)
    
    ## 응답
    - 200: 통계 조회 성공
    - 401: 인증되지 않은 사용자
    - 403: 관리자 권한 필요
    
    ## 반환 정보
    - date: 날짜
    - revenue: 매출
    - payment_count: 결제 건수
    - refund_amount: 환불 금액
    - refund_count: 환불 건수
    - net_revenue: 순수익 (매출 - 환불)
    """
    pass


@router.get(
    "/course-stats",
    response_model=List[CourseStats],
    summary="강의별 통계",
    description="강의별 수강 현황, 진행률, 완료율 통계를 조회합니다.",
    responses={
        200: {"description": "강의별 통계 조회 성공"},
        **ADMIN_DASHBOARD_RESPONSES
    }
)
async def get_course_stats(params: CourseStatsQueryParams = Depends()):
    """
    # 강의별 통계 API
    
    강의별 통계 데이터를 조회합니다.
    
    ## 쿼리 파라미터
    - category_id: 카테고리 ID 필터 (선택)
    - start_date: 시작 날짜 (선택)
    - end_date: 종료 날짜 (선택)
    
    ## 응답
    - 200: 통계 조회 성공
    - 401: 인증되지 않은 사용자
    - 403: 관리자 권한 필요
    
    ## 반환 정보
    - course_id: 강의 ID
    - course_title: 강의명
    - category_name: 카테고리명
    - total_enrollments: 총 수강 등록 수
    - active_enrollments: 활성 수강 수
    - avg_progress: 평균 진행률
    - completion_count: 완료 수
    - completion_rate: 완료율
    - total_revenue: 총 매출
    """
    pass


@router.get(
    "/category-stats",
    response_model=List[CategoryStats],
    summary="카테고리별 통계",
    description="카테고리별 강의 수, 수강 현황, 매출 통계를 조회합니다.",
    responses={
        200: {"description": "카테고리별 통계 조회 성공"},
        **ADMIN_DASHBOARD_RESPONSES
    }
)
async def get_category_stats():
    """
    # 카테고리별 통계 API
    
    카테고리별 통계를 조회합니다.
    
    ## 응답
    - 200: 통계 조회 성공
    - 401: 인증되지 않은 사용자
    - 403: 관리자 권한 필요
    
    ## 반환 정보
    - category_id: 카테고리 ID
    - category_name: 카테고리명
    - course_count: 강의 수
    - total_enrollments: 총 수강 등록 수
    - total_revenue: 총 매출
    - avg_completion_rate: 평균 완료율
    """
    pass


@router.get(
    "/settings",
    response_model=SystemSettings,
    summary="시스템 설정 조회",
    description="시스템 설정 정보를 조회합니다.",
    responses={
        200: {"description": "시스템 설정 조회 성공"},
        **ADMIN_DASHBOARD_RESPONSES
    }
)
async def get_system_settings():
    """
    # 시스템 설정 조회 API
    
    시스템 설정을 조회합니다.
    
    ## 응답
    - 200: 설정 조회 성공
    - 401: 인증되지 않은 사용자
    - 403: 관리자 권한 필요
    
    ## 반환 정보
    - site_name: 사이트명
    - course_price: 기본 강의 가격
    - enrollment_period_years: 수강 기간(년)
    - refund_period_days: 환불 가능 기간(일)
    - refund_progress_limit: 환불 가능 진도율 제한(%)
    - passing_score_rate: 미션 통과 기준 점수(%)
    """
    pass


@router.patch(
    "/settings",
    response_model=SystemSettings,
    summary="시스템 설정 수정",
    description="시스템 설정을 수정합니다.",
    responses={
        200: {"description": "시스템 설정 수정 완료"},
        **ADMIN_DASHBOARD_RESPONSES
    }
)
async def update_system_settings(data: SystemSettings):
    """
    # 시스템 설정 수정 API
    
    시스템 설정을 수정합니다.
    
    ## 요청 본문
    - site_name: 사이트명
    - course_price: 기본 강의 가격
    - enrollment_period_years: 수강 기간
    - refund_period_days: 환불 가능 기간
    - refund_progress_limit: 환불 가능 진도율
    - passing_score_rate: 통과 기준 점수
    
    ## 응답
    - 200: 설정 수정 성공
    - 401: 인증되지 않은 사용자
    - 403: 관리자 권한 필요
    - 422: 입력값 유효성 검사 실패
    """
    pass
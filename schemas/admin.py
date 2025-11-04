from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime, date
from enum import Enum


# Enums
class StatsPeriod(str, Enum):
    DAY = "day"
    WEEK = "week"
    MONTH = "month"
    YEAR = "year"


# ============= 대시보드 통계 =============
class DashboardStats(BaseModel):
    total_users: int
    total_courses: int
    total_enrollments: int
    active_enrollments: int
    total_revenue: int
    pending_refunds: int
    today_visitors: int
    today_views: int
    today_revenue: int


class DailyStats(BaseModel):
    date: date
    visitors: int  # 고유 IP 기준
    views: int  # 총 접속 수
    revenue: int
    enrollments: int
    new_users: int


class RevenueStats(BaseModel):
    date: date
    revenue: int
    payment_count: int
    refund_amount: int
    refund_count: int
    net_revenue: int


class CourseStats(BaseModel):
    course_id: int
    course_title: str
    category_name: str
    total_enrollments: int
    active_enrollments: int
    avg_progress: float
    completion_count: int
    completion_rate: float
    total_revenue: int


class CategoryStats(BaseModel):
    category_id: int
    category_name: str
    course_count: int
    total_enrollments: int
    total_revenue: int
    avg_completion_rate: float


# ============= 사용자 관리 =============
class UserManagementListParams(BaseModel):
    role: Optional[str] = None
    is_active: Optional[bool] = None
    keyword: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=20, ge=1, le=100)


class UserManagementResponse(BaseModel):
    id: int
    email: str
    name: str
    role: str
    is_active: bool
    total_enrollments: int
    total_payments: int
    total_spent: int
    created_at: datetime
    last_login: Optional[datetime]
    
    class Config:
        from_attributes = True


class UserDetailForAdmin(BaseModel):
    id: int
    email: str
    name: str
    gender: str
    birth_date: date
    role: str
    is_active: bool
    provider: str
    created_at: datetime
    last_login: Optional[datetime]
    # 학습 정보
    total_study_time: int
    total_enrollments: int
    active_enrollments: int
    completed_courses: int
    avg_progress_rate: float
    # 결제 정보
    total_payments: int
    total_spent: int
    total_refunds: int
    # 활동 정보
    total_questions: int
    total_comments: int
    enrollments: List[dict] = []
    
    class Config:
        from_attributes = True


# ============= 사용자별 학습 기록 (선택) =============
class UserLearningRecord(BaseModel):
    user_id: int
    user_name: str
    date: date
    study_time: int  # 분 단위
    watched_lectures: int
    completed_lectures: int
    login_count: int


class UserAttendanceRecord(BaseModel):
    date: date
    is_present: bool  # 출석 여부
    study_time: int
    lectures_watched: int


class UserProgressDetail(BaseModel):
    course_id: int
    course_title: str
    enrolled_at: datetime
    expires_at: datetime
    progress_rate: float
    total_lectures: int
    completed_lectures: int
    total_study_time: int
    last_watched_at: Optional[datetime]


class UserLearningReport(BaseModel):
    user_id: int
    user_name: str
    report_period: str  # 예: "2025-01"
    total_study_time: int
    attendance_rate: float
    avg_progress_rate: float
    courses: List[UserProgressDetail] = []
    attendance: List[UserAttendanceRecord] = []


# ============= 강의 관리 =============
class CourseManagementListParams(BaseModel):
    category_id: Optional[int] = None
    difficulty: Optional[str] = None
    is_published: Optional[bool] = None
    keyword: Optional[str] = None
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=20, ge=1, le=100)


class CourseManagementResponse(BaseModel):
    id: int
    category_name: str
    title: str
    instructor_name: str
    difficulty: str
    is_published: bool
    enrollment_count: int
    total_revenue: int
    avg_progress: float
    completion_rate: float
    created_at: datetime
    updated_at: datetime


# ============= 결제 관리 =============
class PaymentManagementListParams(BaseModel):
    status: Optional[str] = None
    payment_method: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    keyword: Optional[str] = None
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=20, ge=1, le=100)


class PaymentManagementResponse(BaseModel):
    id: int
    transaction_id: str
    user_id: int
    user_name: str
    user_email: str
    course_id: int
    course_title: str
    amount: int
    discount_amount: int
    final_amount: int
    payment_method: str
    status: str
    paid_at: Optional[datetime]
    created_at: datetime
    
    class Config:
        from_attributes = True


# ============= 환불 관리 =============
class RefundManagementListParams(BaseModel):
    status: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    keyword: Optional[str] = None
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=20, ge=1, le=100)


class RefundManagementResponse(BaseModel):
    id: int
    payment_id: int
    transaction_id: str
    user_id: int
    user_name: str
    course_title: str
    amount: int
    reason: str
    status: str
    payment_date: datetime
    progress_rate: float
    requested_at: datetime
    processed_at: Optional[datetime]
    admin_note: Optional[str]


# ============= 통계 조회 파라미터 =============
class StatsQueryParams(BaseModel):
    period: StatsPeriod = StatsPeriod.DAY
    start_date: Optional[date] = None
    end_date: Optional[date] = None


class CourseStatsQueryParams(BaseModel):
    category_id: Optional[int] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None


# ============= 시스템 설정 =============
class SystemSettings(BaseModel):
    site_name: str = "BootRun"
    course_price: int = 50000
    enrollment_period_years: int = 2
    refund_period_days: int = 7
    refund_progress_limit: float = 10.0
    passing_score_rate: float = 60.0


# admin.py 맨 아래

class UserManagementPaginatedResponse(BaseModel):
    """사용자 관리 목록 페이지네이션"""
    total: int
    page: int
    page_size: int
    total_pages: int
    items: List[UserManagementResponse]

class CourseManagementPaginatedResponse(BaseModel):
    """강의 관리 목록 페이지네이션"""
    total: int
    page: int
    page_size: int
    total_pages: int
    items: List[CourseManagementResponse]

class PaymentManagementPaginatedResponse(BaseModel):
    """결제 관리 목록 페이지네이션"""
    total: int
    page: int
    page_size: int
    total_pages: int
    items: List[PaymentManagementResponse]

class RefundManagementPaginatedResponse(BaseModel):
    """환불 관리 목록 페이지네이션"""
    total: int
    page: int
    page_size: int
    total_pages: int
    items: List[RefundManagementResponse]
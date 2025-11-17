from pydantic import BaseModel, Field, field_serializer
from typing import Optional, List, Any
from datetime import datetime, date, timezone, timedelta
from enum import Enum

from app.schemas.course import CategoryType, Difficulty

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
    role: Optional[str] = Field(
        None,
        description="역할로 필터링 (student, admin)", 
        example="student"
    )
    is_active: Optional[bool] = Field(
        None,
        description="활성화 상태로 필터링", 
        example=True
    )
    keyword: Optional[str] = Field(
        None,
        description="검색 키워드 (이름, 이메일)", 
        example="홍길동"
    )
    start_date: Optional[datetime] = Field(
        None,
        description="가입 시작일", 
        example="2025-01-01T00:00:00"
    )
    end_date: Optional[datetime] = Field(
        None,
        description="가입 종료일", 
        example="2025-12-31T23:59:59"
    )
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=20, ge=1, le=100)

class UserManagementResponse(BaseModel):
    id: int
    email: str
    nickname: str
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
    nickname: str
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
    enrollments: List[dict[str, Any]] = []
    
    class Config:
        from_attributes = True

# ============= 사용자별 학습 기록 (선택) =============
class UserLearningRecord(BaseModel):
    user_id: int
    user_nickname: str
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
    user_nickname: str
    report_period: str  # 예: "2025-01"
    total_study_time: int
    attendance_rate: float
    avg_progress_rate: float
    courses: List[UserProgressDetail] = []
    attendance: List[UserAttendanceRecord] = []

# ============= 강의 관리 =============
class CourseManagementListParams(BaseModel):
    category_type: Optional[CategoryType] = Field(
        None,
        description="카테고리 타입으로 필터링 (frontend, backend, data_analysis, ai, design, other)",
        example="backend"
    )
    difficulty: Optional[Difficulty] = Field(
        None,
        description="난이도로 필터링 (beginner, intermediate, advanced)",
        example="beginner"
    )
    is_published: Optional[bool] = Field(
        None,
        description="공개 상태로 필터링",
        example=True
    )
    keyword: Optional[str] = Field(
        None,
        description="검색 키워드 (강의명, 강사명)",
        example="FastAPI"
    )
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=20, ge=1, le=100)

class CourseManagementResponse(BaseModel):
    id: int
    title: str
    category_name: str
    instructor_name: str
    difficulty: str
    price: int
    total_duration: int
    chapter_count: int
    enrollment_count: int
    is_published: bool
    created_at: datetime
    total_revenue: int
    avg_progress: float
    completion_rate: float

# ============= 결제 관리 =============
class PaymentManagementListParams(BaseModel):
    status: Optional[str] = Field(
        None,
        description="결제 상태로 필터링", 
        example="completed"
    )
    payment_method: Optional[str] = Field(
        None,
        description="결제 방식으로 필터링", 
        example="card"
    )
    start_date: Optional[datetime] = Field(
        None,
        description="결제 시작일", 
        example="2025-01-01T00:00:00"
    )
    end_date: Optional[datetime] = Field(
        None,
        description="결제 종료일", 
        example="2025-12-31T23:59:59"
    )
    keyword: Optional[str] = Field(
        None,
        description="검색 키워드 (사용자명, 강의명)", 
        example="홍길동"
    )
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=20, ge=1, le=100)

class PaymentManagementResponse(BaseModel):
    id: int
    transaction_id: str
    user_id: int
    user_nickname: str
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

    @field_serializer('paid_at', 'created_at')
    def serialize_datetime(self, value: Optional[datetime]) -> Optional[str]:
        if not value:
            return None
        kst = timezone(timedelta(hours=9))
        utc = value.replace(tzinfo=timezone.utc) if value.tzinfo is None else value
        return utc.astimezone(kst).isoformat()

# ============= 환불 관리 =============
class RefundManagementListParams(BaseModel):
    status: Optional[str] = Field(
        None,
        description="환불 상태로 필터링", 
        example="pending"
    )
    start_date: Optional[datetime] = Field(
        None,
        description="요청 시작일", 
        example="2025-01-01T00:00:00"
    )
    end_date: Optional[datetime] = Field(
        None,
        description="요청 종료일", 
        example="2025-12-31T23:59:59"
    )
    keyword: Optional[str] = Field(
        None,
        description="검색 키워드", 
        example="홍길동"
    )
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=20, ge=1, le=100)

class RefundManagementResponse(BaseModel):
    id: int
    payment_id: int
    transaction_id: str
    user_id: int
    user_nickname: str
    course_title: str
    amount: int
    reason: str
    status: str
    payment_date: datetime
    progress_rate: float
    requested_at: datetime
    processed_at: Optional[datetime]
    admin_note: Optional[str]

    @field_serializer('payment_date', 'requested_at', 'processed_at')
    def serialize_datetime(self, value: Optional[datetime]) -> Optional[str]:
        if not value:
            return None
        kst = timezone(timedelta(hours=9))
        utc = value.replace(tzinfo=timezone.utc) if value.tzinfo is None else value
        return utc.astimezone(kst).isoformat()

# ============= 통계 조회 파라미터 =============
class StatsQueryParams(BaseModel):
    period: StatsPeriod = Field(
        default=StatsPeriod.DAY,
        description="통계 기간 (day, week, month, year)", 
        example="day"
    )
    start_date: Optional[date] = Field(
        None,
        description="시작 날짜", 
        example="2025-01-01"
    )
    end_date: Optional[date] = Field(
        None,
        description="종료 날짜", 
        example="2025-12-31"
    )

class CourseStatsQueryParams(BaseModel):
    category_type: Optional[CategoryType] = Field(
        None,
        description="카테고리 타입으로 필터링 (frontend, backend, data_analysis, ai, design, other)",
        example="backend"
    )
    start_date: Optional[date] = Field(
        None,
        description="시작 날짜",
        example="2025-01-01"
    )
    end_date: Optional[date] = Field(
        None,
        description="종료 날짜",
        example="2025-12-31"
    )

# ============= 시스템 설정 =============
class SystemSettings(BaseModel):
    site_name: str = "BootRun"
    course_price: int = 50000
    enrollment_period_years: int = 2
    refund_period_days: int = 7
    refund_progress_limit: float = 10.0
    passing_score_rate: float = 60.0

class UserManagementPaginatedResponse(BaseModel):
    total: int
    page: int
    page_size: int
    total_pages: int
    items: List[UserManagementResponse]

class CourseManagementPaginatedResponse(BaseModel):
    total: int
    page: int
    page_size: int
    total_pages: int
    items: List[CourseManagementResponse]

class PaymentManagementPaginatedResponse(BaseModel):
    total: int
    page: int
    page_size: int
    total_pages: int
    items: List[PaymentManagementResponse]

class RefundManagementPaginatedResponse(BaseModel):
    total: int
    page: int
    page_size: int
    total_pages: int
    items: List[RefundManagementResponse]
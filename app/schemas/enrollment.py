from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

# ============= 수강 등록 =============
class EnrollmentCreate(BaseModel):
    course_id: int = Field(
        ..., 
        ge=1,
        description="수강 신청할 강의 ID", 
        example=1
    )

class EnrollmentResponse(BaseModel):
    id: int
    user_id: int
    course_id: int
    course_title: str
    course_thumbnail: str
    category_name: str
    difficulty: str
    enrolled_at: datetime
    expires_at: datetime
    is_active: bool
    progress_rate: float = 0.0
    days_until_expiry: int
    total_lectures: int = 0
    completed_lectures: int = 0
    
    class Config:
        from_attributes = True

class MyEnrollmentListParams(BaseModel):
    category_id: Optional[int] = Field(
        None,
        description="카테고리 ID로 필터링", 
        example=1
    )
    difficulty: Optional[str] = Field(
        None,
        description="난이도로 필터링 (beginner, intermediate, advanced)", 
        example="beginner"
    )
    is_active: Optional[bool] = Field(
        True,
        description="활성화 상태로 필터링", 
        example=True
    )
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=20, ge=1, le=100)

class EnrollmentDetailResponse(BaseModel):
    id: int
    user_id: int
    course_id: int
    course_title: str
    course_description: str
    course_thumbnail: str
    instructor_name: str
    category_name: str
    difficulty: str
    enrolled_at: datetime
    expires_at: datetime
    is_active: bool
    progress_rate: float
    days_until_expiry: int
    total_duration: int  # 전체 강의 시간
    watched_duration: int  # 시청한 시간
    total_lectures: int
    completed_lectures: int
    # 미션 정보
    total_missions: int = 0
    completed_missions: int = 0
    
    class Config:
        from_attributes = True

# ============= 학습 진행 =============
class ProgressCreate(BaseModel):
    lecture_id: int = Field(
        ..., 
        ge=1,
        description="시청 중인 강의 ID", 
        example=1
    )
    watched_seconds: int = Field(
        ..., 
        ge=0,
        description="총 시청 시간 (초)", 
        example=300
    )
    last_position: int = Field(
        ..., 
        ge=0,
        description="마지막 시청 위치 (초)", 
        example=295
    )
    is_completed: bool = Field(
        default=False,
        description="강의 완료 여부", 
        example=False
    )

class ProgressUpdate(BaseModel):
    watched_seconds: int = Field(
        ..., 
        ge=0,
        description="총 시청 시간 (초)", 
        example=450
    )
    last_position: int = Field(
        ..., 
        ge=0,
        description="마지막 시청 위치 (초)", 
        example=445
    )
    is_completed: bool = Field(
        default=False,
        description="강의 완료 여부", 
        example=True
    )

class ProgressResponse(BaseModel):
    id: int
    user_id: int
    lecture_id: int
    lecture_title: str
    watched_seconds: int
    last_position: int
    is_completed: bool
    completion_rate: float  # 해당 강의 완료율
    last_watched_at: datetime
    completed_at: Optional[datetime]
    
    class Config:
        from_attributes = True

class LectureProgressSummary(BaseModel):
    lecture_id: int
    lecture_title: str
    duration_seconds: int
    watched_seconds: int
    last_position: int
    is_completed: bool
    completion_rate: float
    last_watched_at: Optional[datetime]

class ChapterProgressSummary(BaseModel):
    chapter_id: int
    chapter_title: str
    total_lectures: int
    completed_lectures: int
    total_duration: int
    watched_duration: int
    progress_rate: float
    lectures: list[LectureProgressSummary] = []

class CourseProgressDetail(BaseModel):
    course_id: int
    course_title: str
    total_duration: int
    watched_duration: int
    progress_rate: float
    total_lectures: int
    completed_lectures: int
    last_watched_at: Optional[datetime]
    chapters: list[ChapterProgressSummary] = []
    
    class Config:
        from_attributes = True

# ============= 학습 대시보드 =============
class StudentDashboard(BaseModel):
    total_enrollments: int
    active_enrollments: int
    completed_courses: int
    total_study_time: int  # 분 단위
    avg_progress_rate: float
    recent_activities: list[dict] = []
    upcoming_expiries: list[dict] = []  # 만료 임박 강의
    
    class Config:
        from_attributes = True

class LearningStats(BaseModel):
    today_study_time: int  # 오늘 학습 시간 (분)
    week_study_time: int  # 이번 주 학습 시간
    month_study_time: int  # 이번 달 학습 시간
    total_study_time: int  # 총 학습 시간
    study_streak: int  # 연속 학습 일수
    last_study_date: Optional[datetime]

class EnrollmentPaginatedResponse(BaseModel):
    total: int
    page: int
    page_size: int
    total_pages: int
    items: List[EnrollmentResponse]
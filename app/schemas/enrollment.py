from pydantic import BaseModel, Field
from typing import List, Optional, Annotated
from datetime import datetime
from enum import Enum
from fastapi import Query

# course.py의 타입들을 import (TYPE_CHECKING으로 순환 참조 방지)
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from app.schemas.course import CourseType, CategoryType, Difficulty, PriceType, VideoType
else:
    from app.schemas.course import CourseType, CategoryType, Difficulty, PriceType, VideoType

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

# ============= 내 강의실 (통합) =============
class EnrollmentStatus(str, Enum):
    """수강 상태"""
    AVAILABLE = "available"  # 학습 가능
    EXPIRED = "expired"  # 만료

class LearningStatus(str, Enum):
    """학습 상태"""
    NOT_STARTED = "not_started"  # 학습 예정
    IN_PROGRESS = "in_progress"  # 학습 중
    COMPLETED = "completed"  # 학습 완료

class MyCourseSummary(BaseModel):
    """내 강의 목록 아이템"""
    id: int
    title: str
    thumbnail_url: str
    course_type: 'CourseType'
    category_type: 'CategoryType'
    difficulty: 'Difficulty'
    instructor_name: str

    # 진행률 정보
    total_lectures: int  # 전체 강의 영상 수
    completed_lectures: int  # 완료한 강의 영상 수
    progress_rate: float  # 전체 완료율 (0-100)

    # 수강 정보
    enrollment_status: EnrollmentStatus
    learning_status: LearningStatus
    enrolled_at: datetime
    expires_at: Optional[datetime] = None

    # 최근 학습 정보
    last_watched_chapter: Optional[str] = None
    last_watched_lecture: Optional[str] = None
    last_watched_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class MyCourseListParams:
    """내 강의 목록 필터링 파라미터"""
    def __init__(
        self,
        enrollment_status: Annotated[Optional[EnrollmentStatus], Query(
            description="수강 상태 (전체=None, available=학습 가능, expired=만료)"
        )] = None,
        learning_status: Annotated[Optional[LearningStatus], Query(
            description="학습 상태 (전체=None, not_started=학습 예정, in_progress=학습중, completed=학습 완료)"
        )] = None,
        course_type: Annotated[Optional[CourseType], Query(
            description="강의 유형 (전체=None, vod=VOD, boost_community=부스트 커뮤니티, kdc=KDC)"
        )] = None,
        category_type: Annotated[Optional[CategoryType], Query(
            description="카테고리 (전체=None, frontend=프론트엔드, backend=백엔드, data_analysis=데이터 분석, ai=인공지능, design=디자인, other=기타)"
        )] = None,
        difficulty: Annotated[Optional[Difficulty], Query(
            description="난이도 (전체=None, beginner=초급, intermediate=중급, advanced=고급)"
        )] = None,
        page: int = Query(default=1, ge=1),
        page_size: int = Query(default=20, ge=1, le=100)
    ):
        self.enrollment_status = enrollment_status
        self.learning_status = learning_status
        self.course_type = course_type
        self.category_type = category_type
        self.difficulty = difficulty
        self.page = page
        self.page_size = page_size

class MyCoursePaginatedResponse(BaseModel):
    """내 강의 목록 페이지네이션 응답"""
    items: List[MyCourseSummary]
    total: int
    page: int
    page_size: int
    total_pages: int

    class Config:
        from_attributes = True

class MyLectureProgress(BaseModel):
    """내 강의 영상 진행 정보"""
    id: int
    chapter_id: int
    title: str
    description: Optional[str]
    video_url: str
    video_type: 'VideoType'
    duration_seconds: int
    order_number: int
    material_url: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    # 진행 정보
    is_completed: bool = False
    last_position: int = 0  # 마지막 시청 위치 (초)
    watched_seconds: int = 0  # 시청한 시간 (초)

    class Config:
        from_attributes = True

class MyChapterWithLectures(BaseModel):
    """내 강의의 챕터 (강의 영상 포함)"""
    id: int
    course_id: int
    title: str
    description: Optional[str]
    order_number: int
    total_duration: int = 0
    lectures: List[MyLectureProgress] = []

    class Config:
        from_attributes = True

class MyCourseDetail(BaseModel):
    """내 강의 상세 정보"""
    id: int
    category_type: 'CategoryType'
    course_type: 'CourseType'
    title: str
    description: str
    thumbnail_url: str
    instructor_name: str
    instructor_bio: str
    instructor_description: Optional[str] = None
    instructor_image: str
    price_type: 'PriceType'
    price: int
    difficulty: 'Difficulty'
    total_duration: int

    # 수강 정보
    enrollment_status: EnrollmentStatus
    learning_status: LearningStatus
    enrolled_at: datetime
    expires_at: Optional[datetime] = None

    # 진행률 정보
    total_lectures: int
    completed_lectures: int
    progress_rate: float  # 0-100

    # 최근 학습 정보
    last_watched_chapter_id: Optional[int] = None
    last_watched_lecture_id: Optional[int] = None
    last_watched_at: Optional[datetime] = None

    # 챕터 및 강의 영상
    chapters: List[MyChapterWithLectures] = []

    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# Forward References 업데이트 (순환 참조 해결)
MyCourseDetail.model_rebuild()
MyChapterWithLectures.model_rebuild()
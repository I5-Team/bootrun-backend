from pydantic import BaseModel, Field, field_validator
from typing import Optional, List, Dict, Any, Annotated
from datetime import datetime
from enum import Enum
from fastapi import Query

# Enums
class CategoryType(str, Enum):
    FRONTEND = "frontend"
    BACKEND = "backend"
    DATA_ANALYSIS = "data_analysis"
    AI = "ai"
    DESIGN = "design"
    OTHER = "other"

class CourseType(str, Enum):
    VOD = "vod"
    BOOST_COMMUNITY = "boost_community"
    KDC = "kdc"

class Difficulty(str, Enum):
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"

class PriceType(str, Enum):
    FREE = "free"
    PAID = "paid"
    NATIONAL_SUPPORT = "national_support"

class VideoType(str, Enum):
    VOD = "vod"
    YOUTUBE = "youtube"

# ============= 강의 검색 메타데이터 =============
class CategoryMetadata(BaseModel):
    value: CategoryType
    label: str
    description: Optional[str] = None

class CourseTypeMetadata(BaseModel):
    value: CourseType
    label: str

class DifficultyMetadata(BaseModel):
    value: Difficulty
    label: str

class PriceTypeMetadata(BaseModel):
    value: PriceType
    label: str

class CourseMetadataResponse(BaseModel):
    categories: List[CategoryMetadata]
    course_types: List[CourseTypeMetadata]
    difficulties: List[DifficultyMetadata]
    price_types: List[PriceTypeMetadata]

# ============= 강의 =============
class CourseCreate(BaseModel):
    category_type: CategoryType = Field(
        ...,
        description="강의 카테고리 (frontend, backend, data_analysis, ai, design, other)", 
        example="backend"
    )
    course_type: CourseType = Field(
        default=CourseType.VOD,
        description="강의 유형", 
        example="vod"
    )
    title: str = Field(
        ..., 
        min_length=1, 
        max_length=200,
        description="강의 제목", 
        example="FastAPI 완벽 가이드"
    )
    description: str = Field(
        ...,
        description="강의 설명 (HTML 가능)", 
        example="FastAPI를 활용한 백엔드 개발 완벽 마스터 과정입니다."
    )
    thumbnail_url: str = Field(
        ...,
        description="썸네일 이미지 URL", 
        example="https://example.com/thumbnail.jpg"
    )
    instructor_name: str = Field(
        ..., 
        min_length=1, 
        max_length=100,
        description="강사명", 
        example="김철수"
    )
    instructor_bio: str = Field(
        ...,
        description="강사 소개", 
        example="10년 경력의 백엔드 개발자입니다."
    )
    instructor_image: str = Field(
        ...,
        description="강사 프로필 이미지 URL", 
        example="https://example.com/instructor.jpg"
    )
    difficulty: Difficulty = Field(
        ...,
        description="난이도 (beginner, intermediate, advanced)", 
        example="beginner"
    )
    price_type: PriceType = Field(
        default=PriceType.PAID,
        description="가격 유형", 
        example="paid"
    )
    price: int = Field(
        default=50000, 
        ge=0,
        description="가격 (원)", 
        example=50000
    )
    faq: Optional[str] = Field(
        None,
        description="자주 묻는 질문 (JSON 형식)", 
        example='[{"question":"환불이 가능한가요?","answer":"구매일로부터 7일 이내, 진도율 10% 미만일 경우 환불 가능합니다."}]'
    )

class CourseUpdate(BaseModel):
    category_type: Optional[CategoryType] = None
    course_type: Optional[CourseType] = None
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    thumbnail_url: Optional[str] = None
    instructor_name: Optional[str] = Field(None, min_length=1, max_length=100)
    instructor_bio: Optional[str] = None
    instructor_image: Optional[str] = None
    difficulty: Optional[Difficulty] = None
    price_type: Optional[PriceType] = None
    price: Optional[int] = Field(None, ge=0)
    faq: Optional[str] = None
    is_published: Optional[bool] = Field(
        None,
        description="강의 공개 여부 (false: 준비 중, true: 공개)", 
        example=True
    )

class CourseResponse(BaseModel):
    id: int
    category_type: CategoryType
    course_type: CourseType
    title: str
    description: str
    thumbnail_url: str
    instructor_name: str
    instructor_bio: str
    instructor_image: str
    price_type: PriceType
    price: int
    difficulty: Difficulty
    total_duration: int  # 초 단위
    faq: Optional[str]
    is_published: bool
    enrollment_count: int = 0
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class CourseDetailResponse(BaseModel):
    id: int
    category_type: CategoryType
    course_type: CourseType
    title: str
    description: str
    thumbnail_url: str
    instructor_name: str
    instructor_bio: str
    instructor_image: str
    price_type: PriceType
    price: int
    difficulty: Difficulty
    total_duration: int
    faq: Optional[str]
    is_published: bool
    enrollment_count: int = 0
    created_at: datetime
    updated_at: datetime
    # 추가 정보
    chapters: List['ChapterWithLectures'] = []
    is_enrolled: bool = False
    my_progress: Optional[float] = None

    class Config:
        from_attributes = True

class CourseListParams:
    def __init__(
        self,
        category_types: Annotated[Optional[List[CategoryType]], Query(
            description="강의 카테고리 (여러 개 선택 가능)"
        )] = None,
        course_types: Annotated[Optional[List[CourseType]], Query(
            description="강의 유형 (여러 개 선택 가능)"
        )] = None,
        difficulties: Annotated[Optional[List[Difficulty]], Query(
            description="난이도 (여러 개 선택 가능)"
        )] = None,
        price_types: Annotated[Optional[List[PriceType]], Query(
            description="가격 유형 (여러 개 선택 가능)"
        )] = None,
        keyword: Annotated[Optional[str], Query(
            description="검색 키워드 (강의명, 강의 설명)"
        )] = None,
        is_published: Optional[bool] = True,
        page: int = Query(default=1, ge=1),
        page_size: int = Query(default=20, ge=1, le=100)
    ):
        self.category_types = category_types
        self.course_types = course_types
        self.difficulties = difficulties
        self.price_types = price_types
        self.keyword = keyword
        self.is_published = is_published
        self.page = page
        self.page_size = page_size

class CoursePaginatedResponse(BaseModel):
    items: List[CourseResponse]
    total: int
    page: int
    page_size: int
    total_pages: int
    
    class Config:
        from_attributes = True

# ============= 챕터 =============
class ChapterCreate(BaseModel):
    title: str = Field(
        ..., 
        min_length=1, 
        max_length=200,
        description="챕터 제목", 
        example="1. FastAPI 시작하기"
    )
    description: Optional[str] = Field(
        None,
        description="챕터 설명", 
        example="FastAPI의 기본 개념과 설치 방법을 학습합니다."
    )
    order_number: int = Field(
        ..., 
        ge=1,
        description="챕터 순서 (1부터 시작)", 
        example=1
    )

class ChapterUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    order_number: Optional[int] = Field(None, ge=1)

class ChapterResponse(BaseModel):
    id: int
    course_id: int
    title: str
    description: Optional[str]
    order_number: int
    total_duration: int = 0  # 챕터 내 강의 총 시간
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class ChapterWithLectures(BaseModel):
    id: int
    course_id: int
    title: str
    description: Optional[str]
    order_number: int
    total_duration: int = 0
    lectures: List['LectureResponse'] = []

    class Config:
        from_attributes = True

# ============= 강의 영상 =============
class LectureCreate(BaseModel):
    title: str = Field(
        ...,
        min_length=1,
        max_length=200,
        description="강의 제목",
        example="FastAPI 설치하기"
    )
    description: Optional[str] = Field(
        None,
        description="강의 설명",
        example="FastAPI를 설치하는 방법을 배웁니다."
    )
    video_url: str = Field(
        ...,
        description="동영상 URL (VOD 또는 유튜브)",
        example="https://youtube.com/watch?v=abc123"
    )
    video_type: VideoType = Field(
        ...,
        description="동영상 타입 (vod 또는 youtube)",
        example="youtube"
    )
    duration_seconds: int = Field(
        ...,
        ge=0,
        description="재생 시간 (초)",
        example=600
    )
    order_number: int = Field(
        ...,
        ge=1,
        description="강의 순서 (챕터 내)",
        example=1
    )
    material_url: Optional[str] = Field(
        None,
        description="강의 자료 URL",
        example="https://example.com/materials/lecture1.pdf"
    )

class LectureUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    video_url: Optional[str] = None
    video_type: Optional[VideoType] = None
    duration_seconds: Optional[int] = Field(None, ge=0)
    order_number: Optional[int] = Field(None, ge=1)
    material_url: Optional[str] = None

class LectureResponse(BaseModel):
    id: int
    chapter_id: int
    title: str
    description: Optional[str]
    video_url: str
    video_type: VideoType
    duration_seconds: int
    order_number: int
    material_url: Optional[str] = None
    # 사용자별 시청 정보 (optional)
    is_completed: Optional[bool] = None
    last_position: Optional[int] = None
    watched_seconds: Optional[int] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# ============= 학습 Q&A =============
class QuestionCreate(BaseModel):
    course_id: int = Field(
        ..., 
        gt=1,
        description="질문할 강의 ID", 
        example=1
    )
    title: str = Field(
        ..., 
        min_length=1, 
        max_length=200,
        description="질문 제목", 
        example="FastAPI 설치 중 에러가 발생합니다"
    )
    content: str = Field(
        ..., 
        min_length=1,
        description="질문 내용", 
        example="pip install fastapi 실행 시 ModuleNotFoundError가 발생합니다. 어떻게 해결하나요?"
    )

class QuestionUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    content: Optional[str] = Field(None, min_length=1)

class QuestionResponse(BaseModel):
    id: int
    user_id: int
    user_nickname: str
    course_id: int
    course_title: str
    title: str
    content: str
    view_count: int = 0
    is_answered: bool = False
    comment_count: int = 0
    created_at: datetime
    updated_at: datetime
    is_deleted: bool = False 
    deleted_at: Optional[datetime]
    deleted_by: Optional[int]
    
    class Config:
        from_attributes = True

class QuestionDetailResponse(BaseModel):
    id: int
    user_id: int
    user_nickname: str
    course_id: int
    course_title: str
    title: str
    content: str
    view_count: int
    is_answered: bool
    created_at: datetime
    updated_at: datetime
    comments: List['CommentResponse'] = []
    
    class Config:
        from_attributes = True

class QuestionListParams(BaseModel):
    course_id: Optional[int] = Field(
        None,
        description="강의 ID로 필터링", 
        example=1
    )
    is_answered: Optional[bool] = Field(
        None,
        description="답변 완료 여부로 필터링", 
        example=False
    )
    keyword: Optional[str] = Field(
        None,
        description="검색 키워드 (제목, 내용)", 
        example="설치"
    )
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=20, ge=1, le=100)

class QuestionPaginatedResponse(BaseModel):
    items: List[QuestionResponse]
    total: int
    page: int
    page_size: int
    total_pages: int
    
    class Config:
        from_attributes = True

# ============= 댓글 =============
class CommentCreate(BaseModel):
    question_id: int = Field(
        ..., 
        gt=1,
        description="댓글을 달 질문 ID", 
        example=1
    )
    content: str = Field(
        ..., 
        min_length=1,
        description="댓글 내용", 
        example="Python 버전을 확인해보세요. FastAPI는 Python 3.7 이상이 필요합니다."
    )
    parent_id: int | None = Field(
        None, 
        ge=1,
        description="부모 댓글 ID (대댓글인 경우)", 
        example=None
    )

class CommentUpdate(BaseModel):
    content: str = Field(
        ..., 
        min_length=1,
        description="수정할 댓글 내용"
    )

class CommentSummary(BaseModel):
    id: int
    user_id: int
    user_nickname: str
    user_role: str
    content: str
    is_instructor_answer: bool = False
    created_at: datetime
    reply_count: int = 0  # 대대댓글 개수만 표시
    
    class Config:
        from_attributes = True

class CommentResponse(BaseModel):
    id: int
    question_id: int
    user_id: int
    user_nickname: str
    user_role: str
    parent_id: Optional[int]
    content: str
    is_instructor_answer: bool = False
    created_at: datetime
    updated_at: datetime
    replies: List[CommentSummary] = []  
    reply_count: int = 0  # 전체 대댓글 수
    
    class Config:
        from_attributes = True

# ============= Forward References 업데이트 =============
# 순환 참조 문제 해결을 위해 모델 재빌드
CourseDetailResponse.model_rebuild()
ChapterWithLectures.model_rebuild()
QuestionDetailResponse.model_rebuild()
CommentResponse.model_rebuild()
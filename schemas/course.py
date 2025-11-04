from pydantic import BaseModel, Field, field_validator
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


# Enums
class CategoryType(str, Enum):
    FRONTEND = "frontend"
    BACKEND = "backend"
    DATA_ANALYSIS = "data_analysis"
    AI = "ai"
    DESIGN = "design"
    OTHER = "other"


class Difficulty(str, Enum):
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"


class VideoType(str, Enum):
    VOD = "vod"
    YOUTUBE = "youtube"


# ============= 카테고리 =============
class CategoryResponse(BaseModel):
    id: int
    name: CategoryType
    display_name: str
    description: Optional[str]
    display_order: int
    course_count: int = 0
    
    class Config:
        from_attributes = True

class CategoryCreate(BaseModel):
    name: CategoryType
    display_name: str = Field(..., min_length=1, max_length=50)
    description: Optional[str] = None
    display_order: int = Field(default=0, ge=0)


class CategoryUpdate(BaseModel):
    display_name: Optional[str] = Field(None, min_length=1, max_length=50)
    description: Optional[str] = None
    display_order: Optional[int] = Field(None, ge=0)


# ============= 강의 =============
class CourseCreate(BaseModel):
    category_id: int = Field(..., gt=0)
    title: str = Field(..., min_length=1, max_length=200)
    description: str
    thumbnail_url: str
    instructor_name: str = Field(..., min_length=1, max_length=100)
    instructor_bio: str
    instructor_image: str
    difficulty: Difficulty
    faq: Optional[str] = None


class CourseUpdate(BaseModel):
    category_id: Optional[int] = Field(None, gt=0)
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    thumbnail_url: Optional[str] = None
    instructor_name: Optional[str] = Field(None, min_length=1, max_length=100)
    instructor_bio: Optional[str] = None
    instructor_image: Optional[str] = None
    difficulty: Optional[Difficulty] = None
    faq: Optional[str] = None
    is_published: Optional[bool] = None


class CourseResponse(BaseModel):
    id: int
    category_id: int
    category_name: str
    title: str
    description: str
    thumbnail_url: str
    instructor_name: str
    instructor_bio: str
    instructor_image: str
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
    category_id: int
    category_name: str
    title: str
    description: str
    thumbnail_url: str
    instructor_name: str
    instructor_bio: str
    instructor_image: str
    price: int
    difficulty: Difficulty
    total_duration: int
    faq: Optional[str]
    is_published: bool
    enrollment_count: int
    created_at: datetime
    updated_at: datetime
    # 추가 정보
    chapters: List['ChapterWithLectures'] = []
    is_enrolled: bool = False
    my_progress: Optional[float] = None
    
    class Config:
        from_attributes = True


class CourseListParams(BaseModel):
    category_id: Optional[int] = None
    difficulty: Optional[Difficulty] = None
    keyword: Optional[str] = None
    is_published: Optional[bool] = True
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=20, ge=1, le=100)


# ============= 챕터 =============
class ChapterCreate(BaseModel):
    course_id: int = Field(..., gt=0)
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    order_number: int = Field(..., ge=1)


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
    total_duration: int
    lectures: List['LectureResponse'] = []
    
    class Config:
        from_attributes = True


# ============= 강의 영상 =============
class LectureCreate(BaseModel):
    chapter_id: int = Field(..., gt=0)
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    video_url: str
    video_type: VideoType
    duration_seconds: int = Field(..., ge=0)
    order_number: int = Field(..., ge=1)


class LectureUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    video_url: Optional[str] = None
    video_type: Optional[VideoType] = None
    duration_seconds: Optional[int] = Field(None, ge=0)
    order_number: Optional[int] = Field(None, ge=1)


class LectureResponse(BaseModel):
    id: int
    chapter_id: int
    title: str
    description: Optional[str]
    video_url: str
    video_type: VideoType
    duration_seconds: int
    order_number: int
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
    course_id: int = Field(..., gt=0)
    title: str = Field(..., min_length=1, max_length=200)
    content: str = Field(..., min_length=1)


class QuestionUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    content: Optional[str] = Field(None, min_length=1)


class QuestionResponse(BaseModel):
    id: int
    user_id: int
    user_name: str
    course_id: int
    course_title: str
    title: str
    content: str
    view_count: int = 0
    is_answered: bool = False
    comment_count: int = 0
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class QuestionDetailResponse(BaseModel):
    id: int
    user_id: int
    user_name: str
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
    course_id: Optional[int] = None
    is_answered: Optional[bool] = None
    keyword: Optional[str] = None
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=20, ge=1, le=100)


# ============= 댓글 =============
class CommentCreate(BaseModel):
    question_id: int = Field(..., gt=0)
    content: str = Field(..., min_length=1)
    parent_id: Optional[int] = Field(None, gt=0)


class CommentUpdate(BaseModel):
    content: str = Field(..., min_length=1)


class CommentResponse(BaseModel):
    id: int
    question_id: int
    user_id: int
    user_name: str
    user_role: str
    parent_id: Optional[int]
    content: str
    is_instructor_answer: bool = False
    created_at: datetime
    updated_at: datetime
    replies: List['CommentResponse'] = []
    
    class Config:
        from_attributes = True
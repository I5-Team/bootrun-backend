from pydantic import BaseModel, Field
from typing import Optional, List, Any, Generic, TypeVar
from datetime import datetime, timezone  

T = TypeVar('T')

# 페이지네이션
class PaginationParams(BaseModel):
    page: int = Field(
        default=1, 
        ge=1, 
        description="페이지 번호 (1부터 시작)", 
        example=1
    )
    page_size: int = Field(
        default=20, 
        ge=1, 
        le=100, 
        description="페이지당 항목 수 (최대 100개)", 
        example=20
    )

class PaginatedResponse(BaseModel, Generic[T]):
    total: int
    page: int
    page_size: int
    total_pages: int
    items: List[T]

# 공통 응답
class MessageResponse(BaseModel):
    message: str
    detail: str | None = None

class ErrorResponse(BaseModel):
    error: str
    detail: Optional[str] = None

# 날짜 필터
class DateRangeFilter(BaseModel):
    start_date: Optional[datetime] = Field(
        None, 
        description="시작 날짜 (YYYY-MM-DDTHH:MM:SS 형식)", 
        example="2025-01-01T00:00:00"
    )
    end_date: Optional[datetime] = Field(
        None, 
        description="종료 날짜 (YYYY-MM-DDTHH:MM:SS 형식)", 
        example="2025-12-31T23:59:59"
    )

# 파일 업로드
class FileUploadResponse(BaseModel):
    file_url: str
    file_name: str
    file_size: int  # bytes
    content_type: str
    uploaded_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))  

class ImageUploadResponse(BaseModel):
    image_url: str
    thumbnail_url: str | None = None
    width: Optional[int] = None
    height: Optional[int] = None
    file_size: int
    uploaded_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))  

class ProfileImageUploadResponse(BaseModel):
    image_url: str
    file_size: int
    uploaded_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
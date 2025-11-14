from pydantic import BaseModel, Field
from typing import Optional, List, Any, Generic, TypeVar
from datetime import datetime
from app.utils.helpers import get_current_utc_datetime

T = TypeVar('T')

# =====================================================
# 페이지네이션 요청 파라미터
# =====================================================
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

# =====================================================
# 성공 응답 스키마
# =====================================================
class SuccessResponse(BaseModel, Generic[T]):
    """성공 응답을 위한 제네릭 래퍼 클래스

    데이터와 함께 성공 상태 및 선택적 메시지를 포함합니다.
    모든 성공 응답에 일관된 구조를 제공합니다.
    """
    success: bool = Field(default=True, description="요청 성공 여부")
    message: Optional[str] = Field(None, description="성공 메시지")
    data: T = Field(..., description="응답 데이터")

    class Config:
        from_attributes = True

class MessageResponse(BaseModel):
    """데이터 없이 메시지만 반환하는 응답 클래스

    주로 삭제, 업데이트 등의 작업에서 사용됩니다.
    """
    success: bool = Field(default=True, description="요청 성공 여부")
    message: str = Field(..., description="응답 메시지")
    detail: Optional[str] = Field(None, description="추가 상세 정보")

    class Config:
        from_attributes = True

class PaginatedResponse(BaseModel, Generic[T]):
    """페이지네이션된 목록 응답 클래스

    목록 데이터와 함께 페이지네이션 메타데이터를 포함합니다.
    """
    success: bool = Field(default=True, description="요청 성공 여부")
    total: int = Field(..., description="전체 항목 수", ge=0)
    page: int = Field(..., description="현재 페이지 번호", ge=1)
    page_size: int = Field(..., description="페이지당 항목 수", ge=1, le=100)
    total_pages: int = Field(..., description="전체 페이지 수", ge=0)
    items: List[T] = Field(..., description="항목 목록")

    class Config:
        from_attributes = True

# =====================================================
# 에러 응답 스키마 (하위 호환성 유지)
# =====================================================
class ErrorResponse(BaseModel):
    """에러 응답 클래스

    주로 예외 처리에서 사용됩니다.
    실제 에러는 exceptions 폴더의 클래스를 사용합니다.
    """
    error: str = Field(..., description="에러 코드")
    detail: Optional[str] = Field(None, description="에러 상세 메시지")

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
    uploaded_at: datetime = Field(default_factory=get_current_utc_datetime)

class ImageUploadResponse(BaseModel):
    image_url: str
    thumbnail_url: str | None = None
    width: Optional[int] = None
    height: Optional[int] = None
    file_size: int
    uploaded_at: datetime = Field(default_factory=get_current_utc_datetime)

class ProfileImageUploadResponse(BaseModel):
    image_url: str
    file_size: int
    uploaded_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
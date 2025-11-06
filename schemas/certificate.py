from pydantic import BaseModel, Field, field_validator
from typing import Optional
from datetime import datetime
import re


# ============= 수료증 =============
class CertificateCreate(BaseModel):
    enrollment_id: int = Field(
        ..., 
        ge=1,
        description="수료증을 발급할 수강 등록 ID", 
        example=1
    )


class CertificateResponse(BaseModel):
    id: int
    user_id: int
    user_nickname: str
    course_id: int
    course_title: str
    certificate_number: str
    issued_at: datetime
    pdf_url: Optional[str]
    pdf_generated_at: Optional[datetime]
    
    class Config:
        from_attributes = True


class CertificateListResponse(BaseModel):
    id: int
    course_id: int
    course_title: str
    category_name: str
    certificate_number: str
    issued_at: datetime
    pdf_url: Optional[str]
    
    class Config:
        from_attributes = True


class CertificateGenerationRequest(BaseModel):
    certificate_id: int = Field(
        ..., 
        ge=1,
        description="PDF를 생성할 수료증 ID", 
        example=1
    )


class CertificateGenerationResponse(BaseModel):
    certificate_id: int
    pdf_url: str
    generated_at: datetime


# ============= 수료증 진위 확인 =============
class CertificateVerifyRequest(BaseModel):
    certificate_number: str = Field(
        ..., 
        min_length=10, 
        max_length=100,
        description="수료증 번호 (형식: WNIV-YYYY-NNNNNN)", 
        example="WNIV-2025-000001"
    )
    
    @field_validator('certificate_number')
    @classmethod
    def validate_certificate_number(cls, v):
        pattern = r'^WNIV-\d{4}-\d{6}$'
        if not re.match(pattern, v):
            raise ValueError('올바른 수료증 번호 형식이 아닙니다 (예: WNIV-2025-000001)')
        return v


class CertificateVerifyResponse(BaseModel):
    is_valid: bool
    message: str
    certificate: Optional['CertificateVerifyDetail'] = None


class CertificateVerifyDetail(BaseModel):
    certificate_number: str
    user_nickname: str
    course_title: str
    category_name: str
    issued_at: datetime
    
    class Config:
        from_attributes = True


# ============= 수료 조건 체크 =============
class CompletionCheckRequest(BaseModel):
    enrollment_id: int = Field(
        ..., 
        ge=1,
        description="수료 조건을 확인할 수강 등록 ID", 
        example=1
    )


class CompletionCheckResponse(BaseModel):
    is_eligible: bool
    message: str
    requirements: dict  # 수료 조건 상세 정보
    # {
    #     "progress_rate": 100.0,
    #     "required_progress": 100.0,
    #     "missions_completed": True,
    #     "midterm_passed": True,
    #     "final_passed": True
    # }


class CompletionRequirement(BaseModel):
    progress_rate: float
    required_progress: float = 100.0
    lectures_completed: int
    total_lectures: int
    missions_completed: bool
    midterm_passed: bool
    final_passed: bool
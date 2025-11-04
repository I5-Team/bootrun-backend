from pydantic import BaseModel, Field, field_validator
from typing import Optional
from datetime import datetime
import re


# ============= 수료증 =============
class CertificateCreate(BaseModel):
    enrollment_id: int = Field(..., gt=0)


class CertificateResponse(BaseModel):
    id: int
    user_id: int
    user_name: str
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
    certificate_id: int = Field(..., gt=0)


class CertificateGenerationResponse(BaseModel):
    certificate_id: int
    pdf_url: str
    generated_at: datetime


# ============= 수료증 진위 확인 =============
class CertificateVerifyRequest(BaseModel):
    certificate_number: str = Field(..., min_length=10, max_length=100)
    
    @field_validator('certificate_number')
    @classmethod
    def validate_certificate_number(cls, v: str) -> str:  # 타입 힌트 추가
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
    user_name: str
    course_title: str
    category_name: str
    issued_at: datetime
    
    class Config:
        from_attributes = True


# ============= 수료 조건 체크 =============
class CompletionCheckRequest(BaseModel):
    enrollment_id: int = Field(..., gt=0)


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
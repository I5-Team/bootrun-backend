from pydantic import BaseModel, Field, field_validator, model_validator
from typing import List, Optional, Any
from datetime import datetime
from enum import Enum


# Enums
class PaymentMethod(str, Enum):
    CARD = "card"
    TRANSFER = "transfer"
    EASY = "easy"


class PaymentStatus(str, Enum):
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"
    REFUNDED = "refunded"


class RefundStatus(str, Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"


# ============= 결제 =============
class PaymentCreate(BaseModel):
    course_id: int = Field(
        ..., 
        gt=1,
        description="결제할 강의 ID", 
        example=1
    )
    payment_method: PaymentMethod = Field(
        ...,
        description="결제 방식 (card: 신용카드, transfer: 계좌이체, easy: 간편결제)", 
        example="card"
    )
    coupon_code: Optional[str] = Field(
        None, 
        max_length=50,
        description="쿠폰 코드 (선택)", 
        example="WELCOME2025"
    )


class PaymentResponse(BaseModel):
    id: int
    user_id: int
    course_id: int
    course_title: str
    amount: int  # 원(KRW) 단위, 소수점 없음
    discount_amount: int = 0  # 원(KRW) 단위
    final_amount: int  # 원(KRW) 단위
    payment_method: PaymentMethod
    status: PaymentStatus
    transaction_id: str
    receipt_url: Optional[str]
    paid_at: Optional[datetime]
    created_at: datetime
    
    class Config:
        from_attributes = True
        # 금액은 정수형 원(KRW) 단위로 저장됩니다.
        # 예: 50000 = 50,000원


class PaymentDetailResponse(BaseModel):
    id: int
    user_id: int
    user_nickname: str
    user_email: str
    course_id: int
    course_title: str
    amount: int
    discount_amount: int
    final_amount: int
    payment_method: PaymentMethod
    status: PaymentStatus
    transaction_id: str
    receipt_url: Optional[str]
    coupon_used: Optional[str]  # 쿠폰 코드
    paid_at: Optional[datetime]
    created_at: datetime
    # 환불 가능 여부
    can_refund: bool = False
    refund_reason: Optional[str] = None  # 환불 불가 사유
    
    class Config:
        from_attributes = True


class PaymentListParams(BaseModel):
    status: Optional[PaymentStatus] = Field(
        None,
        description="결제 상태로 필터링", 
        example="completed"
    )
    payment_method: Optional[PaymentMethod] = Field(
        None,
        description="결제 방식으로 필터링", 
        example="card"
    )
    start_date: Optional[datetime] = Field(
        None,
        description="시작 날짜", 
        example="2025-01-01T00:00:00"
    )
    end_date: Optional[datetime] = Field(
        None,
        description="종료 날짜", 
        example="2025-12-31T23:59:59"
    )
    keyword: Optional[str] = Field(
        None,
        description="검색 키워드 (사용자 이름, 이메일, 강의명)", 
        example="FastAPI"
    )
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=20, ge=1, le=100)


class PaymentConfirmRequest(BaseModel):
    transaction_id: str = Field(
        ..., 
        min_length=1, 
        max_length=100,
        description="PG사 거래 ID", 
        example="toss_payment_123abc"
    )

# ============= 쿠폰 =============
class CouponCreate(BaseModel):
    course_id: Optional[int] = Field(
        None, 
        gt=1,
        description="쿠폰이 적용될 강의 ID (NULL이면 전체 강의)", 
        example=1
    )
    code: str = Field(
        ..., 
        min_length=3, 
        max_length=50,
        description="쿠폰 코드 (중복 불가)", 
        example="WELCOME2025"
    )
    name: str = Field(
        ..., 
        min_length=1, 
        max_length=100,
        description="쿠폰 이름", 
        example="신규 회원 환영 쿠폰"
    )
    description: str = Field(
        ...,
        description="쿠폰 설명", 
        example="신규 회원을 위한 20% 할인 쿠폰입니다."
    )
    discount_rate: Optional[int] = Field(
        None, 
        ge=0, 
        le=100, 
        description="할인율 (%, 정수, discount_amount와 둘 중 하나 필수)", 
        example=20
    )
    discount_amount: Optional[int] = Field(
        None, 
        ge=0, 
        description="할인 금액 (원, 정수, discount_rate와 둘 중 하나 필수)", 
        example=10000
    )
    valid_from: datetime = Field(
        ...,
        description="쿠폰 유효 시작일", 
        example="2025-01-01T00:00:00"
    )
    valid_until: datetime = Field(
        ...,
        description="쿠폰 유효 종료일", 
        example="2025-12-31T23:59:59"
    )
    max_usage: int = Field(
        default=0, 
        ge=0,
        description="최대 사용 인원 (0이면 무제한)", 
        example=100
    )
    
    @model_validator(mode='after')
    def validate_discount(self) -> 'CouponCreate':
        """할인율 또는 할인 금액 중 하나는 필수"""
        if self.discount_rate is None and self.discount_amount is None:
            raise ValueError('할인율 또는 할인 금액 중 하나는 필수입니다')
        return self
    

class CouponUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = None
    valid_from: Optional[datetime] = None
    valid_until: Optional[datetime] = None
    max_usage: Optional[int] = Field(None, ge=0)
    is_active: Optional[bool] = Field(
        None,
        description="쿠폰 활성화 여부", 
        example=True
    )


class CouponResponse(BaseModel):
    id: int
    course_id: Optional[int]
    course_title: Optional[str]  # course_id가 None이면 "전체 강의"
    code: str
    name: str
    description: str
    discount_rate: Optional[int]
    discount_amount: Optional[int]
    valid_from: datetime
    valid_until: datetime
    max_usage: int
    used_count: int = 0
    is_active: bool
    is_available: bool = True  # 현재 사용 가능 여부
    created_at: datetime
    
    class Config:
        from_attributes = True


class CouponValidationRequest(BaseModel):
    code: str = Field(
        ..., 
        min_length=3, 
        max_length=50,
        description="검증할 쿠폰 코드", 
        example="WELCOME2025"
    )
    course_id: int = Field(
        ..., 
        gt=1,
        description="적용할 강의 ID", 
        example=1
    )


class CouponValidationResponse(BaseModel):
    is_valid: bool
    message: str
    coupon: Optional[CouponResponse] = None
    discount_amount: Optional[int] = None
    final_amount: Optional[int] = None

class CouponListParams(BaseModel):
    course_id: Optional[int] = Field(
        None, 
        gt=0, 
        description="강의 ID 필터"
    )
    is_active: Optional[bool] = Field(
        None, 
        description="활성화 여부 필터"
    )
    is_available: Optional[bool] = Field(
        None, 
        description="현재 사용 가능 여부 필터"
    )
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=20, ge=1, le=100)

# ============= 환불 =============
class RefundCreate(BaseModel):
    payment_id: int = Field(
        ..., 
        gt=1,
        description="환불할 결제 ID", 
        example=1
    )
    reason: str = Field(
        ..., 
        min_length=10, 
        max_length=500,
        description="환불 사유 (10자 이상)", 
        example="강의 내용이 생각과 달라서 환불 요청합니다."
    )


class RefundUpdate(BaseModel):
    status: RefundStatus = Field(
        ...,
        description="환불 상태 (pending, approved, rejected)", 
        example="approved"
    )
    admin_note: Optional[str] = Field(
        None, 
        max_length=500,
        description="관리자 메모", 
        example="환불 조건 충족하여 승인 처리"
    )


class RefundResponse(BaseModel):
    id: int
    payment_id: int
    user_id: int
    user_nickname: str
    amount: int
    reason: str
    status: RefundStatus
    admin_note: Optional[str]
    requested_at: datetime
    processed_at: Optional[datetime]
    # 결제 정보
    payment_date: datetime
    course_title: str
    progress_rate: float
    
    class Config:
        from_attributes = True

class RefundCheckResponse(BaseModel):
    can_refund: bool
    message: str
    payment_info: Optional[dict] = None


class PaymentPaginatedResponse(BaseModel):
    """결제 목록 페이지네이션 응답"""
    total: int
    page: int
    page_size: int
    total_pages: int
    items: List[PaymentResponse]
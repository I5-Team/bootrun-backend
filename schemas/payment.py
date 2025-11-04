from pydantic import BaseModel, Field, field_validator
from typing import Optional
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
    course_id: int = Field(..., gt=0)
    payment_method: PaymentMethod
    coupon_code: Optional[str] = Field(None, max_length=50)


class PaymentResponse(BaseModel):
    id: int
    user_id: int
    course_id: int
    course_title: str
    amount: int
    discount_amount: int = 0
    final_amount: int
    payment_method: PaymentMethod
    status: PaymentStatus
    transaction_id: str
    receipt_url: Optional[str]
    paid_at: Optional[datetime]
    created_at: datetime
    
    class Config:
        from_attributes = True


class PaymentDetailResponse(BaseModel):
    id: int
    user_id: int
    user_name: str
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
    status: Optional[PaymentStatus] = None
    payment_method: Optional[PaymentMethod] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    keyword: Optional[str] = None  # 사용자 이름, 이메일, 강의명으로 검색
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=20, ge=1, le=100)


# ============= 쿠폰 =============
class CouponCreate(BaseModel):
    course_id: Optional[int] = Field(None, gt=0)
    code: str = Field(..., min_length=3, max_length=50)
    name: str = Field(..., min_length=1, max_length=100)
    description: str
    discount_rate: Optional[int] = Field(None, ge=0, le=100)
    discount_amount: Optional[int] = Field(None, ge=0)
    valid_from: datetime
    valid_until: datetime
    max_usage: int = Field(default=0, ge=0)
    
    @field_validator('discount_rate', 'discount_amount')
    @classmethod
    def validate_discount(cls, v, info):
        # discount_rate와 discount_amount 중 하나는 반드시 있어야 함
        if info.field_name == 'discount_amount':
            discount_rate = info.data.get('discount_rate')
            if v is None and discount_rate is None:
                raise ValueError('할인율 또는 할인 금액 중 하나는 필수입니다')
        return v


class CouponUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = None
    valid_from: Optional[datetime] = None
    valid_until: Optional[datetime] = None
    max_usage: Optional[int] = Field(None, ge=0)
    is_active: Optional[bool] = None


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
    code: str = Field(..., min_length=3, max_length=50)
    course_id: int = Field(..., gt=0)


class CouponValidationResponse(BaseModel):
    is_valid: bool
    message: str
    coupon: Optional[CouponResponse] = None
    discount_amount: Optional[int] = None
    final_amount: Optional[int] = None


# ============= 환불 =============
class RefundCreate(BaseModel):
    payment_id: int = Field(..., gt=0)
    reason: str = Field(..., min_length=10, max_length=500)


class RefundUpdate(BaseModel):
    status: RefundStatus
    admin_note: Optional[str] = Field(None, max_length=500)


class RefundResponse(BaseModel):
    id: int
    payment_id: int
    user_id: int
    user_name: str
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


class RefundListParams(BaseModel):
    status: Optional[RefundStatus] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    keyword: Optional[str] = None
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=20, ge=1, le=100)


class RefundCheckResponse(BaseModel):
    can_refund: bool
    message: str
    payment_info: Optional[dict] = None
from pydantic import BaseModel, Field, field_validator, model_validator, field_serializer
from typing import List, Optional
from datetime import datetime, timezone, timedelta
from enum import Enum

# Enums
class PaymentMethod(str, Enum):
    CARD = "card"
    TRANSFER = "transfer"
    TOSS = "toss"

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
        ge=1,
        description="결제할 강의 ID", 
        example=1
    )
    payment_method: PaymentMethod = Field(
        ...,
        description="결제 방식 (card: 신용카드, transfer: 계좌이체, toss: 토스페이)",
        example="card"
    )

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
    order_id: str
    transaction_id: Optional[str] = None
    receipt_url: Optional[str]
    paid_at: Optional[datetime]
    created_at: datetime

    class Config:
        from_attributes = True

    @field_serializer('paid_at', 'created_at')
    def serialize_datetime(self, value: Optional[datetime]) -> Optional[str]:
        if not value:
            return None
        kst = timezone(timedelta(hours=9))
        utc = value.replace(tzinfo=timezone.utc) if value.tzinfo is None else value
        return utc.astimezone(kst).isoformat()

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
    order_id: str
    transaction_id: Optional[str] = None
    receipt_url: Optional[str]
    paid_at: Optional[datetime]
    created_at: datetime
    can_refund: bool = False
    refund_reason: Optional[str] = None

    class Config:
        from_attributes = True

    @field_serializer('paid_at', 'created_at')
    def serialize_datetime(self, value: Optional[datetime]) -> Optional[str]:
        if not value:
            return None
        kst = timezone(timedelta(hours=9))
        utc = value.replace(tzinfo=timezone.utc) if value.tzinfo is None else value
        return utc.astimezone(kst).isoformat()

class PaymentListParams(BaseModel):
    status: Optional[str] = Field(
        None,
        description="결제 상태로 필터링",
        example="completed"
    )
    payment_method: Optional[str] = Field(
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
    payment_key: str = Field(
        ...,
        min_length=1,
        max_length=200,
        description="토스 결제 키",
        example="tgen_20250101000000ABCDE"
    )
    order_id: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="주문 ID",
        example="ORDER_20250101_123456"
    )
    amount: int = Field(
        ...,
        ge=1,
        description="결제 금액",
        example=50000
    )

# ============= 환불 =============
class RefundCreate(BaseModel):
    payment_id: int = Field(
        ..., 
        ge=1,
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
    payment_date: datetime
    course_title: str
    progress_rate: float

    class Config:
        from_attributes = True

    @field_serializer('requested_at', 'processed_at', 'payment_date')
    def serialize_datetime(self, value: Optional[datetime]) -> Optional[str]:
        if not value:
            return None
        kst = timezone(timedelta(hours=9))
        utc = value.replace(tzinfo=timezone.utc) if value.tzinfo is None else value
        return utc.astimezone(kst).isoformat()

class RefundCheckResponse(BaseModel):
    can_refund: bool
    message: str
    payment_info: Optional[dict] = None

class PaymentPaginatedResponse(BaseModel):
    total: int
    page: int
    page_size: int
    total_pages: int
    items: List[PaymentResponse]
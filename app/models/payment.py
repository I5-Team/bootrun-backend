
from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum

from .base import Base

# ==================== Enums ====================

class PaymentMethod(str, enum.Enum):
    TOSS = "toss"

class PaymentStatus(str, enum.Enum):
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"
    REFUNDED = "refunded"

class RefundStatus(str, enum.Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"

# ==================== Models ====================

class Payment(Base):
    __tablename__ = "payments"

    # 기본 정보
    id = Column(Integer, primary_key=True, autoincrement=True, comment="결제 고유 ID")
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True, comment="사용자 ID")
    course_id = Column(Integer, ForeignKey("courses.id", ondelete="CASCADE"), nullable=False, index=True, comment="강의 ID")
    coupon_id = Column(Integer, ForeignKey("coupons.id"), nullable=True, comment="쿠폰 ID")
    
    # 결제 금액
    amount = Column(Integer, nullable=False, comment="원래 가격")
    discount_amount = Column(Integer, nullable=False, default=0, comment="할인 금액")
    final_amount = Column(Integer, nullable=False, comment="최종 결제 금액")
    
    # 결제 정보
    payment_method = Column(SQLEnum(PaymentMethod), nullable=False, comment="결제 방식")
    status = Column(SQLEnum(PaymentStatus), nullable=False, default=PaymentStatus.PENDING, comment="결제 상태")
    transaction_id = Column(String(100), unique=True, nullable=True, index=True, comment="PG사 거래 ID")
    receipt_url = Column(String(500), nullable=True, comment="영수증 URL")
    
    # 타임스탬프
    paid_at = Column(DateTime, nullable=True, comment="실제 결제 완료 시각")
    created_at = Column(DateTime, nullable=False, server_default=func.now(), comment="생성일시")

    # Relationships
    user = relationship("User", back_populates="payments")
    course = relationship("Course", back_populates="payments")
    coupon = relationship("Coupon", back_populates="payments")
    refund = relationship("Refund", back_populates="payment", uselist=False)

    def __repr__(self):
        return f"<Payment(id={self.id}, user_id={self.user_id}, amount={self.final_amount}, status='{self.status.value}')>"

class Coupon(Base):
    __tablename__ = "coupons"

    # 기본 정보
    id = Column(Integer, primary_key=True, autoincrement=True, comment="쿠폰 고유 ID")
    course_id = Column(Integer, ForeignKey("courses.id"), nullable=True, comment="강의 ID (NULL이면 전체 강의)")
    code = Column(String(50), unique=True, nullable=False, index=True, comment="쿠폰 코드")
    name = Column(String(100), nullable=False, comment="쿠폰 이름")
    description = Column(Text, nullable=False, comment="쿠폰 설명")
    
    # 할인 정보
    discount_rate = Column(Integer, nullable=True, comment="할인율 (%)")
    discount_amount = Column(Integer, nullable=True, comment="할인 금액 (원)")
    
    # 유효 기간
    valid_from = Column(DateTime, nullable=False, comment="유효 시작일")
    valid_until = Column(DateTime, nullable=False, comment="유효 종료일")
    
    # 사용 제한
    max_usage = Column(Integer, nullable=False, default=0, comment="최대 사용 인원 (0이면 무제한)")
    used_count = Column(Integer, nullable=False, default=0, comment="사용된 인원 수")
    is_active = Column(Boolean, nullable=False, default=True, comment="활성화 여부")
    
    # 타임스탬프
    created_at = Column(DateTime, nullable=False, server_default=func.now(), comment="생성일시")

    # Relationships
    course = relationship("Course", back_populates="coupons")
    payments = relationship("Payment", back_populates="coupon")

    def __repr__(self):
        return f"<Coupon(id={self.id}, code='{self.code}', used={self.used_count}/{self.max_usage})>"

class Refund(Base):
    __tablename__ = "refunds"

    # 기본 정보
    id = Column(Integer, primary_key=True, autoincrement=True, comment="환불 고유 ID")
    payment_id = Column(Integer, ForeignKey("payments.id", ondelete="CASCADE"), unique=True, nullable=False, index=True, comment="결제 ID")
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True, comment="사용자 ID")
    
    # 환불 정보
    amount = Column(Integer, nullable=False, comment="환불 금액")
    reason = Column(Text, nullable=False, comment="환불 사유")
    status = Column(SQLEnum(RefundStatus), nullable=False, default=RefundStatus.PENDING, comment="환불 상태")
    admin_note = Column(Text, nullable=True, comment="관리자 메모")
    
    # 타임스탬프
    requested_at = Column(DateTime, nullable=False, server_default=func.now(), comment="요청일시")
    processed_at = Column(DateTime, nullable=True, comment="처리 완료 시각")

    # Relationships
    payment = relationship("Payment", back_populates="refund")
    user = relationship("User", back_populates="refunds")

    def __repr__(self):
        return f"<Refund(id={self.id}, payment_id={self.payment_id}, status='{self.status.value}')>"
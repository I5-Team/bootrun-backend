
from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum

from .base import Base

# ==================== Enums ====================

class PaymentMethod(str, enum.Enum):
    CARD = "card"
    TRANSFER = "transfer"
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
    coupon_id = Column(Integer, nullable=True, comment="쿠폰 ID (미사용)")
    
    # 결제 금액
    amount = Column(Integer, nullable=False, comment="원래 가격")
    discount_amount = Column(Integer, nullable=False, default=0, comment="할인 금액")
    final_amount = Column(Integer, nullable=False, comment="최종 결제 금액")

    # 결제 정보
    payment_method = Column(SQLEnum(PaymentMethod, values_callable=lambda x: [e.value for e in x]), nullable=False, comment="결제 방식")
    status = Column(SQLEnum(PaymentStatus, values_callable=lambda x: [e.value for e in x]), nullable=False, default=PaymentStatus.PENDING.value, comment="결제 상태")
    order_id = Column(String(100), unique=True, nullable=True, index=True, comment="주문 ID (토스 연동용, 기존 데이터는 NULL)")
    payment_key = Column(String(200), nullable=True, comment="토스 결제 키")
    transaction_id = Column(String(100), unique=True, nullable=True, index=True, comment="PG사 거래 ID")
    receipt_url = Column(String(500), nullable=True, comment="영수증 URL")

    # 타임스탬프
    paid_at = Column(DateTime, nullable=True, comment="실제 결제 완료 시각")
    created_at = Column(DateTime, nullable=False, server_default=func.now(), comment="생성일시")

    # Relationships
    user = relationship("User", back_populates="payments")
    course = relationship("Course", back_populates="payments")
    refund = relationship("Refund", back_populates="payment", uselist=False)

    def __repr__(self):
        return f"<Payment(id={self.id}, user_id={self.user_id}, amount={self.final_amount}, status='{self.status}')>"

    def can_cancel(self) -> bool:
        """
        결제 취소 가능 여부 판단
        - 생성 후 1분 이내만 취소 가능
        """
        if self.status != PaymentStatus.COMPLETED.value:
            return False

        from datetime import timedelta, datetime as dt
        elapsed = dt.utcnow() - self.created_at
        return elapsed <= timedelta(minutes=1)

class Refund(Base):
    __tablename__ = "refunds"

    # 기본 정보
    id = Column(Integer, primary_key=True, autoincrement=True, comment="환불 고유 ID")
    payment_id = Column(Integer, ForeignKey("payments.id", ondelete="CASCADE"), unique=True, nullable=False, index=True, comment="결제 ID")
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True, comment="사용자 ID")
    
    # 환불 정보
    amount = Column(Integer, nullable=False, comment="환불 금액")
    reason = Column(Text, nullable=False, comment="환불 사유")
    status = Column(SQLEnum(RefundStatus, values_callable=lambda x: [e.value for e in x]), nullable=False, default=RefundStatus.PENDING.value, comment="환불 상태")
    admin_note = Column(Text, nullable=True, comment="관리자 메모")
    
    # 타임스탬프
    requested_at = Column(DateTime, nullable=False, server_default=func.now(), comment="요청일시")
    processed_at = Column(DateTime, nullable=True, comment="처리 완료 시각")

    # Relationships
    payment = relationship("Payment", back_populates="refund")
    user = relationship("User", back_populates="refunds")

    def __repr__(self):
        return f"<Refund(id={self.id}, payment_id={self.payment_id}, status='{self.status}')>"
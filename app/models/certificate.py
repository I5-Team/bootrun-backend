
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from .base import Base

class Certificate(Base):
    __tablename__ = "certificates"

    # 기본 정보
    id = Column(Integer, primary_key=True, autoincrement=True, comment="수료증 고유 ID")
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True, comment="사용자 ID")
    course_id = Column(Integer, ForeignKey("courses.id", ondelete="CASCADE"), nullable=False, index=True, comment="강의 ID")
    enrollment_id = Column(Integer, ForeignKey("enrollments.id", ondelete="CASCADE"), nullable=False, unique=True, index=True, comment="수강 등록 ID")
    
    # 수료증 정보
    certificate_number = Column(String(100), unique=True, nullable=False, index=True, comment="수료증 번호 (예: WNIV-2025-000001)")
    issued_at = Column(DateTime, nullable=False, server_default=func.now(), comment="발급일시")
    pdf_url = Column(String(500), nullable=True, comment="PDF 파일 URL")
    pdf_generated_at = Column(DateTime, nullable=True, comment="PDF 생성일시")

    # Relationships
    user = relationship("User", back_populates="certificates")
    course = relationship("Course", back_populates="certificates")
    enrollment = relationship("Enrollment", back_populates="certificates")

    def __repr__(self):
        return f"<Certificate(id={self.id}, number='{self.certificate_number}', user_id={self.user_id})>"
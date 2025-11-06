"""
Enrollments, Progresses 테이블 모델
"""

from sqlalchemy import Column, Integer, Float, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from .base import Base


class Enrollment(Base):
    """수강 등록 테이블"""
    __tablename__ = "enrollments"

    # 기본 정보
    id = Column(Integer, primary_key=True, autoincrement=True, comment="수강 등록 고유 ID")
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True, comment="사용자 ID")
    course_id = Column(Integer, ForeignKey("courses.id", ondelete="CASCADE"), nullable=False, index=True, comment="강의 ID")
    
    # 수강 정보
    enrolled_at = Column(DateTime, nullable=False, server_default=func.now(), comment="등록일시")
    expires_at = Column(DateTime, nullable=False, comment="만료일시 (등록일 + 2년)")
    is_active = Column(Boolean, nullable=False, default=True, comment="활성화 여부")
    progress_rate = Column(Float, nullable=False, default=0.0, comment="전체 진행률 0~100")
    
    # 타임스탬프
    updated_at = Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now(), comment="수정일시")

    # Relationships
    user = relationship("User", back_populates="enrollments")
    course = relationship("Course", back_populates="enrollments")
    certificates = relationship("Certificate", back_populates="enrollment", uselist=False)

    def __repr__(self):
        return f"<Enrollment(id={self.id}, user_id={self.user_id}, course_id={self.course_id}, progress={self.progress_rate}%)>"


class Progress(Base):
    """학습 진행 테이블"""
    __tablename__ = "progresses"

    # 기본 정보
    id = Column(Integer, primary_key=True, autoincrement=True, comment="진행 상황 고유 ID")
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True, comment="사용자 ID")
    lecture_id = Column(Integer, ForeignKey("lectures.id", ondelete="CASCADE"), nullable=False, index=True, comment="강의 ID")
    
    # 진행 정보
    watched_seconds = Column(Integer, nullable=False, default=0, comment="총 시청 시간 (초)")
    last_position = Column(Integer, nullable=False, default=0, comment="마지막 시청 위치 (초)")
    is_completed = Column(Boolean, nullable=False, default=False, comment="완료 여부")
    
    # 타임스탬프
    last_watched_at = Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now(), comment="마지막 시청 일시")
    completed_at = Column(DateTime, nullable=True, comment="완료 일시")
    created_at = Column(DateTime, nullable=False, server_default=func.now(), comment="생성일시")
    updated_at = Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now(), comment="수정일시")

    # Relationships
    user = relationship("User", back_populates="progresses")
    lecture = relationship("Lecture", back_populates="progresses")

    def __repr__(self):
        return f"<Progress(id={self.id}, user_id={self.user_id}, lecture_id={self.lecture_id}, completed={self.is_completed})>"
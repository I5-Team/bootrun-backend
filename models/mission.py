"""
Missions, MissionSubmissions 테이블 모델
"""

from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey, Enum as SQLEnum
from sqlalchemy.dialects.mysql import JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum

from .base import Base


# ==================== Enums ====================

class MissionType(str, enum.Enum):
    """미션 유형"""
    MIDTERM = "midterm"
    FINAL = "final"


class QuestionType(str, enum.Enum):
    """문제 유형"""
    MULTIPLE_CHOICE = "multiple_choice"
    CODE = "code"


# ==================== Models ====================

class Mission(Base):
    """미션 테이블"""
    __tablename__ = "missions"

    # 기본 정보
    id = Column(Integer, primary_key=True, autoincrement=True, comment="미션 고유 ID")
    course_id = Column(Integer, ForeignKey("courses.id", ondelete="CASCADE"), nullable=False, index=True, comment="강의 ID")
    title = Column(String(200), nullable=False, comment="미션 제목")
    description = Column(Text, nullable=False, comment="미션 설명")
    mission_type = Column(SQLEnum(MissionType), nullable=False, comment="미션 유형")
    question_type = Column(SQLEnum(QuestionType), nullable=False, comment="문제 유형")
    
    # 문제 데이터
    question_data = Column(JSON, nullable=False, comment="문제 데이터 (JSON 형태)")
    answer_data = Column(JSON, nullable=False, comment="정답 데이터 (JSON 형태)")
    
    # 점수 설정
    max_score = Column(Integer, nullable=False, default=100, comment="최대 점수")
    passing_score = Column(Integer, nullable=False, default=60, comment="통과 기준 점수")
    max_attempts = Column(Integer, nullable=False, default=3, comment="최대 제출 횟수")
    
    # 타임스탬프
    created_at = Column(DateTime, nullable=False, server_default=func.now(), comment="생성일시")
    updated_at = Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now(), comment="수정일시")

    # Relationships
    course = relationship("Course", back_populates="missions")
    submissions = relationship("MissionSubmission", back_populates="mission", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Mission(id={self.id}, title='{self.title}', type='{self.mission_type.value}')>"


class MissionSubmission(Base):
    """미션 제출 테이블"""
    __tablename__ = "mission_submissions"

    # 기본 정보
    id = Column(Integer, primary_key=True, autoincrement=True, comment="제출 고유 ID")
    mission_id = Column(Integer, ForeignKey("missions.id", ondelete="CASCADE"), nullable=False, index=True, comment="미션 ID")
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True, comment="사용자 ID")
    
    # 제출 정보
    answer = Column(JSON, nullable=False, comment="제출 답안 (JSON 형태)")
    score = Column(Integer, nullable=False, comment="획득 점수")
    is_passed = Column(Boolean, nullable=False, default=False, comment="통과 여부")
    feedback = Column(Text, nullable=False, comment="피드백")
    execution_result = Column(JSON, nullable=True, comment="실행 결과 (코드 제출형, JSON 형태)")
    attempt_number = Column(Integer, nullable=False, default=1, comment="시도 횟수")
    
    # 타임스탬프
    submitted_at = Column(DateTime, nullable=False, server_default=func.now(), comment="제출일시")

    # Relationships
    mission = relationship("Mission", back_populates="submissions")
    user = relationship("User", back_populates="mission_submissions")

    def __repr__(self):
        return f"<MissionSubmission(id={self.id}, mission_id={self.mission_id}, score={self.score}, passed={self.is_passed})>"
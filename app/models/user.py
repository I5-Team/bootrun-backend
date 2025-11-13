from sqlalchemy import Column, Integer, String, Date, Boolean, DateTime, Enum as SQLEnum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime
import enum

from .base import Base

class UserRole(str, enum.Enum):
    STUDENT = "student"
    ADMIN = "admin"

class Gender(str, enum.Enum):
    MALE = "male"
    FEMALE = "female"
    OTHER = "other"

class SocialProvider(str, enum.Enum):
    EMAIL = "email"
    GOOGLE = "google"
    GITHUB = "github"

class User(Base):
    __tablename__ = "users"

    # 기본 정보
    id = Column(Integer, primary_key=True, autoincrement=True, comment="사용자 고유 ID")
    email = Column(String(255), unique=True, nullable=False, index=True, comment="이메일")
    password_hash = Column(String(255), nullable=True, comment="비밀번호 해시 (소셜 로그인 시 NULL)")
    nickname = Column(String(18), unique=True, nullable=False, index=True, comment="닉네임 (2~18자)")
    gender = Column(SQLEnum(Gender, values_callable=lambda obj: [e.value for e in obj]), nullable=True, comment="성별")
    birth_date = Column(Date, nullable=True, comment="생년월일")
    profile_image = Column(String(500), nullable=True, comment="프로필 이미지 URL")

    # 역할 및 권한
    role = Column(SQLEnum(UserRole, values_callable=lambda obj: [e.value for e in obj]), nullable=False, default=UserRole.STUDENT, comment="사용자 역할")

    # 소셜 로그인
    social_provider = Column(SQLEnum(SocialProvider, values_callable=lambda obj: [e.value for e in obj]), nullable=False, default=SocialProvider.EMAIL, comment="소셜 로그인 제공자")
    social_id = Column(String(255), nullable=True, comment="소셜 로그인 고유 ID")
    
    # 계정 상태
    is_active = Column(Boolean, nullable=False, default=True, comment="계정 활성화 여부")
    is_email_verified = Column(Boolean, nullable=False, default=False, comment="이메일 인증 여부")
    
    # 타임스탬프
    created_at = Column(DateTime, nullable=False, server_default=func.now(), comment="가입일시")
    updated_at = Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now(), comment="수정일시")
    last_login = Column(DateTime, nullable=True, comment="마지막 로그인 일시")

    # Relationships
    enrollments = relationship("Enrollment", back_populates="user", cascade="all, delete-orphan")
    payments = relationship("Payment", back_populates="user", cascade="all, delete-orphan")
    progresses = relationship("Progress", back_populates="user", cascade="all, delete-orphan")
    course_questions = relationship("CourseQuestion", foreign_keys="CourseQuestion.user_id", back_populates="user", cascade="all, delete-orphan")
    deleted_questions = relationship("CourseQuestion", foreign_keys="CourseQuestion.deleted_by", back_populates="deleter")
    comments = relationship("Comment", foreign_keys="Comment.user_id", back_populates="user", cascade="all, delete-orphan")
    deleted_comments = relationship("Comment", foreign_keys="Comment.deleted_by", back_populates="deleter")
    mission_submissions = relationship("MissionSubmission", back_populates="user", cascade="all, delete-orphan")
    certificates = relationship("Certificate", back_populates="user", cascade="all, delete-orphan")
    refunds = relationship("Refund", back_populates="user", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<User(id={self.id}, email='{self.email}', nickname='{self.nickname}')>"
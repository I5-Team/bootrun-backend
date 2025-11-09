
from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum

from .base import Base

# ==================== Enums ====================

class CategoryType(str, enum.Enum):
    FRONTEND = "frontend"
    BACKEND = "backend"
    DATA_ANALYSIS = "data_analysis"
    AI = "ai"
    DESIGN = "design"
    OTHER = "other"

class CourseType(str, enum.Enum):
    VOD = "vod"
    BOOST_COMMUNITY = "boost_community"
    KDC = "kdc"

class Difficulty(str, enum.Enum):
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"

class PriceType(str, enum.Enum):
    FREE = "free"
    PAID = "paid"
    NATIONAL_SUPPORT = "national_support"

class VideoType(str, enum.Enum):
    VOD = "vod"
    YOUTUBE = "youtube"

# ==================== Models ====================

class Course(Base):
    __tablename__ = "courses"

    # 기본 정보
    id = Column(Integer, primary_key=True, autoincrement=True, comment="강의 고유 ID")
    category_type = Column(SQLEnum(CategoryType), nullable=False, comment="카테고리 유형")
    course_type = Column(SQLEnum(CourseType), nullable=False, default=CourseType.VOD, comment="강의 유형")
    title = Column(String(200), nullable=False, index=True, comment="강의 제목")
    description = Column(Text, nullable=False, comment="강의 설명")
    thumbnail_url = Column(String(500), nullable=False, comment="썸네일 이미지 URL")
    
    # 강사 정보
    instructor_name = Column(String(100), nullable=False, comment="강사명")
    instructor_bio = Column(Text, nullable=False, comment="강사 소개")
    instructor_image = Column(String(500), nullable=False, comment="강사 프로필 이미지 URL")
    
    # 강의 속성
    difficulty = Column(SQLEnum(Difficulty), nullable=False, comment="난이도")
    price_type = Column(SQLEnum(PriceType), nullable=False, default=PriceType.PAID, comment="가격 유형")
    price = Column(Integer, nullable=False, default=50000, comment="실제 가격 (원)")
    total_duration = Column(Integer, nullable=False, default=0, comment="전체 강의 시간 (초)")
    
    # 추가 정보
    faq = Column(Text, nullable=True, comment="자주 묻는 질문 (JSON 형태)")
    is_published = Column(Boolean, nullable=False, default=False, comment="공개 여부")
    
    # 타임스탬프
    created_at = Column(DateTime, nullable=False, server_default=func.now(), comment="생성일시")
    updated_at = Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now(), comment="수정일시")

    # Relationships
    chapters = relationship("Chapter", back_populates="course", cascade="all, delete-orphan")
    enrollments = relationship("Enrollment", back_populates="course", cascade="all, delete-orphan")
    missions = relationship("Mission", back_populates="course", cascade="all, delete-orphan")
    course_questions = relationship("CourseQuestion", back_populates="course", cascade="all, delete-orphan")
    certificates = relationship("Certificate", back_populates="course", cascade="all, delete-orphan")
    payments = relationship("Payment", back_populates="course", cascade="all, delete-orphan")
    coupons = relationship("Coupon", back_populates="course")

    def __repr__(self):
        return f"<Course(id={self.id}, title='{self.title}', category='{self.category_type.value}')>"

class Chapter(Base):
    __tablename__ = "chapters"

    # 기본 정보
    id = Column(Integer, primary_key=True, autoincrement=True, comment="챕터 고유 ID")
    course_id = Column(Integer, ForeignKey("courses.id", ondelete="CASCADE"), nullable=False, index=True, comment="강의 ID")
    title = Column(String(200), nullable=False, comment="챕터 제목")
    description = Column(Text, nullable=True, comment="챕터 설명")
    order_number = Column(Integer, nullable=False, comment="챕터 순서")
    
    # 타임스탬프
    created_at = Column(DateTime, nullable=False, server_default=func.now(), comment="생성일시")
    updated_at = Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now(), comment="수정일시")

    # Relationships
    course = relationship("Course", back_populates="chapters")
    lectures = relationship("Lecture", back_populates="chapter", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Chapter(id={self.id}, title='{self.title}', order={self.order_number})>"

class Lecture(Base):
    __tablename__ = "lectures"

    # 기본 정보
    id = Column(Integer, primary_key=True, autoincrement=True, comment="강의 영상 고유 ID")
    chapter_id = Column(Integer, ForeignKey("chapters.id", ondelete="CASCADE"), nullable=False, index=True, comment="챕터 ID")
    title = Column(String(200), nullable=False, comment="강의 제목")
    description = Column(Text, nullable=True, comment="강의 설명")
    video_url = Column(String(500), nullable=False, comment="동영상 URL")
    video_type = Column(SQLEnum(VideoType), nullable=False, comment="동영상 타입")
    duration_seconds = Column(Integer, nullable=False, default=0, comment="재생 시간 (초)")
    order_number = Column(Integer, nullable=False, comment="강의 순서")
    
    # 타임스탬프
    created_at = Column(DateTime, nullable=False, server_default=func.now(), comment="생성일시")
    updated_at = Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now(), comment="수정일시")

    # Relationships
    chapter = relationship("Chapter", back_populates="lectures")
    progresses = relationship("Progress", back_populates="lecture", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Lecture(id={self.id}, title='{self.title}', order={self.order_number})>"
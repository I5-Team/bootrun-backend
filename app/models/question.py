
from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from .base import Base

class CourseQuestion(Base):
    __tablename__ = "course_questions"

    # 기본 정보
    id = Column(Integer, primary_key=True, autoincrement=True, comment="질문 고유 ID")
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True, comment="작성자 ID")
    course_id = Column(Integer, ForeignKey("courses.id", ondelete="CASCADE"), nullable=False, index=True, comment="강의 ID")
    
    # 질문 내용
    title = Column(String(200), nullable=False, comment="질문 제목")
    content = Column(Text, nullable=False, comment="질문 내용")
    
    # 상태 정보
    view_count = Column(Integer, nullable=False, default=0, comment="조회수")
    is_answered = Column(Boolean, nullable=False, default=False, comment="답변 완료 여부")
    
    # 소프트 삭제
    is_deleted = Column(Boolean, nullable=False, default=False, comment="소프트 삭제 여부")
    deleted_at = Column(DateTime, nullable=True, comment="삭제 일시")
    deleted_by = Column(Integer, ForeignKey("users.id"), nullable=True, comment="삭제한 사용자 ID")
    
    # 타임스탬프
    created_at = Column(DateTime, nullable=False, server_default=func.now(), comment="작성일시")
    updated_at = Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now(), comment="수정일시")

    # Relationships
    user = relationship("User", foreign_keys=[user_id], back_populates="course_questions")
    course = relationship("Course", back_populates="course_questions")
    comments = relationship("Comment", back_populates="question", cascade="all, delete-orphan")
    deleter = relationship("User", foreign_keys=[deleted_by], back_populates="deleted_questions")

    def __repr__(self):
        return f"<CourseQuestion(id={self.id}, title='{self.title}', answered={self.is_answered})>"

class Comment(Base):
    __tablename__ = "comments"

    # 기본 정보
    id = Column(Integer, primary_key=True, autoincrement=True, comment="댓글 고유 ID")
    question_id = Column(Integer, ForeignKey("course_questions.id", ondelete="CASCADE"), nullable=False, index=True, comment="질문 ID")
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True, comment="작성자 ID")
    parent_id = Column(Integer, ForeignKey("comments.id"), nullable=True, comment="부모 댓글 ID (대댓글용)")
    
    # 댓글 내용
    content = Column(Text, nullable=False, comment="댓글 내용")
    is_instructor_answer = Column(Boolean, nullable=False, default=False, comment="강사 답변 여부")
    
    # 소프트 삭제
    is_deleted = Column(Boolean, nullable=False, default=False, comment="소프트 삭제 여부")
    deleted_at = Column(DateTime, nullable=True, comment="삭제 일시")
    deleted_by = Column(Integer, ForeignKey("users.id"), nullable=True, comment="삭제한 사용자 ID")
    
    # 타임스탬프
    created_at = Column(DateTime, nullable=False, server_default=func.now(), comment="작성일시")
    updated_at = Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now(), comment="수정일시")

    # Relationships
    question = relationship("CourseQuestion", back_populates="comments")
    user = relationship("User", foreign_keys=[user_id], back_populates="comments")
    parent = relationship("Comment", remote_side=[id], back_populates="replies")
    replies = relationship("Comment", back_populates="parent", cascade="all, delete-orphan")
    deleter = relationship("User", foreign_keys=[deleted_by], back_populates="deleted_comments")

    def __repr__(self):
        return f"<Comment(id={self.id}, question_id={self.question_id}, instructor_answer={self.is_instructor_answer})>"
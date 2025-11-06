"""
SQLAlchemy Base 클래스
"""

from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """모든 모델의 기본 클래스"""
    pass
"""
Models package for the application.
Import order is crucial to avoid circular dependencies.
"""

# Base must be imported first
from .base import Base

# Import models in dependency order
from .user import User, UserRole, Gender, SocialProvider
from .course import Course, Chapter, Lecture, CategoryType, CourseType, Difficulty, PriceType, VideoType
from .progress import Enrollment, Progress
from .payment import Payment, Refund, PaymentMethod, PaymentStatus, RefundStatus

__all__ = [
    # Base
    "Base",

    # User models and enums
    "User",
    "UserRole",
    "Gender",
    "SocialProvider",

    # Course models and enums
    "Course",
    "Chapter",
    "Lecture",
    "CategoryType",
    "CourseType",
    "Difficulty",
    "PriceType",
    "VideoType",

    # Progress models
    "Enrollment",
    "Progress",

    # Payment models and enums
    "Payment",
    "Refund",
    "PaymentMethod",
    "PaymentStatus",
    "RefundStatus",
]

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
from .mission import Mission, MissionSubmission, MissionType, QuestionType
from .question import CourseQuestion, Comment
from .certificate import Certificate
from .payment import Payment, Coupon, Refund, PaymentMethod, PaymentStatus, RefundStatus

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

    # Mission models and enums
    "Mission",
    "MissionSubmission",
    "MissionType",
    "QuestionType",

    # Question models
    "CourseQuestion",
    "Comment",

    # Certificate model
    "Certificate",

    # Payment models and enums
    "Payment",
    "Coupon",
    "Refund",
    "PaymentMethod",
    "PaymentStatus",
    "RefundStatus",
]

"""
Exceptions Package
예외 처리 패키지

핵심 클래스와 함수만 export하여 순환 임포트를 방지합니다.
개별 예외 클래스는 각 라우터에서 직접 import하여 사용하세요.

사용 예시:
    from exceptions import BaseAPIException, register_exception_handlers
    from exceptions.base import LoginFailedError, CourseNotFoundError
"""

from .base import BaseAPIException
from .handlers import register_exception_handlers

__all__ = [
    "BaseAPIException",
    "register_exception_handlers",
]
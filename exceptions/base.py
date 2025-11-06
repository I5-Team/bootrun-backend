"""
Base Exception Classes and Common Response Templates
커스텀 예외 클래스와 공통 에러 응답 템플릿 정의
"""

from fastapi import status
from typing import Optional


# ============= 커스텀 예외 클래스 =============

class BaseAPIException(Exception):
    """
    모든 커스텀 예외의 기본 클래스
    
    Attributes:
        status_code: HTTP 상태 코드
        detail: 에러 상세 메시지 (사용자에게 표시)
        error_code: 에러 코드 (UPPER_SNAKE_CASE, 로그/추적용)
    """
    
    def __init__(
        self, 
        detail: str,
        status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR,
        error_code: Optional[str] = None
    ) -> None:
        self.status_code = status_code
        self.detail = detail
        # error_code를 UPPER_SNAKE_CASE로 자동 변환
        if error_code:
            self.error_code = error_code
        else:
            # 클래스명을 UPPER_SNAKE_CASE로 변환
            # 예: LoginFailedError -> LOGIN_FAILED
            class_name = self.__class__.__name__.replace('Error', '')
            self.error_code = ''.join(
                ['_' + c.upper() if c.isupper() and i > 0 else c.upper() 
                 for i, c in enumerate(class_name)]
            ).lstrip('_')
        super().__init__(self.detail)


# ============= HTTP 예외 클래스 (4xx, 5xx) =============

class BadRequestError(BaseAPIException):
    """400 - 잘못된 요청"""
    
    def __init__(self, detail: str = '잘못된 요청입니다') -> None:
        super().__init__(
            detail=detail,
            status_code=status.HTTP_400_BAD_REQUEST
        )


class UnauthorizedError(BaseAPIException):
    """401 - 인증 실패"""
    
    def __init__(self, detail: str = '인증이 필요합니다') -> None:
        super().__init__(
            detail=detail,
            status_code=status.HTTP_401_UNAUTHORIZED
        )


class ForbiddenError(BaseAPIException):
    """403 - 권한 없음"""
    
    def __init__(self, detail: str = '접근 권한이 없습니다') -> None:
        super().__init__(
            detail=detail,
            status_code=status.HTTP_403_FORBIDDEN
        )


class NotFoundError(BaseAPIException):
    """404 - 리소스를 찾을 수 없음"""
    
    def __init__(
        self,
        detail: str = '요청한 리소스를 찾을 수 없습니다'
    ) -> None:
        super().__init__(
            detail=detail,
            status_code=status.HTTP_404_NOT_FOUND
        )


class ConflictError(BaseAPIException):
    """409 - 리소스 충돌"""
    
    def __init__(
        self,
        detail: str = '리소스 충돌이 발생했습니다'
    ) -> None:
        super().__init__(
            detail=detail,
            status_code=status.HTTP_409_CONFLICT
        )


class GoneError(BaseAPIException):
    """410 - 리소스가 영구적으로 사용 불가"""
    
    def __init__(
        self,
        detail: str = '리소스를 더 이상 사용할 수 없습니다'
    ) -> None:
        super().__init__(
            detail=detail,
            status_code=status.HTTP_410_GONE
        )


class UnprocessableEntityError(BaseAPIException):
    """422 - 유효성 검사 실패"""
    
    def __init__(
        self,
        detail: str = '입력값이 올바르지 않습니다'
    ) -> None:
        super().__init__(
            detail=detail,
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY
        )


class InternalServerError(BaseAPIException):
    """500 - 서버 내부 오류"""
    
    def __init__(
        self,
        detail: str = '서버 오류가 발생했습니다'
    ) -> None:
        super().__init__(
            detail=detail,
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


# ============= 도메인별 커스텀 예외 =============

# 인증/회원
class LoginFailedError(UnauthorizedError):
    """로그인 실패"""
    
    def __init__(
        self,
        detail: str = '이메일 또는 비밀번호가 일치하지 않습니다'
    ) -> None:
        super().__init__(detail=detail)


class EmailAlreadyExistsError(ConflictError):
    """이메일 중복"""
    
    def __init__(
        self,
        detail: str = '이미 존재하는 이메일입니다'
    ) -> None:
        super().__init__(detail=detail)


class VerificationCodeInvalidError(BadRequestError):
    """인증 코드 오류"""
    
    def __init__(
        self,
        detail: str = '인증 코드가 올바르지 않습니다'
    ) -> None:
        super().__init__(detail=detail)


class TokenExpiredError(UnauthorizedError):
    """토큰 만료"""
    
    def __init__(self, detail: str = '토큰이 만료되었습니다') -> None:
        super().__init__(detail=detail)


# 강의
class CourseNotFoundError(NotFoundError):
    """강의를 찾을 수 없음"""
    
    def __init__(
        self,
        detail: str = '강의를 찾을 수 없습니다'
    ) -> None:
        super().__init__(detail=detail)


class ChapterNotFoundError(NotFoundError):
    """챕터를 찾을 수 없음"""
    
    def __init__(
        self,
        detail: str = '챕터를 찾을 수 없습니다'
    ) -> None:
        super().__init__(detail=detail)


class LectureNotFoundError(NotFoundError):
    """강의 영상을 찾을 수 없음"""
    
    def __init__(
        self,
        detail: str = '강의 영상을 찾을 수 없습니다'
    ) -> None:
        super().__init__(detail=detail)


# 수강 등록
class AlreadyEnrolledError(ConflictError):
    """이미 등록한 강의"""
    
    def __init__(
        self,
        detail: str = '이미 등록한 강의입니다'
    ) -> None:
        super().__init__(detail=detail)


class EnrollmentRequiredError(ForbiddenError):
    """수강 등록 필요"""
    
    def __init__(
        self,
        detail: str = '수강 등록이 필요합니다'
    ) -> None:
        super().__init__(detail=detail)


class EnrollmentExpiredError(GoneError):
    """수강 기간 만료"""
    
    def __init__(
        self,
        detail: str = '수강 기간이 만료되었습니다'
    ) -> None:
        super().__init__(detail=detail)


# 미션
class MaxAttemptsExceededError(BadRequestError):
    """최대 제출 횟수 초과"""
    
    def __init__(
        self,
        detail: str = '최대 제출 횟수를 초과했습니다'
    ) -> None:
        super().__init__(detail=detail)


class MissionNotFoundError(NotFoundError):
    """미션을 찾을 수 없음"""
    
    def __init__(
        self,
        detail: str = '미션을 찾을 수 없습니다'
    ) -> None:
        super().__init__(detail=detail)


# 결제
class AlreadyPaidError(ConflictError):
    """이미 결제한 강의"""
    
    def __init__(
        self,
        detail: str = '이미 결제한 강의입니다'
    ) -> None:
        super().__init__(detail=detail)


class PaymentNotFoundError(NotFoundError):
    """결제 내역을 찾을 수 없음"""
    
    def __init__(
        self,
        detail: str = '결제 내역을 찾을 수 없습니다'
    ) -> None:
        super().__init__(detail=detail)


class RefundNotAllowedError(BadRequestError):
    """환불 불가"""
    
    def __init__(
        self,
        detail: str = '환불 가능 기간이 지났습니다'
    ) -> None:
        super().__init__(detail=detail)


class CouponNotFoundError(NotFoundError):
    """쿠폰을 찾을 수 없음"""
    
    def __init__(
        self,
        detail: str = '쿠폰을 찾을 수 없습니다'
    ) -> None:
        super().__init__(detail=detail)


class CouponExpiredError(BadRequestError):
    """쿠폰 만료"""
    
    def __init__(self, detail: str = '쿠폰이 만료되었습니다') -> None:
        super().__init__(detail=detail)


# 수료증
class CertificateNotFoundError(NotFoundError):
    """수료증을 찾을 수 없음"""
    
    def __init__(
        self,
        detail: str = '수료증을 찾을 수 없습니다'
    ) -> None:
        super().__init__(detail=detail)


class CompletionRequirementsNotMetError(BadRequestError):
    """수료 조건 미충족"""
    
    def __init__(
        self,
        detail: str = '수료 조건을 충족하지 않았습니다'
    ) -> None:
        super().__init__(detail=detail)


# Q&A
class QuestionNotFoundError(NotFoundError):
    """질문을 찾을 수 없음"""
    
    def __init__(
        self,
        detail: str = '질문을 찾을 수 없습니다'
    ) -> None:
        super().__init__(detail=detail)


class OnlyAuthorCanModifyError(ForbiddenError):
    """작성자만 수정 가능"""
    
    def __init__(
        self,
        detail: str = '본인이 작성한 글만 수정할 수 있습니다'
    ) -> None:
        super().__init__(detail=detail)


# ============= 공통 에러 응답 템플릿 팩토리 =============

def make_error_response(
    error_code: str, 
    detail: str, 
    description: Optional[str] = None
) -> dict:
    """
    에러 응답 템플릿을 생성하는 팩토리 함수
    
    Args:
        error_code: 에러 코드 (UPPER_SNAKE_CASE)
        detail: 에러 상세 메시지
        description: OpenAPI 문서 설명 (선택)
    
    Returns:
        FastAPI responses 딕셔너리
    """
    return {
        'description': description or detail,
        'content': {
            'application/json': {
                'example': {
                    'error': error_code,
                    'detail': detail
                }
            }
        }
    }


# ============= 공통 에러 응답 템플릿 =============

COMMON_400 = make_error_response(
    'BAD_REQUEST',
    '잘못된 요청입니다'
)

COMMON_401 = make_error_response(
    'UNAUTHORIZED',
    '인증이 필요합니다'
)

COMMON_403 = make_error_response(
    'FORBIDDEN',
    '접근 권한이 없습니다'
)

COMMON_404 = make_error_response(
    'NOT_FOUND',
    '요청한 리소스를 찾을 수 없습니다'
)

COMMON_409 = make_error_response(
    'CONFLICT',
    '리소스 충돌이 발생했습니다'
)

COMMON_410 = make_error_response(
    'GONE',
    '리소스를 더 이상 사용할 수 없습니다'
)

COMMON_422 = {
    'description': '유효성 검사 실패',
    'content': {
        'application/json': {
            'example': {
                'error': 'VALIDATION_ERROR',
                'detail': '입력값이 올바르지 않습니다',
                'errors': [
                    {
                        'loc': ['body', 'email'],
                        'msg': '유효한 이메일 주소를 입력하세요',
                        'type': 'value_error.email'
                    }
                ],
                'path': '/api/users/register'  
            }
        }
    }
}

COMMON_500 = make_error_response(
    'INTERNAL_SERVER_ERROR',
    '서버 오류가 발생했습니다'
)


# ============= 도메인별 에러 응답 세트 =============

# 인증이 필요한 엔드포인트용
AUTH_RESPONSES = {
    401: COMMON_401,
    403: COMMON_403,
    422: COMMON_422,
    500: COMMON_500,
}

# 리소스 조회 엔드포인트용
READ_RESPONSES = {
    404: COMMON_404,
    422: COMMON_422,
    500: COMMON_500,
}

# 리소스 생성 엔드포인트용
CREATE_RESPONSES = {
    400: COMMON_400,
    401: COMMON_401,
    409: COMMON_409,
    422: COMMON_422,
    500: COMMON_500,
}

# 리소스 수정/삭제 엔드포인트용
MODIFY_RESPONSES = {
    400: COMMON_400,
    401: COMMON_401,
    403: COMMON_403,
    404: COMMON_404,
    422: COMMON_422,
    500: COMMON_500,
}

# 관리자 전용 엔드포인트용
ADMIN_RESPONSES = {
    401: COMMON_401,
    403: COMMON_403,
    422: COMMON_422,
    500: COMMON_500,
}
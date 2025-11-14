
from fastapi import status
from typing import Optional
import re

# ============= 커스텀 예외 기본 클래스 =============

class BaseAPIException(Exception):
    
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
            # CamelCase를 UPPER_SNAKE_CASE로 변환
            self.error_code = re.sub(r'(?<!^)(?=[A-Z])', '_', class_name).upper()
        super().__init__(self.detail)

# ============= HTTP 예외 클래스 (4xx, 5xx) =============

class BadRequestError(BaseAPIException):
    
    def __init__(self, detail: str = '잘못된 요청입니다') -> None:
        super().__init__(
            detail=detail,
            status_code=status.HTTP_400_BAD_REQUEST
        )

class UnauthorizedError(BaseAPIException):
    
    def __init__(self, detail: str = '인증이 필요합니다') -> None:
        super().__init__(
            detail=detail,
            status_code=status.HTTP_401_UNAUTHORIZED
        )

class ForbiddenError(BaseAPIException):
    
    def __init__(self, detail: str = '접근 권한이 없습니다') -> None:
        super().__init__(
            detail=detail,
            status_code=status.HTTP_403_FORBIDDEN
        )

class NotFoundError(BaseAPIException):
    
    def __init__(
        self,
        detail: str = '요청한 리소스를 찾을 수 없습니다'
    ) -> None:
        super().__init__(
            detail=detail,
            status_code=status.HTTP_404_NOT_FOUND
        )

class ConflictError(BaseAPIException):
    
    def __init__(
        self,
        detail: str = '리소스 충돌이 발생했습니다'
    ) -> None:
        super().__init__(
            detail=detail,
            status_code=status.HTTP_409_CONFLICT
        )

class GoneError(BaseAPIException):
    
    def __init__(
        self,
        detail: str = '리소스를 더 이상 사용할 수 없습니다'
    ) -> None:
        super().__init__(
            detail=detail,
            status_code=status.HTTP_410_GONE
        )

class UnprocessableEntityError(BaseAPIException):
    
    def __init__(
        self,
        detail: str = '입력값이 올바르지 않습니다'
    ) -> None:
        super().__init__(
            detail=detail,
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY
        )

class InternalServerError(BaseAPIException):
    
    def __init__(
        self,
        detail: str = '서버 오류가 발생했습니다'
    ) -> None:
        super().__init__(
            detail=detail,
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

# ============= 도메인별 커스텀 예외 (HTTP 예외 확장) =============

# 인증/회원 도메인
class LoginFailedError(UnauthorizedError):
    
    def __init__(
        self,
        detail: str = '이메일 또는 비밀번호가 일치하지 않습니다'
    ) -> None:
        super().__init__(detail=detail)

class EmailAlreadyExistsError(ConflictError):
    
    def __init__(
        self,
        detail: str = '이미 존재하는 이메일입니다'
    ) -> None:
        super().__init__(detail=detail)

class VerificationCodeInvalidError(BadRequestError):
    
    def __init__(
        self,
        detail: str = '인증 코드가 올바르지 않습니다'
    ) -> None:
        super().__init__(detail=detail)

class TokenExpiredError(UnauthorizedError):

    def __init__(self, detail: str = '토큰이 만료되었습니다') -> None:
        super().__init__(detail=detail)

# 강의 도메인
class CourseNotFoundError(NotFoundError):
    
    def __init__(
        self,
        detail: str = '강의를 찾을 수 없습니다'
    ) -> None:
        super().__init__(detail=detail)

class ChapterNotFoundError(NotFoundError):
    
    def __init__(
        self,
        detail: str = '챕터를 찾을 수 없습니다'
    ) -> None:
        super().__init__(detail=detail)

class LectureNotFoundError(NotFoundError):

    def __init__(
        self,
        detail: str = '강의 영상을 찾을 수 없습니다'
    ) -> None:
        super().__init__(detail=detail)

# 수강 등록 도메인
class AlreadyEnrolledError(ConflictError):

    def __init__(
        self,
        detail: str = '이미 등록한 강의입니다'
    ) -> None:
        super().__init__(detail=detail)

class EnrollmentAlreadyExistsError(ConflictError):

    def __init__(
        self,
        detail: str = '이미 수강 등록된 강의입니다'
    ) -> None:
        super().__init__(detail=detail)

class EnrollmentNotFoundError(NotFoundError):

    def __init__(
        self,
        detail: str = '수강 등록 정보를 찾을 수 없습니다'
    ) -> None:
        super().__init__(detail=detail)

class EnrollmentRequiredError(ForbiddenError):

    def __init__(
        self,
        detail: str = '수강 등록이 필요합니다'
    ) -> None:
        super().__init__(detail=detail)

class EnrollmentExpiredError(GoneError):

    def __init__(
        self,
        detail: str = '수강 기간이 만료되었습니다'
    ) -> None:
        super().__init__(detail=detail)

class ProgressNotFoundError(NotFoundError):

    def __init__(
        self,
        detail: str = '학습 진행 기록을 찾을 수 없습니다'
    ) -> None:
        super().__init__(detail=detail)

# 미션 도메인
class MaxAttemptsExceededError(BadRequestError):
    
    def __init__(
        self,
        detail: str = '최대 제출 횟수를 초과했습니다'
    ) -> None:
        super().__init__(detail=detail)

class MissionNotFoundError(NotFoundError):

    def __init__(
        self,
        detail: str = '미션을 찾을 수 없습니다'
    ) -> None:
        super().__init__(detail=detail)

# 결제 및 쿠폰 도메인
class AlreadyPaidError(ConflictError):
    
    def __init__(
        self,
        detail: str = '이미 결제한 강의입니다'
    ) -> None:
        super().__init__(detail=detail)

class PaymentNotFoundError(NotFoundError):

    def __init__(
        self,
        detail: str = '결제 내역을 찾을 수 없습니다'
    ) -> None:
        super().__init__(detail=detail)

class PaymentConfirmFailedError(BadRequestError):

    def __init__(
        self,
        detail: str = '결제 확인에 실패했습니다'
    ) -> None:
        super().__init__(detail=detail)

class RefundNotAllowedError(BadRequestError):
    
    def __init__(
        self,
        detail: str = '환불 가능 기간이 지났습니다'
    ) -> None:
        super().__init__(detail=detail)

class CouponNotFoundError(NotFoundError):
    
    def __init__(
        self,
        detail: str = '쿠폰을 찾을 수 없습니다'
    ) -> None:
        super().__init__(detail=detail)

class CouponExpiredError(BadRequestError):

    def __init__(self, detail: str = '쿠폰이 만료되었습니다') -> None:
        super().__init__(detail=detail)

class CouponCodeDuplicateError(ConflictError):

    def __init__(
        self,
        detail: str = '이미 존재하는 쿠폰 코드입니다'
    ) -> None:
        super().__init__(detail=detail)

class CouponMaxUsageExceededError(BadRequestError):

    def __init__(
        self,
        detail: str = '쿠폰 사용 한도에 도달했습니다'
    ) -> None:
        super().__init__(detail=detail)

# 수료증 도메인
class CertificateNotFoundError(NotFoundError):
    
    def __init__(
        self,
        detail: str = '수료증을 찾을 수 없습니다'
    ) -> None:
        super().__init__(detail=detail)

class CompletionRequirementsNotMetError(BadRequestError):

    def __init__(
        self,
        detail: str = '수료 조건을 충족하지 않았습니다'
    ) -> None:
        super().__init__(detail=detail)

# Q&A 도메인
class QuestionNotFoundError(NotFoundError):

    def __init__(
        self,
        detail: str = '질문을 찾을 수 없습니다'
    ) -> None:
        super().__init__(detail=detail)

class OnlyAuthorCanModifyError(ForbiddenError):

    def __init__(
        self,
        detail: str = '본인이 작성한 글만 수정할 수 있습니다'
    ) -> None:
        super().__init__(detail=detail)

# 환불 도메인
class InsufficientRefundPeriodError(BadRequestError):

    def __init__(
        self,
        detail: str = '환불 가능 기간이 지났습니다'
    ) -> None:
        super().__init__(detail=detail)

class RefundAlreadyProcessedError(ConflictError):

    def __init__(
        self,
        detail: str = '이미 처리된 환불 요청입니다'
    ) -> None:
        super().__init__(detail=detail)

class RefundNotFoundError(NotFoundError):

    def __init__(
        self,
        detail: str = '환불 요청을 찾을 수 없습니다'
    ) -> None:
        super().__init__(detail=detail)

class InvalidRefundStatusError(BadRequestError):

    def __init__(
        self,
        detail: str = '유효하지 않은 환불 상태입니다'
    ) -> None:
        super().__init__(detail=detail)

class CancelNotAllowedError(BadRequestError):

    def __init__(
        self,
        detail: str = '완료된 결제는 취소할 수 없습니다'
    ) -> None:
        super().__init__(detail=detail)
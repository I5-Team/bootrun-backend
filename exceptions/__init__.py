"""
BootRun Exceptions Package
모든 예외 클래스, 에러 응답 딕셔너리, 핸들러를 중앙 관리
"""

# ============= 기본 예외 클래스 =============
from .base import (
    # 기본 예외
    BaseAPIException,
    
    # HTTP 예외 (4xx, 5xx)
    BadRequestError,
    UnauthorizedError,
    ForbiddenError,
    NotFoundError,
    ConflictError,
    GoneError,
    UnprocessableEntityError,
    InternalServerError,
    
    # 도메인별 커스텀 예외 - 인증/회원
    LoginFailedError,
    EmailAlreadyExistsError,
    VerificationCodeInvalidError,
    TokenExpiredError,
    
    # 도메인별 커스텀 예외 - 강의
    CourseNotFoundError,
    ChapterNotFoundError,
    LectureNotFoundError,
    
    # 도메인별 커스텀 예외 - 수강 등록
    AlreadyEnrolledError,
    EnrollmentRequiredError,
    EnrollmentExpiredError,
    
    # 도메인별 커스텀 예외 - 미션
    MaxAttemptsExceededError,
    MissionNotFoundError,
    
    # 도메인별 커스텀 예외 - 결제
    AlreadyPaidError,
    PaymentNotFoundError,
    RefundNotAllowedError,
    CouponNotFoundError,
    CouponExpiredError,
    
    # 도메인별 커스텀 예외 - 수료증
    CertificateNotFoundError,
    CompletionRequirementsNotMetError,
    
    # 도메인별 커스텀 예외 - Q&A
    QuestionNotFoundError,
    OnlyAuthorCanModifyError,
)

# ============= 공통 응답 템플릿 =============
from .base import (
    COMMON_400,
    COMMON_401,
    COMMON_403,
    COMMON_404,
    COMMON_409,
    COMMON_410,
    COMMON_422,
    COMMON_500,
    AUTH_RESPONSES,
    READ_RESPONSES,
    CREATE_RESPONSES,
    MODIFY_RESPONSES,
    ADMIN_RESPONSES,
    make_error_response,
)

# ============= 도메인별 에러 응답 =============
from .responses import (
    # 인증/회원
    LOGIN_RESPONSES,
    REGISTER_RESPONSES,
    EMAIL_VERIFICATION_RESPONSES,
    PASSWORD_RESET_RESPONSES,
    USER_UPDATE_RESPONSES,
    
    # 강의
    COURSE_CREATE_RESPONSES,
    COURSE_UPDATE_RESPONSES,
    COURSE_LIST_RESPONSES,
    COURSE_DETAIL_RESPONSES,
    CHAPTER_CREATE_RESPONSES,
    LECTURE_CREATE_RESPONSES,
    QNA_CREATE_RESPONSES,
    QNA_UPDATE_RESPONSES,
    COMMENT_CREATE_RESPONSES,
    
    # 수강 등록
    ENROLLMENT_CREATE_RESPONSES,
    ENROLLMENT_ACCESS_RESPONSES,
    PROGRESS_UPDATE_RESPONSES,
    
    # 미션
    MISSION_CREATE_RESPONSES,
    MISSION_SUBMIT_RESPONSES,
    
    # 결제
    PAYMENT_CREATE_RESPONSES,
    PAYMENT_CONFIRM_RESPONSES,
    COUPON_VALIDATE_RESPONSES,
    REFUND_CREATE_RESPONSES,
    REFUND_UPDATE_RESPONSES,
    
    # 수료증
    CERTIFICATE_ISSUE_RESPONSES,
    CERTIFICATE_VERIFY_RESPONSES,
    CERTIFICATE_GENERATE_RESPONSES,
    
    # 관리자
    ADMIN_DASHBOARD_RESPONSES,
    ADMIN_USER_MANAGEMENT_RESPONSES,
    ADMIN_COURSE_MANAGEMENT_RESPONSES,
    ADMIN_PAYMENT_MANAGEMENT_RESPONSES,
    ADMIN_STATS_RESPONSES,
)

# ============= 예외 핸들러 =============
from .handlers import (
    custom_exception_handler,
    http_exception_handler,
    validation_exception_handler,
    general_exception_handler,
    register_exception_handlers,
    error_response,
)


# ============= Public API 명시 =============
__all__ = [
    # ========== 예외 클래스 ==========
    # 기본 예외
    'BaseAPIException',
    
    # HTTP 예외
    'BadRequestError',
    'UnauthorizedError',
    'ForbiddenError',
    'NotFoundError',
    'ConflictError',
    'GoneError',
    'UnprocessableEntityError',
    'InternalServerError',
    
    # 인증/회원 예외
    'LoginFailedError',
    'EmailAlreadyExistsError',
    'VerificationCodeInvalidError',
    'TokenExpiredError',
    
    # 강의 예외
    'CourseNotFoundError',
    'ChapterNotFoundError',
    'LectureNotFoundError',
    
    # 수강 등록 예외
    'AlreadyEnrolledError',
    'EnrollmentRequiredError',
    'EnrollmentExpiredError',
    
    # 미션 예외
    'MaxAttemptsExceededError',
    'MissionNotFoundError',
    
    # 결제 예외
    'AlreadyPaidError',
    'PaymentNotFoundError',
    'RefundNotAllowedError',
    'CouponNotFoundError',
    'CouponExpiredError',
    
    # 수료증 예외
    'CertificateNotFoundError',
    'CompletionRequirementsNotMetError',
    
    # Q&A 예외
    'QuestionNotFoundError',
    'OnlyAuthorCanModifyError',
    
    # ========== 공통 응답 ==========
    'COMMON_400',
    'COMMON_401',
    'COMMON_403',
    'COMMON_404',
    'COMMON_409',
    'COMMON_410',
    'COMMON_422',
    'COMMON_500',
    'AUTH_RESPONSES',
    'READ_RESPONSES',
    'CREATE_RESPONSES',
    'MODIFY_RESPONSES',
    'ADMIN_RESPONSES',
    'make_error_response',
    
    # ========== 도메인별 에러 응답 ==========
    # 인증/회원
    'LOGIN_RESPONSES',
    'REGISTER_RESPONSES',
    'EMAIL_VERIFICATION_RESPONSES',
    'PASSWORD_RESET_RESPONSES',
    'USER_UPDATE_RESPONSES',
    
    # 강의
    'COURSE_CREATE_RESPONSES',
    'COURSE_UPDATE_RESPONSES',
    'COURSE_LIST_RESPONSES',
    'COURSE_DETAIL_RESPONSES',
    'CHAPTER_CREATE_RESPONSES',
    'LECTURE_CREATE_RESPONSES',
    'QNA_CREATE_RESPONSES',
    'QNA_UPDATE_RESPONSES',
    'COMMENT_CREATE_RESPONSES',
    
    # 수강 등록
    'ENROLLMENT_CREATE_RESPONSES',
    'ENROLLMENT_ACCESS_RESPONSES',
    'PROGRESS_UPDATE_RESPONSES',
    
    # 미션
    'MISSION_CREATE_RESPONSES',
    'MISSION_SUBMIT_RESPONSES',
    
    # 결제
    'PAYMENT_CREATE_RESPONSES',
    'PAYMENT_CONFIRM_RESPONSES',
    'COUPON_VALIDATE_RESPONSES',
    'REFUND_CREATE_RESPONSES',
    'REFUND_UPDATE_RESPONSES',
    
    # 수료증
    'CERTIFICATE_ISSUE_RESPONSES',
    'CERTIFICATE_VERIFY_RESPONSES',
    'CERTIFICATE_GENERATE_RESPONSES',
    
    # 관리자
    'ADMIN_DASHBOARD_RESPONSES',
    'ADMIN_USER_MANAGEMENT_RESPONSES',
    'ADMIN_COURSE_MANAGEMENT_RESPONSES',
    'ADMIN_PAYMENT_MANAGEMENT_RESPONSES',
    'ADMIN_STATS_RESPONSES',
    
    # ========== 예외 핸들러 ==========
    'custom_exception_handler',
    'http_exception_handler',
    'validation_exception_handler',
    'general_exception_handler',
    'register_exception_handlers',
    'error_response',
]
"""
상수 정의 모듈

이 모듈은 애플리케이션 전역에서 사용되는 상수를 중앙 집중식으로 관리합니다.
"""

# =====================================================
# 비밀번호 검증 상수
# =====================================================
PASSWORD_MIN_LENGTH = 8
PASSWORD_MAX_LENGTH = 32
PASSWORD_PATTERN = r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,32}$'
PASSWORD_ERROR_MESSAGE = '비밀번호는 8~32자의 영문 대/소문자, 숫자, 특수문자를 포함해야 합니다'

# =====================================================
# 닉네임 검증 상수
# =====================================================
NICKNAME_MIN_LENGTH = 2
NICKNAME_MAX_LENGTH = 18

# =====================================================
# 페이지네이션 상수
# =====================================================
DEFAULT_PAGE = 1
DEFAULT_PAGE_SIZE = 20
MAX_PAGE_SIZE = 100

# =====================================================
# 로그인 보안 상수
# =====================================================
MAX_LOGIN_ATTEMPTS = 5
LOGIN_LOCKOUT_DURATION = 900  # 15분 (초 단위)
LOGIN_ATTEMPTS_REDIS_KEY_PREFIX = "login_attempts"

# =====================================================
# JWT 토큰 타입
# =====================================================
TOKEN_TYPE_ACCESS = "access"
TOKEN_TYPE_REFRESH = "refresh"
TOKEN_TYPE_EMAIL_VERIFICATION = "email_verification"
TOKEN_TYPE_PASSWORD_RESET = "password_reset"
TOKEN_ISSUER = "bootrun-backend"

# =====================================================
# Redis 키 패턴
# =====================================================
REDIS_KEY_LOGIN_ATTEMPTS = "login_attempts:{user_id}"
REDIS_KEY_EMAIL_VERIFICATION = "email_verify:{email}"
REDIS_KEY_PASSWORD_RESET = "password_reset:{user_id}"
REDIS_KEY_SESSION = "session:{user_id}"
REDIS_KEY_COURSE_CACHE = "course:{course_id}"
REDIS_KEY_USER_CACHE = "user:{user_id}"

# =====================================================
# 파일 업로드 상수
# =====================================================
MAX_UPLOAD_SIZE_MB = 100
MAX_UPLOAD_SIZE_BYTES = MAX_UPLOAD_SIZE_MB * 1024 * 1024

# 이미지 확장자
ALLOWED_IMAGE_EXTENSIONS = {"jpg", "jpeg", "png", "gif", "webp"}

# 비디오 확장자
ALLOWED_VIDEO_EXTENSIONS = {"mp4", "avi", "mov", "mkv", "webm"}

# 문서 확장자
ALLOWED_DOCUMENT_EXTENSIONS = {"pdf", "doc", "docx", "xls", "xlsx", "ppt", "pptx"}

# 모든 허용 확장자
ALLOWED_ALL_EXTENSIONS = ALLOWED_IMAGE_EXTENSIONS | ALLOWED_VIDEO_EXTENSIONS | ALLOWED_DOCUMENT_EXTENSIONS

# MIME 타입 매핑
MIME_TYPE_MAPPING = {
    # 이미지
    "jpg": "image/jpeg",
    "jpeg": "image/jpeg",
    "png": "image/png",
    "gif": "image/gif",
    "webp": "image/webp",
    # 비디오
    "mp4": "video/mp4",
    "avi": "video/x-msvideo",
    "mov": "video/quicktime",
    "mkv": "video/x-matroska",
    "webm": "video/webm",
    # 문서
    "pdf": "application/pdf",
    "doc": "application/msword",
    "docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "xls": "application/vnd.ms-excel",
    "xlsx": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    "ppt": "application/vnd.ms-powerpoint",
    "pptx": "application/vnd.openxmlformats-officedocument.presentationml.presentation",
}

# =====================================================
# 인증서 관련 상수
# =====================================================
CERTIFICATE_NUMBER_PATTERN = r'^WNIV-\d{4}-\d{6}$'
CERTIFICATE_PREFIX = "WNIV"

# =====================================================
# 이메일 관련 상수
# =====================================================
EMAIL_VERIFICATION_CODE_LENGTH = 6
EMAIL_VERIFICATION_CODE_EXPIRY_MINUTES = 30

# =====================================================
# HTTP 상태 코드
# =====================================================
HTTP_200_OK = 200
HTTP_201_CREATED = 201
HTTP_204_NO_CONTENT = 204
HTTP_400_BAD_REQUEST = 400
HTTP_401_UNAUTHORIZED = 401
HTTP_403_FORBIDDEN = 403
HTTP_404_NOT_FOUND = 404
HTTP_409_CONFLICT = 409
HTTP_410_GONE = 410
HTTP_422_UNPROCESSABLE_ENTITY = 422
HTTP_500_INTERNAL_SERVER_ERROR = 500

# =====================================================
# 성공/오류 메시지
# =====================================================
MSG_SUCCESS = "요청이 성공적으로 처리되었습니다"
MSG_CREATED = "리소스가 성공적으로 생성되었습니다"
MSG_UPDATED = "리소스가 성공적으로 수정되었습니다"
MSG_DELETED = "리소스가 성공적으로 삭제되었습니다"

# 회원가입 관련
MSG_USER_REGISTERED = "회원가입이 완료되었습니다"
MSG_EMAIL_SENT = "이메일이 전송되었습니다"
MSG_EMAIL_VERIFIED = "이메일 인증이 완료되었습니다"

# 로그인 관련
MSG_LOGIN_SUCCESS = "로그인 성공"
MSG_LOGOUT_SUCCESS = "로그아웃 성공"
MSG_TOKEN_REFRESHED = "토큰이 갱신되었습니다"

# 비밀번호 관련
MSG_PASSWORD_CHANGED = "비밀번호가 변경되었습니다"
MSG_PASSWORD_RESET_EMAIL_SENT = "비밀번호 재설정 이메일이 전송되었습니다"
MSG_PASSWORD_RESET_SUCCESS = "비밀번호가 재설정되었습니다"

# 프로필 관련
MSG_PROFILE_UPDATED = "프로필이 업데이트되었습니다"
MSG_PROFILE_IMAGE_UPDATED = "프로필 이미지가 업데이트되었습니다"

# 계정 관련
MSG_ACCOUNT_DEACTIVATED = "계정이 비활성화되었습니다"
MSG_ACCOUNT_RESTORED = "계정이 복구되었습니다"

# 에러 메시지
MSG_ERROR_INVALID_CREDENTIALS = "이메일 또는 비밀번호가 올바르지 않습니다"
MSG_ERROR_EMAIL_EXISTS = "이미 존재하는 이메일입니다"
MSG_ERROR_USER_NOT_FOUND = "사용자를 찾을 수 없습니다"
MSG_ERROR_UNAUTHORIZED = "인증이 필요합니다"
MSG_ERROR_FORBIDDEN = "접근 권한이 없습니다"
MSG_ERROR_TOKEN_EXPIRED = "토큰이 만료되었습니다"
MSG_ERROR_INVALID_TOKEN = "유효하지 않은 토큰입니다"
MSG_ERROR_PASSWORDS_NOT_MATCH = "비밀번호가 일치하지 않습니다"
MSG_ERROR_WEAK_PASSWORD = PASSWORD_ERROR_MESSAGE
MSG_ERROR_LOGIN_ATTEMPTS_EXCEEDED = "로그인 시도 횟수를 초과했습니다. 나중에 다시 시도해주세요"
MSG_ERROR_VERIFICATION_CODE_INVALID = "인증 코드가 유효하지 않습니다"
MSG_ERROR_FILE_TOO_LARGE = f"파일 크기는 {MAX_UPLOAD_SIZE_MB}MB를 초과할 수 없습니다"
MSG_ERROR_INVALID_FILE_TYPE = "허용되지 않는 파일 형식입니다"
MSG_ERROR_INTERNAL_SERVER = "서버 내부 오류가 발생했습니다"

# =====================================================
# API 라우터 접두사
# =====================================================
API_PREFIX = "/api"
ADMIN_PREFIX = "/admin"
AUTH_PREFIX = "/auth"
USER_PREFIX = "/user"
COURSE_PREFIX = "/course"
ENROLLMENT_PREFIX = "/enrollment"
MISSION_PREFIX = "/mission"
PAYMENT_PREFIX = "/payment"
COUPON_PREFIX = "/coupon"
CERTIFICATE_PREFIX_API = "/certificate"
QUESTION_PREFIX = "/question"
CHATBOT_PREFIX = "/chatbot"

# =====================================================
# 타임존 및 로케일
# =====================================================
TIMEZONE_KST = "Asia/Seoul"
TIMEZONE_UTC = "UTC"
DEFAULT_LOCALE = "ko_KR"

# =====================================================
# 캐시 만료 시간 (초)
# =====================================================
CACHE_TTL_SHORT = 60  # 1분
CACHE_TTL_MEDIUM = 300  # 5분
CACHE_TTL_LONG = 3600  # 1시간
CACHE_TTL_DAY = 86400  # 24시간

# =====================================================
# 코스 관련 상수
# =====================================================
COURSE_PUBLISH_STATUS_DRAFT = "draft"
COURSE_PUBLISH_STATUS_PUBLISHED = "published"
COURSE_PUBLISH_STATUS_ARCHIVED = "archived"

# =====================================================
# 결제 관련 상수
# =====================================================
PAYMENT_STATUS_PENDING = "pending"
PAYMENT_STATUS_COMPLETED = "completed"
PAYMENT_STATUS_FAILED = "failed"
PAYMENT_STATUS_REFUNDED = "refunded"

# 환불 가능 기간 (일)
REFUND_ALLOWED_DAYS = 7

# =====================================================
# 진행률 관련 상수
# =====================================================
PROGRESS_COMPLETION_THRESHOLD = 100  # 100%
MISSION_MAX_ATTEMPTS = 3

# =====================================================
# 정규 표현식 패턴
# =====================================================
PATTERN_EMAIL = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
PATTERN_PHONE_KR = r'^01[0-9]-?\d{3,4}-?\d{4}$'
PATTERN_UUID = r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$'

# =====================================================
# 기본값
# =====================================================
DEFAULT_PROFILE_IMAGE = "https://via.placeholder.com/150"
DEFAULT_COURSE_THUMBNAIL = "https://via.placeholder.com/800x450"

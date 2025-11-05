"""
인증 API 라우터
회원가입, 로그인, 소셜 로그인, 이메일 인증, 비밀번호 재설정 등을 처리합니다.
"""

from fastapi import APIRouter, Header, status
from schemas.user import (
    UserCreate, UserLogin, UserResponse, TokenResponse,
    EmailVerificationRequest, EmailVerificationConfirm,
    SocialLoginRequest, PasswordResetRequest, PasswordResetConfirm
)
from schemas.common import MessageResponse
from exceptions import (
    REGISTER_RESPONSES,
    LOGIN_RESPONSES,
    EMAIL_VERIFICATION_RESPONSES,
    PASSWORD_RESET_RESPONSES,
    AUTH_RESPONSES,
)

router = APIRouter(prefix="/auth", tags=["인증"])


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="회원가입",
    description="새로운 사용자를 등록합니다. 이메일과 비밀번호를 사용하여 회원가입할 수 있습니다.",
    responses=REGISTER_RESPONSES
)
async def register(data: UserCreate):
    """
    # 회원가입 API
    
    새로운 사용자 계정을 생성합니다.
    
    ## 요청 본문
    - **email**: 이메일 주소 (중복 불가)
    - **password**: 비밀번호 (8~32자, 대소문자/숫자/특수문자 포함)
    - **password_confirm**: 비밀번호 확인 (password와 일치해야 함)
    - **nickname**: 닉네임 (2~18자, 중복 불가)
    - **gender**: 성별 (MALE/FEMALE/OTHER)
    - **birth_date**: 생년월일
    - **profile_image**: 프로필 이미지 URL (선택)
    
    ## 응답
    - 201: 회원가입 성공, 생성된 사용자 정보 반환
    - 400: 이미 존재하는 이메일
    - 422: 입력값 유효성 검사 실패
    """
    pass


@router.post(
    "/login",
    response_model=TokenResponse,
    summary="로그인",
    description="이메일과 비밀번호로 로그인하여 액세스 토큰을 발급받습니다.",
    responses=LOGIN_RESPONSES
)
async def login(data: UserLogin):
    """
    # 로그인 API
    
    이메일과 비밀번호로 로그인하여 JWT 토큰을 발급받습니다.
    
    ## 요청 본문
    - **email**: 이메일 주소
    - **password**: 비밀번호
    
    ## 응답
    - 200: 로그인 성공, 액세스 토큰 및 사용자 정보 반환
    - 401: 이메일 또는 비밀번호 불일치
    - 422: 입력값 유효성 검사 실패
    
    ## 참고
    - 발급된 토큰은 Authorization 헤더에 'Bearer {token}' 형식으로 포함하여 사용
    """
    pass


@router.post(
    "/logout",
    response_model=MessageResponse,
    summary="로그아웃",
    description="현재 세션을 종료하고 토큰을 무효화합니다.",
    responses=AUTH_RESPONSES
)
async def logout():
    """
    # 로그아웃 API
    
    현재 로그인된 세션을 종료합니다.
    
    ## 응답
    - 200: 로그아웃 성공
    - 401: 인증되지 않은 사용자
    
    ## 참고
    - 클라이언트에서 저장된 토큰을 삭제해야 합니다
    """
    pass


@router.post(
    "/refresh",
    response_model=TokenResponse,
    summary="토큰 갱신",
    description="리프레시 토큰을 사용하여 새로운 액세스 토큰을 발급받습니다.",
    responses={
        **AUTH_RESPONSES,
        401: {
            "description": "리프레시 토큰이 유효하지 않거나 만료됨",
            "content": {
                "application/json": {
                    "example": {
                        "error": "TOKEN_EXPIRED",
                        "detail": "리프레시 토큰이 만료되었습니다"
                    }
                }
            }
        }
    }
)
async def refresh_token(
    authorization: str = Header(..., description="Bearer {refresh_token}")
):
    """
    # 토큰 갱신 API
    
    만료된 액세스 토큰을 리프레시 토큰으로 갱신합니다.
    
    ## 헤더
    - **Authorization**: Bearer {refresh_token}
    
    ## 응답
    - 200: 새로운 액세스 토큰 발급
    - 401: 리프레시 토큰 만료 또는 유효하지 않음
    """
    pass


@router.post(
    "/email/verification/request",
    response_model=MessageResponse,
    summary="이메일 인증 요청",
    description="이메일 주소로 인증 코드를 발송합니다.",
    responses=EMAIL_VERIFICATION_RESPONSES
)
async def request_email_verification(data: EmailVerificationRequest):
    """
    # 이메일 인증 요청 API
    
    회원가입 시 이메일 인증을 위한 코드를 발송합니다.
    
    ## 요청 본문
    - **email**: 인증할 이메일 주소
    
    ## 응답
    - 200: 인증 코드 발송 성공
    - 400: 유효하지 않은 이메일
    - 422: 입력값 유효성 검사 실패
    
    ## 참고
    - 인증 코드는 5분간 유효합니다
    """
    pass


@router.post(
    "/email/verification/confirm",
    response_model=MessageResponse,
    summary="이메일 인증 확인",
    description="발송된 인증 코드를 확인하여 이메일을 인증합니다.",
    responses=EMAIL_VERIFICATION_RESPONSES
)
async def confirm_email_verification(data: EmailVerificationConfirm):
    """
    # 이메일 인증 확인 API
    
    발송된 인증 코드를 확인합니다.
    
    ## 요청 본문
    - **email**: 인증할 이메일 주소
    - **verification_code**: 이메일로 받은 인증 코드
    
    ## 응답
    - 200: 이메일 인증 완료
    - 400: 인증 코드가 올바르지 않거나 만료됨
    - 422: 입력값 유효성 검사 실패
    """
    pass


@router.post(
    "/social/google",
    response_model=TokenResponse,
    summary="Google 소셜 로그인",
    description="Google 계정으로 로그인합니다.",
    responses=LOGIN_RESPONSES
)
async def google_login(data: SocialLoginRequest):
    """
    # Google 소셜 로그인 API
    
    Google OAuth를 통해 로그인합니다.
    
    ## 요청 본문
    - **provider**: "google" (고정값)
    - **access_token**: Google에서 발급받은 액세스 토큰
    - **email**: 사용자 이메일 (선택)
    - **nickname**: 사용자 닉네임 (선택)
    
    ## 응답
    - 200: 로그인 성공
    - 401: Google 토큰 검증 실패
    - 422: 입력값 유효성 검사 실패
    """
    pass


@router.post(
    "/social/github",
    response_model=TokenResponse,
    summary="Github 소셜 로그인",
    description="Github 계정으로 로그인합니다.",
    responses=LOGIN_RESPONSES
)
async def github_login(data: SocialLoginRequest):
    """
    # Github 소셜 로그인 API
    
    Github OAuth를 통해 로그인합니다.
    
    ## 요청 본문
    - **provider**: "github" (고정값)
    - **access_token**: Github에서 발급받은 액세스 토큰
    - **email**: 사용자 이메일 (선택)
    - **nickname**: 사용자 닉네임 (선택)
    
    ## 응답
    - 200: 로그인 성공
    - 401: Github 토큰 검증 실패
    - 422: 입력값 유효성 검사 실패
    """
    pass


@router.post(
    "/password/reset/request",
    response_model=MessageResponse,
    summary="비밀번호 재설정 요청",
    description="비밀번호 재설정을 위한 링크를 이메일로 발송합니다.",
    responses=PASSWORD_RESET_RESPONSES
)
async def request_password_reset(data: PasswordResetRequest):
    """
    # 비밀번호 재설정 요청 API
    
    비밀번호를 잊어버린 경우 재설정 링크를 이메일로 발송합니다.
    
    ## 요청 본문
    - **email**: 가입된 이메일 주소
    
    ## 응답
    - 200: 재설정 링크 발송 성공
    - 404: 해당 이메일로 가입된 사용자 없음
    - 422: 입력값 유효성 검사 실패
    
    ## 참고
    - 재설정 토큰은 1시간 동안 유효합니다
    """
    pass


@router.post(
    "/password/reset/confirm",
    response_model=MessageResponse,
    summary="비밀번호 재설정 확인",
    description="재설정 토큰을 확인하고 새 비밀번호로 변경합니다.",
    responses=PASSWORD_RESET_RESPONSES
)
async def confirm_password_reset(data: PasswordResetConfirm):
    """
    # 비밀번호 재설정 확인 API
    
    이메일로 받은 토큰으로 비밀번호를 재설정합니다.
    
    ## 요청 본문
    - **email**: 이메일 주소
    - **reset_token**: 이메일로 받은 재설정 토큰
    - **new_password**: 새 비밀번호 (8~16자, 대소문자/숫자/특수문자 포함)
    - **password_confirm**: 비밀번호 확인
    
    ## 응답
    - 200: 비밀번호 재설정 완료
    - 400: 토큰이 유효하지 않거나 만료됨
    - 422: 입력값 유효성 검사 실패
    """
    pass


@router.get(
    "/verify",
    response_model=UserResponse,
    summary="토큰 검증",
    description="현재 액세스 토큰의 유효성을 검증하고 사용자 정보를 반환합니다.",
    responses=AUTH_RESPONSES
)
async def verify_token():
    """
    # 토큰 검증 API
    
    현재 사용 중인 액세스 토큰이 유효한지 확인합니다.
    
    ## 응답
    - 200: 토큰 유효, 사용자 정보 반환
    - 401: 토큰이 유효하지 않거나 만료됨
    
    ## 참고
    - 이 API는 프론트엔드에서 페이지 로드 시 로그인 상태를 확인하는 데 사용됩니다
    """
    pass
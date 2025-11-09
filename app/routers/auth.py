from fastapi import APIRouter, Header, status, Depends
from app.schemas.user import (
    UserCreate, UserLogin, UserResponse, TokenResponse,
    EmailVerificationRequest, EmailVerificationConfirm,
    SocialLoginRequest, PasswordResetRequest, PasswordResetConfirm
)
from app.schemas.common import MessageResponse, SuccessResponse
from app.exceptions.responses import (
    REGISTER_RESPONSES,
    LOGIN_RESPONSES,
    EMAIL_VERIFICATION_RESPONSES,
    PASSWORD_RESET_RESPONSES,
    USER_UPDATE_RESPONSES,
    COMMON_401,
    COMMON_422,
    COMMON_500,
)
from app.core.dependencies import get_current_user
from app.models.user import User

router = APIRouter(prefix="/auth", tags=["인증"])

@router.post(
    "/register",
    response_model=SuccessResponse[UserResponse],
    status_code=status.HTTP_201_CREATED,
    summary="회원가입",
    description="새로운 사용자를 등록합니다. 이메일과 비밀번호를 사용하여 회원가입할 수 있습니다.",
    responses={
        201: {"description": "회원가입 성공"},
        **REGISTER_RESPONSES
    }
)
async def register(data: UserCreate):
    pass

@router.post(
    "/login",
    response_model=SuccessResponse[TokenResponse],
    summary="로그인",
    description="이메일과 비밀번호로 로그인하여 액세스 토큰을 발급받습니다.",
    responses={
        200: {"description": "로그인 성공"},
        **LOGIN_RESPONSES
    }
)
async def login(data: UserLogin):
    pass

@router.post(
    "/logout",
    response_model=MessageResponse,
    summary="로그아웃",
    description="현재 세션을 종료하고 토큰을 무효화합니다.",
    responses={
        200: {"description": "로그아웃 성공"},
        401: COMMON_401,
        422: COMMON_422,
        500: COMMON_500,
    }
)
async def logout(current_user: User = Depends(get_current_user)):
    pass

@router.post(
    "/refresh",
    response_model=SuccessResponse[TokenResponse],
    summary="토큰 갱신",
    description="리프레시 토큰을 사용하여 새로운 액세스 토큰을 발급받습니다.",
    responses={
        200: {"description": "토큰 갱신 성공"},
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
        },
        422: COMMON_422,
        500: COMMON_500,
    }
)
async def refresh_token(
    authorization: str = Header(..., description="Bearer {refresh_token}")
):
    pass

@router.post(
    "/email/verification/request",
    response_model=MessageResponse,
    summary="이메일 인증 요청",
    description="이메일 주소로 인증 코드를 발송합니다.",
    responses={
        200: {"description": "인증 코드 발송 성공"},
        **EMAIL_VERIFICATION_RESPONSES
    }
)
async def request_email_verification(data: EmailVerificationRequest):
    pass

@router.post(
    "/email/verification/confirm",
    response_model=MessageResponse,
    summary="이메일 인증 확인",
    description="발송된 인증 코드를 확인하여 이메일을 인증합니다.",
    responses={
        200: {"description": "이메일 인증 완료"},
        **EMAIL_VERIFICATION_RESPONSES
    }
)
async def confirm_email_verification(data: EmailVerificationConfirm):
    pass

@router.post(
    "/social/google",
    response_model=SuccessResponse[TokenResponse],
    summary="Google 소셜 로그인",
    description="Google 계정으로 로그인합니다.",
    responses={
        200: {"description": "Google 로그인 성공"},
        **LOGIN_RESPONSES
    }
)
async def google_login(data: SocialLoginRequest):
    pass

@router.post(
    "/social/github",
    response_model=SuccessResponse[TokenResponse],
    summary="Github 소셜 로그인",
    description="Github 계정으로 로그인합니다.",
    responses={
        200: {"description": "Github 로그인 성공"},
        **LOGIN_RESPONSES
    }
)
async def github_login(data: SocialLoginRequest):
    pass

@router.post(
    "/password/reset/request",
    response_model=MessageResponse,
    summary="비밀번호 재설정 요청",
    description="비밀번호 재설정을 위한 링크를 이메일로 발송합니다.",
    responses={
        200: {"description": "재설정 링크 발송 성공"},
        **PASSWORD_RESET_RESPONSES
    }
)
async def request_password_reset(data: PasswordResetRequest):
    pass

@router.post(
    "/password/reset/confirm",
    response_model=MessageResponse,
    summary="비밀번호 재설정 확인",
    description="재설정 토큰을 확인하고 새 비밀번호로 변경합니다.",
    responses={
        200: {"description": "비밀번호 재설정 완료"},
        **PASSWORD_RESET_RESPONSES
    }
)
async def confirm_password_reset(data: PasswordResetConfirm):
    pass

@router.get(
    "/verify",
    response_model=SuccessResponse[UserResponse],
    summary="토큰 검증",
    description="현재 액세스 토큰의 유효성을 검증하고 사용자 정보를 반환합니다.",
    responses={
        200: {"description": "토큰 검증 성공"},
        401: COMMON_401,
        422: COMMON_422,
        500: COMMON_500,
    }
)
async def verify_token(current_user: User = Depends(get_current_user)):
    pass
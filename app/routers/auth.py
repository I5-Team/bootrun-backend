from fastapi import APIRouter, Header, status, Depends, HTTPException
from app.schemas.user import (
    UserCreate, UserLogin, UserResponse, TokenResponse,
    EmailVerificationRequest, EmailVerificationConfirm,
    SocialLoginRequest, PasswordResetRequest, PasswordResetConfirm,
    SocialProvider
)
from app.schemas.common import MessageResponse, SuccessResponse
from app.exceptions.responses import (
    REGISTER_RESPONSES,
    LOGIN_RESPONSES,
    EMAIL_VERIFICATION_RESPONSES,
    PASSWORD_RESET_RESPONSES,
    AUTH_RESPONSES,
)
from app.core.dependencies import get_current_user, get_user_service
from app.models.user import User
from app.services.user_service import UserService
from app.exceptions.base import BaseAPIException
from app.utils.constants import (
    MSG_USER_REGISTERED,
    MSG_LOGIN_SUCCESS,
    MSG_LOGOUT_SUCCESS,
    MSG_TOKEN_REFRESHED,
    MSG_EMAIL_VERIFIED,
    MSG_ERROR_INVALID_TOKEN,
    MSG_PASSWORD_RESET_EMAIL_SENT,
    MSG_PASSWORD_RESET_SUCCESS,
)
from app.utils.helpers import is_valid_email, truncate_string
import logging

router = APIRouter(prefix="/auth", tags=["인증"])
logger = logging.getLogger(__name__)

# ============================================================
# 1. 회원가입 & 이메일 인증
# ============================================================

@router.post(
    "/register",
    response_model=SuccessResponse[UserResponse],
    status_code=status.HTTP_201_CREATED,
    summary="회원가입",
    description="새로운 사용자를 등록합니다. 이메일과 비밀번호를 사용하여 회원가입할 수 있습니다.",
    responses={
        201: {
            "description": "회원가입 성공",
            "content": {
                "application/json": {
                    "example": {
                        "success": True,
                        "message": "회원가입이 완료되었습니다",
                        "data": {
                            "id": 1,
                            "email": "hong@example.com",
                            "nickname": "홍길동",
                            "gender": "male",
                            "birth_date": "1995-01-01",
                            "profile_image": None,
                            "role": "student",
                            "is_active": True,
                            "is_email_verified": False,
                            "created_at": "2025-01-10T12:00:00Z",
                            "updated_at": "2025-01-10T12:00:00Z",
                            "last_login": None,
                            "social_provider": "email",
                            "social_id": None
                        }
                    }
                }
            }
        },
        **REGISTER_RESPONSES
    }
)
async def register(
    data: UserCreate,
    user_service: UserService = Depends(get_user_service)
):
    try:
        user = await user_service.register_user(data)
        return SuccessResponse(
            success=True,
            message=MSG_USER_REGISTERED,
            data=user
        )
    except BaseAPIException as e:
        raise HTTPException(
            status_code=e.status_code,
            detail={"error": e.error_code, "detail": e.detail}
        )

@router.post(
    "/email/verification/request",
    response_model=MessageResponse,
    summary="이메일 인증 요청",
    description="이메일 주소로 인증 코드를 발송합니다.",
    responses={
        200: {
            "description": "인증 코드 발송 성공",
            "content": {
                "application/json": {
                    "example": {
                        "success": True,
                        "message": "인증 코드가 이메일로 발송되었습니다",
                        "detail": "개발 환경에서 인증 코드: 123456"
                    }
                }
            }
        },
        **EMAIL_VERIFICATION_RESPONSES
    }
)
async def request_email_verification(
    data: EmailVerificationRequest,
    user_service: UserService = Depends(get_user_service)
):
    try:
        verification_code = await user_service.send_verification_code(data.email)
        logger.info(f"이메일 인증 코드 발송: {data.email}, 코드: {verification_code}")

        return MessageResponse(
            success=True,
            message="인증 코드가 이메일로 발송되었습니다",
            detail=f"개발 환경에서 인증 코드: {verification_code}"
        )
    except BaseAPIException as e:
        raise HTTPException(
            status_code=e.status_code,
            detail={"error": e.error_code, "detail": e.detail}
        )

@router.post(
    "/email/verification/confirm",
    response_model=MessageResponse,
    summary="이메일 인증 확인",
    description="발송된 인증 코드를 확인하여 이메일을 인증합니다.",
    responses={
        200: {
            "description": "이메일 인증 완료",
            "content": {
                "application/json": {
                    "example": {
                        "success": True,
                        "message": "이메일 인증이 완료되었습니다"
                    }
                }
            }
        },
        **EMAIL_VERIFICATION_RESPONSES
    }
)
async def confirm_email_verification(
    data: EmailVerificationConfirm,
    user_service: UserService = Depends(get_user_service)
):
    try:
        await user_service.verify_email(data.email, data.verification_code)
        return MessageResponse(
            success=True,
            message=MSG_EMAIL_VERIFIED
        )
    except BaseAPIException as e:
        raise HTTPException(
            status_code=e.status_code,
            detail={"error": e.error_code, "detail": e.detail}
        )

# ============================================================
# 2. 로그인
# ============================================================

@router.post(
    "/login",
    response_model=SuccessResponse[TokenResponse],
    summary="로그인",
    description="이메일과 비밀번호로 로그인하여 액세스 토큰을 발급받습니다.",
    responses={
        200: {
            "description": "로그인 성공",
            "content": {
                "application/json": {
                    "example": {
                        "success": True,
                        "message": "로그인에 성공했습니다",
                        "data": {
                            "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                            "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                            "token_type": "bearer",
                            "user": {
                                "id": 1,
                                "email": "hong@example.com",
                                "nickname": "홍길동",
                                "gender": "male",
                                "birth_date": "1995-01-01",
                                "profile_image": None,
                                "role": "student",
                                "is_active": True,
                                "is_email_verified": True,
                                "created_at": "2025-01-01T00:00:00Z",
                                "updated_at": "2025-01-10T12:00:00Z",
                                "last_login": "2025-01-10T12:00:00Z",
                                "social_provider": "email",
                                "social_id": None
                            }
                        }
                    }
                }
            }
        },
        **LOGIN_RESPONSES
    }
)
async def login(
    data: UserLogin,
    user_service: UserService = Depends(get_user_service)
):
    try:
        token_response = await user_service.login(data)
        return SuccessResponse(
            success=True,
            message=MSG_LOGIN_SUCCESS,
            data=token_response
        )
    except BaseAPIException as e:
        raise HTTPException(
            status_code=e.status_code,
            detail={"error": e.error_code, "detail": e.detail}
        )

@router.post(
    "/social/google",
    response_model=SuccessResponse[TokenResponse],
    summary="Google 소셜 로그인",
    description="Google 계정으로 로그인합니다.",
    responses={
        200: {
            "description": "Google 로그인 성공",
            "content": {
                "application/json": {
                    "example": {
                        "success": True,
                        "message": "Google 로그인에 성공했습니다",
                        "data": {
                            "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                            "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                            "token_type": "bearer",
                            "user": {
                                "id": 1,
                                "email": "user@gmail.com",
                                "nickname": "구글사용자",
                                "gender": "other",
                                "birth_date": "2000-01-01",
                                "profile_image": None,
                                "role": "student",
                                "is_active": True,
                                "is_email_verified": True,
                                "created_at": "2025-01-10T12:00:00Z",
                                "updated_at": "2025-01-10T12:00:00Z",
                                "last_login": "2025-01-10T12:00:00Z",
                                "social_provider": "google",
                                "social_id": "google_abc123"
                            }
                        }
                    }
                }
            }
        },
        **LOGIN_RESPONSES
    }
)
async def google_login(
    data: SocialLoginRequest,
    user_service: UserService = Depends(get_user_service)
):
    try:
        if data.provider != SocialProvider.GOOGLE:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={"error": "INVALID_PROVIDER", "detail": "Google 로그인만 허용됩니다"}
            )

        if not data.email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={"error": "EMAIL_REQUIRED", "detail": "이메일이 필요합니다"}
            )

        if not is_valid_email(data.email):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={"error": "INVALID_EMAIL", "detail": "유효하지 않은 이메일 형식입니다"}
            )

        social_id = f"google_{truncate_string(data.access_token, 20, suffix='')}"

        token_response = await user_service.social_login(
            provider=SocialProvider.GOOGLE,
            social_id=social_id,
            email=data.email,
            nickname=data.nickname
        )

        return SuccessResponse(
            success=True,
            message="Google 로그인에 성공했습니다",
            data=token_response
        )
    except BaseAPIException as e:
        raise HTTPException(
            status_code=e.status_code,
            detail={"error": e.error_code, "detail": e.detail}
        )

@router.post(
    "/social/github",
    response_model=SuccessResponse[TokenResponse],
    summary="Github 소셜 로그인",
    description="Github 계정으로 로그인합니다.",
    responses={
        200: {
            "description": "Github 로그인 성공",
            "content": {
                "application/json": {
                    "example": {
                        "success": True,
                        "message": "Github 로그인에 성공했습니다",
                        "data": {
                            "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                            "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                            "token_type": "bearer",
                            "user": {
                                "id": 2,
                                "email": "user@github.com",
                                "nickname": "깃허브사용자",
                                "gender": "other",
                                "birth_date": "2000-01-01",
                                "profile_image": None,
                                "role": "student",
                                "is_active": True,
                                "is_email_verified": True,
                                "created_at": "2025-01-10T12:00:00Z",
                                "updated_at": "2025-01-10T12:00:00Z",
                                "last_login": "2025-01-10T12:00:00Z",
                                "social_provider": "github",
                                "social_id": "github_xyz789"
                            }
                        }
                    }
                }
            }
        },
        **LOGIN_RESPONSES
    }
)
async def github_login(
    data: SocialLoginRequest,
    user_service: UserService = Depends(get_user_service)
):
    try:
        if data.provider != SocialProvider.GITHUB:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={"error": "INVALID_PROVIDER", "detail": "Github 로그인만 허용됩니다"}
            )

        if not data.email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={"error": "EMAIL_REQUIRED", "detail": "이메일이 필요합니다"}
            )

        if not is_valid_email(data.email):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={"error": "INVALID_EMAIL", "detail": "유효하지 않은 이메일 형식입니다"}
            )

        social_id = f"github_{truncate_string(data.access_token, 20, suffix='')}"

        token_response = await user_service.social_login(
            provider=SocialProvider.GITHUB,
            social_id=social_id,
            email=data.email,
            nickname=data.nickname
        )

        return SuccessResponse(
            success=True,
            message="Github 로그인에 성공했습니다",
            data=token_response
        )
    except BaseAPIException as e:
        raise HTTPException(
            status_code=e.status_code,
            detail={"error": e.error_code, "detail": e.detail}
        )

# ============================================================
# 3. 토큰 관리
# ============================================================

@router.get(
    "/verify",
    response_model=SuccessResponse[UserResponse],
    summary="토큰 검증",
    description="현재 액세스 토큰의 유효성을 검증하고 사용자 정보를 반환합니다.",
    responses={
        200: {
            "description": "토큰 검증 성공",
            "content": {
                "application/json": {
                    "example": {
                        "success": True,
                        "message": "토큰이 유효합니다",
                        "data": {
                            "id": 1,
                            "email": "user@example.com",
                            "nickname": "사용자",
                            "gender": "male",
                            "birth_date": "1995-01-01",
                            "profile_image": None,
                            "role": "student",
                            "is_active": True,
                            "is_email_verified": True,
                            "created_at": "2025-01-01T00:00:00Z",
                            "updated_at": "2025-01-01T00:00:00Z",
                            "last_login": "2025-01-10T12:00:00Z",
                            "social_provider": "email",
                            "social_id": None
                        }
                    }
                }
            }
        },
        **AUTH_RESPONSES
    }
)
async def verify_token(current_user: User = Depends(get_current_user)):
    try:
        return SuccessResponse(
            success=True,
            message="토큰이 유효합니다",
            data=UserResponse.model_validate(current_user)
        )
    except BaseAPIException as e:
        raise HTTPException(
            status_code=e.status_code,
            detail={"error": e.error_code, "detail": e.detail}
        )
    except Exception as e:
        logger.error(f"토큰 검증 중 오류: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error": "INTERNAL_SERVER_ERROR", "detail": "토큰 검증 중 오류가 발생했습니다"}
        )

@router.post(
    "/refresh",
    response_model=SuccessResponse[TokenResponse],
    summary="토큰 갱신",
    description="리프레시 토큰을 사용하여 새로운 액세스 토큰을 발급받습니다.",
    responses={
        200: {
            "description": "토큰 갱신 성공",
            "content": {
                "application/json": {
                    "example": {
                        "success": True,
                        "message": "토큰 갱신에 성공했습니다",
                        "data": {
                            "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                            "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                            "token_type": "bearer",
                            "user": {
                                "id": 1,
                                "email": "hong@example.com",
                                "nickname": "홍길동",
                                "gender": "male",
                                "birth_date": "1995-01-01",
                                "profile_image": None,
                                "role": "student",
                                "is_active": True,
                                "is_email_verified": True,
                                "created_at": "2025-01-01T00:00:00Z",
                                "updated_at": "2025-01-10T12:00:00Z",
                                "last_login": "2025-01-10T12:00:00Z",
                                "social_provider": "email",
                                "social_id": None
                            }
                        }
                    }
                }
            }
        },
        401: {
            "description": "리프레시 토큰이 유효하지 않거나 만료됨",
            "content": {
                "application/json": {
                    "examples": {
                        "token_expired": {
                            "summary": "토큰 만료",
                            "value": {
                                "error": "UNAUTHORIZED",
                                "detail": "유효하지 않거나 만료된 리프레시 토큰입니다"
                            }
                        },
                        "invalid_format": {
                            "summary": "잘못된 토큰 형식",
                            "value": {
                                "error": "INVALID_TOKEN",
                                "detail": "잘못된 토큰 형식입니다"
                            }
                        }
                    }
                }
            }
        },
        **{k: v for k, v in AUTH_RESPONSES.items() if k != 401}
    }
)
async def refresh_token(
    authorization: str = Header(..., description="Bearer {refresh_token}"),
    user_service: UserService = Depends(get_user_service)
):
    try:
        if not authorization.startswith("Bearer "):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail={"error": "INVALID_TOKEN", "detail": MSG_ERROR_INVALID_TOKEN}
            )

        token = authorization.replace("Bearer ", "")
        token_response = await user_service.refresh_access_token(token)

        return SuccessResponse(
            success=True,
            message=MSG_TOKEN_REFRESHED,
            data=token_response
        )
    except BaseAPIException as e:
        raise HTTPException(
            status_code=e.status_code,
            detail={"error": e.error_code, "detail": e.detail}
        )

# ============================================================
# 4. 로그아웃
# ============================================================

@router.post(
    "/logout",
    response_model=MessageResponse,
    summary="로그아웃",
    description="현재 세션을 종료하고 토큰을 무효화합니다.",
    responses={
        200: {
            "description": "로그아웃 성공",
            "content": {
                "application/json": {
                    "example": {
                        "success": True,
                        "message": "로그아웃이 완료되었습니다"
                    }
                }
            }
        },
        **AUTH_RESPONSES
    }
)
async def logout(
    current_user: User = Depends(get_current_user),
    user_service: UserService = Depends(get_user_service)
):
    try:
        await user_service.logout(current_user.id)
        return MessageResponse(
            success=True,
            message=MSG_LOGOUT_SUCCESS
        )
    except BaseAPIException as e:
        raise HTTPException(
            status_code=e.status_code,
            detail={"error": e.error_code, "detail": e.detail}
        )

# ============================================================
# 5. 비밀번호 재설정
# ============================================================

@router.post(
    "/password/reset/request",
    response_model=MessageResponse,
    summary="비밀번호 재설정 요청",
    description="비밀번호 재설정을 위한 링크를 이메일로 발송합니다.",
    responses={
        200: {
            "description": "재설정 링크 발송 성공",
            "content": {
                "application/json": {
                    "example": {
                        "success": True,
                        "message": "비밀번호 재설정 링크가 이메일로 발송되었습니다",
                        "detail": "개발 환경에서 재설정 토큰: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
                    }
                }
            }
        },
        **PASSWORD_RESET_RESPONSES
    }
)
async def request_password_reset(
    data: PasswordResetRequest,
    user_service: UserService = Depends(get_user_service)
):
    try:
        reset_token = await user_service.request_password_reset(data.email)
        logger.info(f"비밀번호 재설정 토큰 발급: {data.email}, 토큰: {reset_token}")

        return MessageResponse(
            success=True,
            message=MSG_PASSWORD_RESET_EMAIL_SENT,
            detail=f"개발 환경에서 재설정 토큰: {reset_token}"
        )
    except BaseAPIException as e:
        raise HTTPException(
            status_code=e.status_code,
            detail={"error": e.error_code, "detail": e.detail}
        )

@router.post(
    "/password/reset/confirm",
    response_model=MessageResponse,
    summary="비밀번호 재설정 확인",
    description="재설정 토큰을 확인하고 새 비밀번호로 변경합니다.",
    responses={
        200: {
            "description": "비밀번호 재설정 완료",
            "content": {
                "application/json": {
                    "example": {
                        "success": True,
                        "message": "비밀번호가 성공적으로 재설정되었습니다"
                    }
                }
            }
        },
        **PASSWORD_RESET_RESPONSES
    }
)
async def confirm_password_reset(
    data: PasswordResetConfirm,
    user_service: UserService = Depends(get_user_service)
):
    try:
        await user_service.confirm_password_reset(data)
        return MessageResponse(
            success=True,
            message=MSG_PASSWORD_RESET_SUCCESS
        )
    except BaseAPIException as e:
        raise HTTPException(
            status_code=e.status_code,
            detail={"error": e.error_code, "detail": e.detail}
        )

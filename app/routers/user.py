from fastapi import APIRouter, Query, Depends, HTTPException, UploadFile, File

from app.schemas.user import (
    UserResponse, UserUpdate, PasswordChangeRequest,
    NotificationResponse,
    UserProfileResponse
)
from app.schemas.common import MessageResponse, PaginatedResponse, SuccessResponse, ProfileImageUploadResponse
from app.exceptions.responses import (
    USER_UPDATE_RESPONSES,
    AUTH_RESPONSES,
)
from app.core.dependencies import get_current_user, get_user_service
from app.models.user import User
from app.services.user_service import UserService
from app.exceptions.base import BaseAPIException
import logging

router = APIRouter(prefix="/users", tags=["사용자"])
logger = logging.getLogger(__name__)

# ============================================================
# 1. 프로필 조회 및 수정
# ============================================================

@router.get(
    "/me",
    response_model=SuccessResponse[UserProfileResponse],
    summary="내 프로필 조회",
    description="현재 로그인한 사용자의 프로필 정보를 조회합니다.",
    responses={
        200: {
            "description": "사용자 정보 조회 성공",
            "content": {
                "application/json": {
                    "example": {
                        "success": True,
                        "message": "프로필 조회에 성공했습니다",
                        "data": {
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
                            "social_id": None,
                            "total_study_time": 1200,
                            "enrollment_expires_at": "2027-01-10T00:00:00Z"
                        }
                    }
                }
            }
        },
        **AUTH_RESPONSES
    }
)
async def get_my_profile(
    current_user: User = Depends(get_current_user),
    user_service: UserService = Depends(get_user_service)
):
    try:
        profile = await user_service.get_user_profile(current_user.id)
        return SuccessResponse(
            success=True,
            message="프로필 조회에 성공했습니다",
            data=profile
        )
    except BaseAPIException as e:
        raise HTTPException(
            status_code=e.status_code,
            detail={"error_code": e.error_code, "message": e.detail}
        )

@router.patch(
    "/me",
    response_model=SuccessResponse[UserResponse],
    summary="내 프로필 수정",
    description="현재 로그인한 사용자의 프로필 정보를 수정합니다.",
    responses={
        200: {
            "description": "프로필 수정 성공",
            "content": {
                "application/json": {
                    "example": {
                        "success": True,
                        "message": "프로필이 수정되었습니다",
                        "data": {
                            "id": 1,
                            "email": "hong@example.com",
                            "nickname": "새닉네임",
                            "gender": "male",
                            "birth_date": "1995-01-01",
                            "profile_image": None,
                            "role": "student",
                            "is_active": True,
                            "is_email_verified": True,
                            "created_at": "2025-01-01T00:00:00Z",
                            "updated_at": "2025-01-10T13:00:00Z",
                            "last_login": "2025-01-10T12:00:00Z",
                            "social_provider": "email",
                            "social_id": None
                        }
                    }
                }
            }
        },
        **USER_UPDATE_RESPONSES
    }
)
async def update_my_profile(
    data: UserUpdate,
    current_user: User = Depends(get_current_user),
    user_service: UserService = Depends(get_user_service)
):
    try:
        updated_user = await user_service.update_profile(current_user.id, data)
        return SuccessResponse(
            success=True,
            message="프로필이 수정되었습니다",
            data=updated_user
        )
    except BaseAPIException as e:
        raise HTTPException(
            status_code=e.status_code,
            detail={"error_code": e.error_code, "message": e.detail}
        )

# ============================================================
# 2. 프로필 이미지 관리
# ============================================================

@router.post(
    "/me/profile-image",
    response_model=SuccessResponse[ProfileImageUploadResponse],
    summary="프로필 이미지 업로드",
    description="현재 로그인한 사용자의 프로필 이미지를 업로드합니다.",
    responses={
        200: {
            "description": "프로필 이미지 업로드 성공",
            "content": {
                "application/json": {
                    "example": {
                        "success": True,
                        "message": "프로필 이미지가 업로드되었습니다",
                        "data": {
                            "image_url": "/uploads/profiles/abc123.jpg",
                            "file_size": 102400,
                            "uploaded_at": "2025-01-10T12:00:00Z"
                        }
                    }
                }
            }
        },
        **AUTH_RESPONSES,
        400: {
            "description": "잘못된 요청 (파일 크기 초과, 지원하지 않는 형식)",
            "content": {
                "application/json": {
                    "example": {
                        "error": "BAD_REQUEST",
                        "detail": "파일 크기는 5MB를 초과할 수 없습니다"
                    }
                }
            }
        }
    },
    openapi_extra={
        "requestBody": {
            "content": {
                "multipart/form-data": {
                    "schema": {
                        "type": "object",
                        "properties": {
                            "file": {
                                "type": "string",
                                "format": "binary",
                                "description": "업로드할 프로필 이미지 파일 (JPG, PNG, GIF, WEBP, 최대 5MB)"
                            }
                        },
                        "required": ["file"]
                    }
                }
            }
        }
    }
)
async def upload_profile_image(
    current_user: User = Depends(get_current_user),
    user_service: UserService = Depends(get_user_service),
    file: UploadFile = File(..., description="업로드할 프로필 이미지 파일 (JPG, PNG, GIF, WEBP, 최대 5MB)")
):
    try:
        result = await user_service.upload_profile_image(current_user.id, file)
        return SuccessResponse(
            success=True,
            message="프로필 이미지가 업로드되었습니다",
            data=result
        )
    except BaseAPIException as e:
        raise HTTPException(
            status_code=e.status_code,
            detail={"error_code": e.error_code, "message": e.detail}
        )

@router.delete(
    "/me/profile-image",
    response_model=MessageResponse,
    summary="프로필 이미지 삭제",
    description="현재 로그인한 사용자의 프로필 이미지를 삭제하고 기본 이미지로 변경합니다.",
    responses={
        200: {
            "description": "프로필 이미지 삭제 성공",
            "content": {
                "application/json": {
                    "example": {
                        "success": True,
                        "message": "프로필 이미지가 삭제되었습니다"
                    }
                }
            }
        },
        **AUTH_RESPONSES
    }
)
async def delete_profile_image(
    current_user: User = Depends(get_current_user),
    user_service: UserService = Depends(get_user_service)
):
    try:
        await user_service.delete_profile_image(current_user.id)
        return MessageResponse(
            success=True,
            message="프로필 이미지가 삭제되었습니다"
        )
    except BaseAPIException as e:
        raise HTTPException(
            status_code=e.status_code,
            detail={"error_code": e.error_code, "message": e.detail}
        )

# ============================================================
# 3. 비밀번호 변경
# ============================================================

@router.post(
    "/me/change-password",
    response_model=MessageResponse,
    summary="비밀번호 변경",
    description="현재 비밀번호를 확인하고 새 비밀번호로 변경합니다.",
    responses={
        200: {
            "description": "비밀번호 변경 완료",
            "content": {
                "application/json": {
                    "example": {
                        "success": True,
                        "message": "비밀번호가 변경되었습니다"
                    }
                }
            }
        },
        **AUTH_RESPONSES,
        400: {
            "description": "현재 비밀번호가 일치하지 않음",
            "content": {
                "application/json": {
                    "example": {
                        "error": "BAD_REQUEST",
                        "detail": "현재 비밀번호가 일치하지 않습니다"
                    }
                }
            }
        }
    }
)
async def change_password(
    data: PasswordChangeRequest,
    current_user: User = Depends(get_current_user),
    user_service: UserService = Depends(get_user_service)
):
    try:
        await user_service.change_password(current_user.id, data)
        return MessageResponse(
            success=True,
            message="비밀번호가 변경되었습니다"
        )
    except BaseAPIException as e:
        raise HTTPException(
            status_code=e.status_code,
            detail={"error_code": e.error_code, "message": e.detail}
        )

# ============================================================
# 4. 알림
# ============================================================

@router.post(
    "/me/profile-image",
    response_model=SuccessResponse[ProfileImageUploadResponse],
    summary="프로필 이미지 업로드",
    description="현재 로그인한 사용자의 프로필 이미지를 업로드합니다.",
    responses={
        200: {
            "description": "프로필 이미지 업로드 성공",
            "content": {
                "application/json": {
                    "example": {
                        "success": True,
                        "message": "프로필 이미지가 업로드되었습니다",
                        "data": {
                            "image_url": "/uploads/profiles/abc123.jpg",
                            "file_size": 102400,
                            "uploaded_at": "2025-01-10T12:00:00Z"
                        }
                    }
                }
            }
        },
        **AUTH_RESPONSES,
        400: {
            "description": "잘못된 요청 (파일 크기 초과, 지원하지 않는 형식)",
            "content": {
                "application/json": {
                    "example": {
                        "error": "BAD_REQUEST",
                        "detail": "파일 크기는 5MB를 초과할 수 없습니다"
                    }
                }
            }
        }
    }
)
async def upload_profile_image(
    file: UploadFile = File(..., description="업로드할 프로필 이미지 파일 (JPG, PNG, GIF, WEBP, 최대 5MB)"),
    current_user: User = Depends(get_current_user),
    user_service: UserService = Depends(get_user_service)
):
    try:
        result = await user_service.upload_profile_image(current_user.id, file)
        return SuccessResponse(
            success=True,
            message="프로필 이미지가 업로드되었습니다",
            data=result
        )
    except BaseAPIException as e:
        raise HTTPException(
            status_code=e.status_code,
            detail={"error_code": e.error_code, "message": e.detail}
        )

@router.delete(
    "/me/profile-image",
    response_model=MessageResponse,
    summary="프로필 이미지 삭제",
    description="현재 로그인한 사용자의 프로필 이미지를 삭제하고 기본 이미지로 변경합니다.",
    responses={
        200: {
            "description": "프로필 이미지 삭제 성공",
            "content": {
                "application/json": {
                    "example": {
                        "success": True,
                        "message": "프로필 이미지가 삭제되었습니다"
                    }
                }
            }
        },
        **AUTH_RESPONSES
    }
)
async def delete_profile_image(
    current_user: User = Depends(get_current_user),
    user_service: UserService = Depends(get_user_service)
):
    try:
        await user_service.delete_profile_image(current_user.id)
        return MessageResponse(
            success=True,
            message="프로필 이미지가 삭제되었습니다"
        )
    except BaseAPIException as e:
        raise HTTPException(
            status_code=e.status_code,
            detail={"error_code": e.error_code, "message": e.detail}
        )

@router.get(
    "/me/notifications",
    response_model=PaginatedResponse[NotificationResponse],
    summary="내 알림 목록",
    description="사용자의 알림 목록을 조회합니다.",
    responses={
        200: {
            "description": "알림 목록 조회 성공",
            "content": {
                "application/json": {
                    "example": {
                        "success": True,
                        "total": 10,
                        "page": 1,
                        "page_size": 20,
                        "total_pages": 1,
                        "items": [
                            {
                                "id": 1,
                                "user_id": 1,
                                "type": "expiry_warning",
                                "title": "수강 기간 만료 예정",
                                "content": "Python 기초 강의의 수강 기간이 7일 후 만료됩니다",
                                "is_read": False,
                                "related_url": "/courses/5",
                                "created_at": "2025-01-10T12:00:00Z"
                            }
                        ]
                    }
                }
            }
        },
        **AUTH_RESPONSES
    }
)
async def get_my_notifications(
    is_read: bool = Query(None, description="읽음 여부 필터"),
    page: int = Query(1, ge=1, description="페이지 번호"),
    page_size: int = Query(20, ge=1, le=100, description="페이지 크기"),
    current_user: User = Depends(get_current_user),
    user_service: UserService = Depends(get_user_service)
):
    try:
        result = await user_service.get_user_notifications(
            current_user.id,
            is_read,
            page,
            page_size
        )
        return result
    except BaseAPIException as e:
        raise HTTPException(
            status_code=e.status_code,
            detail={"error_code": e.error_code, "message": e.detail}
        )

# ============================================================
# 5. 회원 탈퇴
# ============================================================

@router.delete(
    "/me",
    response_model=MessageResponse,
    summary="회원 탈퇴",
    description="현재 사용자 계정을 삭제합니다. 이 작업은 되돌릴 수 없습니다.",
    responses={
        200: {
            "description": "회원 탈퇴 완료",
            "content": {
                "application/json": {
                    "example": {
                        "success": True,
                        "message": "회원 탈퇴가 완료되었습니다"
                    }
                }
            }
        },
        **AUTH_RESPONSES,
        400: {
            "description": "회원 탈퇴 조건 불충족",
            "content": {
                "application/json": {
                    "example": {
                        "error": "BAD_REQUEST",
                        "detail": "진행 중인 강의가 있어 탈퇴할 수 없습니다"
                    }
                }
            }
        }
    }
)
async def delete_account(
    password: str = Query(..., description="비밀번호 확인"),
    confirm_deletion: bool = Query(..., description="탈퇴 확인 (true만 허용)"),
    current_user: User = Depends(get_current_user),
    user_service: UserService = Depends(get_user_service)
):
    try:
        await user_service.delete_account(current_user.id, password, confirm_deletion)
        return MessageResponse(
            success=True,
            message="회원 탈퇴가 완료되었습니다"
        )
    except BaseAPIException as e:
        raise HTTPException(
            status_code=e.status_code,
            detail={"error_code": e.error_code, "message": e.detail}
        )

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

@router.get(
    "/me",
    response_model=SuccessResponse[UserProfileResponse],
    summary="내 프로필 조회",
    description="현재 로그인한 사용자의 프로필 정보를 조회합니다.",
    responses={
        200: {"description": "사용자 정보 조회 성공"},
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

@router.post(
    "/me/profile-image",
    response_model=SuccessResponse[ProfileImageUploadResponse],
    summary="프로필 이미지 업로드",
    description="프로필 이미지를 업로드합니다.",
    responses={
        200: {"description": "업로드 성공"},
        **AUTH_RESPONSES,
        400: {"description": "파일 오류"}
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
                                "description": "업로드할 프로필 이미지 (JPG, PNG, GIF, WEBP, 최대 5MB)"
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
    description="프로필 이미지를 삭제합니다.",
    responses={
        200: {"description": "삭제 성공"},
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

@router.post(
    "/me/change-password",
    response_model=MessageResponse,
    summary="비밀번호 변경",
    description="비밀번호를 변경합니다.",
    responses={
        200: {"description": "변경 완료"},
        **AUTH_RESPONSES,
        400: {"description": "비밀번호 오류"}
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


@router.delete(
    "/me",
    response_model=MessageResponse,
    summary="회원 탈퇴",
    description="사용자 계정을 삭제합니다.",
    responses={
        200: {"description": "탈퇴 완료"},
        **AUTH_RESPONSES,
        400: {"description": "탈퇴 불가능"}
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

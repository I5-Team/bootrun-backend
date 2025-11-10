from fastapi import APIRouter, UploadFile, File, Query, status, Depends, Path, Body, HTTPException

from app.schemas.user import (
    UserResponse, UserUpdate, PasswordChangeRequest,
    EmailChangeRequest, EmailChangeConfirm,
    ActivityResponse, NotificationResponse,
    UserProfileResponse
)
from app.schemas.common import MessageResponse, ProfileImageUploadResponse, PaginatedResponse, SuccessResponse
from app.exceptions.responses import (
    USER_UPDATE_RESPONSES,
    AUTH_RESPONSES,
    READ_RESPONSES,
    MODIFY_RESPONSES,
)
from app.core.dependencies import get_current_user, get_current_active_user, get_user_service
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
                            "gender": "MALE",
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
            detail={"error": e.error_code, "detail": e.detail}
        )

@router.get(
    "/{user_id}",
    response_model=SuccessResponse[UserResponse],
    summary="사용자 프로필 조회",
    description="특정 사용자의 프로필 정보를 조회합니다.",
    responses={
        200: {
            "description": "사용자 정보 조회 성공",
            "content": {
                "application/json": {
                    "example": {
                        "success": True,
                        "message": "사용자 정보 조회에 성공했습니다",
                        "data": {
                            "id": 1,
                            "email": "hong@example.com",
                            "nickname": "홍길동",
                            "gender": "MALE",
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
        },
        **READ_RESPONSES
    }
)
async def get_user_profile(
    user_id: int = Path(..., gt=0, description="사용자 ID"),
    user_service: UserService = Depends(get_user_service)
):
    try:
        user = await user_service.get_user_by_id(user_id)
        return SuccessResponse(
            success=True,
            message="사용자 정보 조회에 성공했습니다",
            data=UserResponse.model_validate(user)
        )
    except BaseAPIException as e:
        raise HTTPException(
            status_code=e.status_code,
            detail={"error": e.error_code, "detail": e.detail}
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
                            "gender": "MALE",
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
            detail={"error": e.error_code, "detail": e.detail}
        )

@router.post(
    "/me/profile-image",
    response_model=SuccessResponse[ProfileImageUploadResponse],
    status_code=status.HTTP_201_CREATED,
    summary="프로필 이미지 업로드",
    description="프로필 이미지를 업로드하고 URL을 반환합니다.",
    responses={
        201: {
            "description": "이미지 업로드 성공",
            "content": {
                "application/json": {
                    "example": {
                        "success": True,
                        "message": "프로필 이미지가 업로드되었습니다",
                        "data": {
                            "image_url": "/uploads/profiles/abc123.jpg",
                            "file_size": 102400,
                            "uploaded_at": "2025-01-10T13:00:00Z"
                        }
                    }
                }
            }
        },
        **AUTH_RESPONSES,
        413: {
            "description": "파일 크기가 너무 큼",
            "content": {
                "application/json": {
                    "example": {
                        "error": "FILE_TOO_LARGE",
                        "detail": "파일 크기는 5MB를 초과할 수 없습니다"
                    }
                }
            }
        }
    }
)
async def upload_profile_image(
    file: UploadFile = File(..., description="프로필 이미지 파일"),
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
            detail={"error": e.error_code, "detail": e.detail}
        )

@router.delete(
    "/me/profile-image",
    response_model=MessageResponse,
    summary="프로필 이미지 삭제",
    description="현재 설정된 프로필 이미지를 삭제하고 기본 이미지로 변경합니다.",
    responses={
        200: {
            "description": "이미지 삭제 성공",
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
            detail={"error": e.error_code, "detail": e.detail}
        )

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
            detail={"error": e.error_code, "detail": e.detail}
        )

@router.post(
    "/me/change-email/request",
    response_model=MessageResponse,
    summary="이메일 변경 요청",
    description="새 이메일 주소로 인증 코드를 발송합니다.",
    responses={
        200: {
            "description": "인증 코드 발송 성공",
            "content": {
                "application/json": {
                    "example": {
                        "success": True,
                        "message": "새 이메일로 인증 코드가 발송되었습니다",
                        "detail": "개발 환경에서 인증 코드: 123456"
                    }
                }
            }
        },
        **AUTH_RESPONSES
    }
)
async def request_email_change(
    data: EmailChangeRequest,
    current_user: User = Depends(get_current_user),
    user_service: UserService = Depends(get_user_service)
):
    try:
        verification_code = await user_service.request_email_change(current_user.id, data.new_email)
        logger.info(f"이메일 변경 인증 코드: {current_user.email} -> {data.new_email}, 코드: {verification_code}")
        return MessageResponse(
            success=True,
            message="새 이메일로 인증 코드가 발송되었습니다",
            detail=f"개발 환경에서 인증 코드: {verification_code}"
        )
    except BaseAPIException as e:
        raise HTTPException(
            status_code=e.status_code,
            detail={"error": e.error_code, "detail": e.detail}
        )

@router.post(
    "/me/change-email/confirm",
    response_model=MessageResponse,
    summary="이메일 변경 확인",
    description="인증 코드를 확인하고 이메일을 변경합니다.",
    responses={
        200: {
            "description": "이메일 변경 완료",
            "content": {
                "application/json": {
                    "example": {
                        "success": True,
                        "message": "이메일이 변경되었습니다"
                    }
                }
            }
        },
        **AUTH_RESPONSES
    }
)
async def confirm_email_change(
    data: EmailChangeConfirm,
    current_user: User = Depends(get_current_user),
    user_service: UserService = Depends(get_user_service)
):
    try:
        await user_service.confirm_email_change(current_user.id, data)
        return MessageResponse(
            success=True,
            message="이메일이 변경되었습니다"
        )
    except BaseAPIException as e:
        raise HTTPException(
            status_code=e.status_code,
            detail={"error": e.error_code, "detail": e.detail}
        )

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
            detail={"error": e.error_code, "detail": e.detail}
        )

@router.get(
    "/me/activities",
    response_model=PaginatedResponse[ActivityResponse],
    summary="내 활동 내역",
    description="사용자의 최근 활동 내역을 조회합니다.",
    responses={
        200: {
            "description": "활동 내역 조회 성공",
            "content": {
                "application/json": {
                    "example": {
                        "success": True,
                        "total": 50,
                        "page": 1,
                        "page_size": 20,
                        "total_pages": 3,
                        "items": [
                            {
                                "id": 1,
                                "activity_type": "enrollment",
                                "title": "강의 수강 등록",
                                "description": "강의 ID: 5",
                                "created_at": "2025-01-10T12:00:00Z",
                                "related_id": 5
                            }
                        ]
                    }
                }
            }
        },
        **AUTH_RESPONSES
    }
)
async def get_my_activities(
    activity_type: str = Query(None, description="활동 유형 필터 (question/comment/enrollment/payment)"),
    page: int = Query(1, ge=1, description="페이지 번호"),
    page_size: int = Query(20, ge=1, le=100, description="페이지 크기"),
    current_user: User = Depends(get_current_user),
    user_service: UserService = Depends(get_user_service)
):
    try:
        result = await user_service.get_user_activities(
            current_user.id,
            activity_type,
            page,
            page_size
        )
        return result
    except BaseAPIException as e:
        raise HTTPException(
            status_code=e.status_code,
            detail={"error": e.error_code, "detail": e.detail}
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
            detail={"error": e.error_code, "detail": e.detail}
        )

@router.patch(
    "/me/notifications/{notification_id}/read",
    response_model=SuccessResponse[NotificationResponse],
    summary="알림 읽음 처리",
    description="특정 알림을 읽음 상태로 변경합니다.",
    responses={
        200: {
            "description": "알림 읽음 처리 완료",
            "content": {
                "application/json": {
                    "example": {
                        "success": True,
                        "message": "알림이 읽음 처리되었습니다",
                        "data": {
                            "id": 1,
                            "user_id": 1,
                            "type": "expiry_warning",
                            "title": "수강 기간 만료 예정",
                            "content": "Python 기초 강의의 수강 기간이 7일 후 만료됩니다",
                            "is_read": True,
                            "related_url": "/courses/5",
                            "created_at": "2025-01-10T12:00:00Z"
                        }
                    }
                }
            }
        },
        **MODIFY_RESPONSES
    }
)
async def mark_notification_as_read(
    notification_id: int = Path(..., gt=0, description="알림 ID"),
    current_user: User = Depends(get_current_user),
    user_service: UserService = Depends(get_user_service)
):
    try:
        notification = await user_service.mark_notification_as_read(current_user.id, notification_id)
        return SuccessResponse(
            success=True,
            message="알림이 읽음 처리되었습니다",
            data=notification
        )
    except BaseAPIException as e:
        raise HTTPException(
            status_code=e.status_code,
            detail={"error": e.error_code, "detail": e.detail}
        )

@router.post(
    "/me/notifications/read-all",
    response_model=MessageResponse,
    summary="모든 알림 읽음 처리",
    description="모든 알림을 읽음 상태로 변경합니다.",
    responses={
        200: {
            "description": "모든 알림 읽음 처리 완료",
            "content": {
                "application/json": {
                    "example": {
                        "success": True,
                        "message": "모든 알림이 읽음 처리되었습니다"
                    }
                }
            }
        },
        **AUTH_RESPONSES
    }
)
async def mark_all_notifications_as_read(
    current_user: User = Depends(get_current_user),
    user_service: UserService = Depends(get_user_service)
):
    try:
        await user_service.mark_all_notifications_as_read(current_user.id)
        return MessageResponse(
            success=True,
            message="모든 알림이 읽음 처리되었습니다"
        )
    except BaseAPIException as e:
        raise HTTPException(
            status_code=e.status_code,
            detail={"error": e.error_code, "detail": e.detail}
        )

@router.post(
    "/restore",
    response_model=MessageResponse,
    summary="계정 복구",
    description="탈퇴한 계정을 복구합니다. (탈퇴 후 30일 이내만 가능)",
    responses={
        200: {
            "description": "계정 복구 완료",
            "content": {
                "application/json": {
                    "example": {
                        "success": True,
                        "message": "계정이 복구되었습니다"
                    }
                }
            }
        },
        **READ_RESPONSES,
        400: {
            "description": "계정 복구 불가",
            "content": {
                "application/json": {
                    "example": {
                        "error": "BAD_REQUEST",
                        "detail": "복구 가능 기간이 지났습니다"
                    }
                }
            }
        }
    }
)
async def restore_account(
    email: str = Body(..., description="이메일 주소"),
    password: str = Body(..., description="비밀번호"),
    user_service: UserService = Depends(get_user_service)
):
    try:
        await user_service.restore_account(email, password)
        return MessageResponse(
            success=True,
            message="계정이 복구되었습니다"
        )
    except BaseAPIException as e:
        raise HTTPException(
            status_code=e.status_code,
            detail={"error": e.error_code, "detail": e.detail}
        )
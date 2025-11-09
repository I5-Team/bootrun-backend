from fastapi import APIRouter, UploadFile, File, Query, status, Depends, Path, Body
from sqlalchemy.orm import Session

from app.schemas.user import (
    UserResponse, UserUpdate, PasswordChangeRequest,
    EmailChangeRequest, EmailChangeConfirm,
    ActivityResponse, NotificationResponse
)
from app.schemas.common import MessageResponse, ProfileImageUploadResponse, PaginatedResponse, SuccessResponse
from app.exceptions.responses import (
    USER_UPDATE_RESPONSES,
    AUTH_RESPONSES,
    READ_RESPONSES,
    MODIFY_RESPONSES,
)
from app.core.dependencies import get_current_user, get_current_active_user
from app.core.database import get_db
from app.models.user import User

router = APIRouter(prefix="/users", tags=["사용자"])

@router.get(
    "/me",
    response_model=SuccessResponse[UserResponse],
    summary="내 프로필 조회",
    description="현재 로그인한 사용자의 프로필 정보를 조회합니다.",
    responses={
        200: {"description": "사용자 정보 조회 성공"},
        **AUTH_RESPONSES
    }
)
async def get_my_profile(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    pass

@router.get(
    "/{user_id}",
    response_model=SuccessResponse[UserResponse],
    summary="사용자 프로필 조회",
    description="특정 사용자의 프로필 정보를 조회합니다.",
    responses={
        200: {"description": "사용자 정보 조회 성공"},
        **READ_RESPONSES
    }
)
async def get_user_profile(
    user_id: int = Path(..., gt=0, description="사용자 ID"),
    db: Session = Depends(get_db)
):
    pass

@router.patch(
    "/me",
    response_model=SuccessResponse[UserResponse],
    summary="내 프로필 수정",
    description="현재 로그인한 사용자의 프로필 정보를 수정합니다.",
    responses={
        200: {"description": "프로필 수정 성공"},
        **USER_UPDATE_RESPONSES
    }
)
async def update_my_profile(
    data: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    pass

@router.post(
    "/me/profile-image",
    response_model=SuccessResponse[ProfileImageUploadResponse],
    status_code=status.HTTP_201_CREATED,
    summary="프로필 이미지 업로드",
    description="프로필 이미지를 업로드하고 URL을 반환합니다.",
    responses={
        201: {"description": "이미지 업로드 성공"},
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
    db: Session = Depends(get_db)
):
    pass

@router.delete(
    "/me/profile-image",
    response_model=MessageResponse,
    summary="프로필 이미지 삭제",
    description="현재 설정된 프로필 이미지를 삭제하고 기본 이미지로 변경합니다.",
    responses={
        200: {"description": "이미지 삭제 성공"},
        **AUTH_RESPONSES
    }
)
async def delete_profile_image(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    pass

@router.post(
    "/me/change-password",
    response_model=MessageResponse,
    summary="비밀번호 변경",
    description="현재 비밀번호를 확인하고 새 비밀번호로 변경합니다.",
    responses={
        200: {"description": "비밀번호 변경 완료"},
        **AUTH_RESPONSES,
        400: {
            "description": "현재 비밀번호가 일치하지 않음",
            "content": {
                "application/json": {
                    "example": {
                        "error": "INVALID_PASSWORD",
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
    db: Session = Depends(get_db)
):
    pass

@router.post(
    "/me/change-email/request",
    response_model=MessageResponse,
    summary="이메일 변경 요청",
    description="새 이메일 주소로 인증 코드를 발송합니다.",
    responses={
        200: {"description": "인증 코드 발송 성공"},
        **AUTH_RESPONSES
    }
)
async def request_email_change(
    data: EmailChangeRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    pass

@router.post(
    "/me/change-email/confirm",
    response_model=MessageResponse,
    summary="이메일 변경 확인",
    description="인증 코드를 확인하고 이메일을 변경합니다.",
    responses={
        200: {"description": "이메일 변경 완료"},
        **AUTH_RESPONSES
    }
)
async def confirm_email_change(
    data: EmailChangeConfirm,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    pass

@router.delete(
    "/me",
    response_model=MessageResponse,
    summary="회원 탈퇴",
    description="현재 사용자 계정을 삭제합니다. 이 작업은 되돌릴 수 없습니다.",
    responses={
        200: {"description": "회원 탈퇴 완료"},
        **AUTH_RESPONSES,
        400: {
            "description": "회원 탈퇴 조건 불충족",
            "content": {
                "application/json": {
                    "example": {
                        "error": "DELETION_NOT_ALLOWED",
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
    db: Session = Depends(get_db)
):
    pass

@router.get(
    "/me/activities",
    response_model=PaginatedResponse[ActivityResponse],
    summary="내 활동 내역",
    description="사용자의 최근 활동 내역을 조회합니다.",
    responses={
        200: {"description": "활동 내역 조회 성공"},
        **AUTH_RESPONSES
    }
)
async def get_my_activities(
    activity_type: str = Query(None, description="활동 유형 필터 (question/comment/enrollment/payment)"),
    page: int = Query(1, ge=1, description="페이지 번호"),
    page_size: int = Query(20, ge=1, le=100, description="페이지 크기"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    pass

@router.get(
    "/me/notifications",
    response_model=PaginatedResponse[NotificationResponse],
    summary="내 알림 목록",
    description="사용자의 알림 목록을 조회합니다.",
    responses={
        200: {"description": "알림 목록 조회 성공"},
        **AUTH_RESPONSES
    }
)
async def get_my_notifications(
    is_read: bool = Query(None, description="읽음 여부 필터"),
    page: int = Query(1, ge=1, description="페이지 번호"),
    page_size: int = Query(20, ge=1, le=100, description="페이지 크기"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    pass

@router.patch(
    "/me/notifications/{notification_id}/read",
    response_model=SuccessResponse[NotificationResponse],
    summary="알림 읽음 처리",
    description="특정 알림을 읽음 상태로 변경합니다.",
    responses={
        200: {"description": "알림 읽음 처리 완료"},
        **MODIFY_RESPONSES
    }
)
async def mark_notification_as_read(
    notification_id: int = Path(..., gt=0, description="알림 ID"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    pass

@router.post(
    "/me/notifications/read-all",
    response_model=MessageResponse,
    summary="모든 알림 읽음 처리",
    description="모든 알림을 읽음 상태로 변경합니다.",
    responses={
        200: {"description": "모든 알림 읽음 처리 완료"},
        **AUTH_RESPONSES
    }
)
async def mark_all_notifications_as_read(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    pass

@router.post(
    "/restore",
    response_model=MessageResponse,
    summary="계정 복구",
    description="탈퇴한 계정을 복구합니다. (탈퇴 후 30일 이내만 가능)",
    responses={
        200: {"description": "계정 복구 완료"},
        **READ_RESPONSES,
        400: {
            "description": "계정 복구 불가",
            "content": {
                "application/json": {
                    "example": {
                        "error": "RESTORE_NOT_ALLOWED",
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
    db: Session = Depends(get_db)
):
    pass
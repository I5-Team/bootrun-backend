from fastapi import APIRouter, Depends, status
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.admin import (
    UserManagementListParams, UserManagementPaginatedResponse,
    UserDetailForAdmin, UserLearningReport
)
from app.schemas.common import MessageResponse, SuccessResponse
from app.exceptions.responses import (
    ADMIN_USER_MANAGEMENT_RESPONSES,
    ADMIN_RESPONSES,
)
from app.core.dependencies import get_current_admin, get_db
from app.models.user import User
from app.services.admin_user_service import AdminUserService
from app.exceptions.base import BadRequestError, NotFoundError

router = APIRouter(prefix="/admin/users", tags=["관리자 - 사용자 관리"])

@router.get(
    "/export",
    summary="사용자 목록 내보내기",
    description="사용자 목록을 CSV 파일로 내보냅니다.",
    responses={
        200: {"description": "사용자 목록 내보내기 완료"},
        **ADMIN_RESPONSES
    }
)
async def export_users(
    params: UserManagementListParams = Depends(),
    current_admin: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db)
):
    pass

@router.patch(
    "/{user_id}/activate",
    response_model=MessageResponse,
    summary="사용자 활성화",
    description="비활성화된 사용자를 활성화합니다.",
    responses={
        200: {"description": "사용자 활성화 완료"},
        **ADMIN_USER_MANAGEMENT_RESPONSES
    }
)
async def activate_user(
    user_id: int,
    current_admin: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db)
):
    service = AdminUserService(db)
    try:
        await service.activate_user(user_id)
    except NotFoundError:
        raise
    except ValueError as e:
        raise BadRequestError(str(e))

    return MessageResponse(
        success=True,
        message="사용자가 성공적으로 활성화되었습니다"
    )

@router.patch(
    "/{user_id}/deactivate",
    response_model=MessageResponse,
    summary="사용자 비활성화",
    description="사용자를 비활성화합니다.",
    responses={
        200: {"description": "사용자 비활성화 완료"},
        **ADMIN_USER_MANAGEMENT_RESPONSES
    }
)
async def deactivate_user(
    user_id: int,
    current_admin: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db)
):
    service = AdminUserService(db)
    try:
        await service.deactivate_user(user_id)
    except NotFoundError:
        raise
    except ValueError as e:
        raise BadRequestError(str(e))

    return MessageResponse(
        success=True,
        message="사용자가 성공적으로 비활성화되었습니다"
    )

@router.get(
    "/{user_id}/learning-report",
    response_model=SuccessResponse[UserLearningReport],
    summary="사용자 학습 리포트",
    description="사용자의 학습 리포트를 조회합니다.",
    responses={
        200: {"description": "학습 리포트 조회 성공"},
        **ADMIN_USER_MANAGEMENT_RESPONSES
    }
)
async def get_user_learning_report(
    user_id: int,
    report_period: str,
    current_admin: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db)
):
    service = AdminUserService(db)
    try:
        report = await service.get_user_learning_report(user_id, report_period)
    except NotFoundError:
        raise
    except ValueError as e:
        raise BadRequestError(str(e))

    return SuccessResponse(
        success=True,
        data=report
    )

@router.get(
    "",
    response_model=UserManagementPaginatedResponse,
    summary="사용자 목록 조회",
    description="전체 사용자 목록을 조회합니다.",
    responses={
        200: {"description": "사용자 목록 조회 성공"},
        **ADMIN_RESPONSES
    }
)
async def get_users(
    params: UserManagementListParams = Depends(),
    current_admin: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db)
):
    service = AdminUserService(db)
    return await service.get_users_list(params)

@router.get(
    "/{user_id}",
    response_model=SuccessResponse[UserDetailForAdmin],
    summary="사용자 상세 조회",
    description="특정 사용자의 상세 정보를 조회합니다.",
    responses={
        200: {"description": "사용자 상세 조회 성공"},
        **ADMIN_USER_MANAGEMENT_RESPONSES
    }
)
async def get_user(
    user_id: int,
    current_admin: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db)
):
    service = AdminUserService(db)
    try:
        user_detail = await service.get_user_detail(user_id)
    except NotFoundError:
        raise

    return SuccessResponse(
        success=True,
        data=user_detail
    )

@router.delete(
    "/{user_id}",
    response_model=MessageResponse,
    summary="사용자 삭제",
    description="사용자를 완전히 삭제합니다.",
    responses={
        200: {"description": "사용자 삭제 완료"},
        **ADMIN_USER_MANAGEMENT_RESPONSES
    }
)
async def delete_user(
    user_id: int,
    current_admin: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db)
):
    service = AdminUserService(db)
    try:
        await service.delete_user(user_id)
    except NotFoundError:
        raise
    except ValueError as e:
        raise BadRequestError(str(e))

    return MessageResponse(
        success=True,
        message="사용자가 성공적으로 삭제되었습니다"
    )

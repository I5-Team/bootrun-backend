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

# ================== 1. 고정 경로 (먼저 정의) ==================

@router.get(
    "/export",
    summary="사용자 목록 내보내기",
    description="사용자 목록을 엑셀 파일로 내보냅니다.",
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

# ================== 2. 구체적인 동작 경로 ({user_id}/특정_동작) ==================

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
    """사용자 활성화

    - 비활성화된 사용자를 다시 활성화합니다
    - 활성화 후 사용자는 로그인 가능
    """
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
    """사용자 비활성화

    - 사용자를 비활성화합니다
    - 비활성화된 사용자는 로그인 불가
    """
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
    """사용자 학습 리포트 조회

    - report_period 형식: YYYY-MM (예: 2025-01)
    - 월별 총 학습 시간 조회
    - 강의별 진도 현황 조회
    - 출석 현황 조회
    """
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

# ================== 3. 일반 경로 (가장 나중에 정의) ==================

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
    """사용자 목록 조회

    - 역할, 활성화 상태, 키워드, 가입 기간으로 필터링 가능
    - 페이지네이션 지원
    - 각 사용자의 수강 등록 수, 결제 횟수, 총 지출액 포함
    """
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
    """사용자 상세 정보 조회

    - 사용자 기본 정보 (이메일, 닉네임, 성별, 생년월일 등)
    - 학습 통계 (총 학습 시간, 수강 등록 수, 완료한 강의 수 등)
    - 결제 정보 (총 결제 횟수, 총 지출액, 환불액)
    - 활동 정보 (작성한 질문, 댓글 수)
    - 수강 중인 강의 목록
    """
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
    """사용자 완전 삭제

    - 사용자를 완전히 삭제합니다 (카스케이드 삭제)
    - 연결된 모든 데이터도 함께 삭제됩니다 (주의!)
    """
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

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.common import MessageResponse, PaginatedResponse, SuccessResponse
from app.schemas.payment import (
    CouponCreate,
    CouponUpdate,
    CouponResponse,
    CouponListParams
)
from app.exceptions.responses import (
    ADMIN_RESPONSES,
    ADMIN_COUPON_LIST_RESPONSES,
    ADMIN_COUPON_DETAIL_RESPONSES,
    COUPON_CREATE_RESPONSES,
    COUPON_UPDATE_RESPONSES,
    COUPON_DELETE_RESPONSES,
)
from app.core.dependencies import get_current_admin, get_db
from app.models.user import User

router = APIRouter(prefix="/admin/coupons", tags=["관리자 - 쿠폰 관리"])

@router.get(
    "",
    response_model=PaginatedResponse[CouponResponse],
    summary="쿠폰 목록 조회",
    description="전체 쿠폰 목록을 조회합니다.",
    operation_id="admin_get_coupons",
    responses={
        200: {"description": "쿠폰 목록 조회 성공"},
        **ADMIN_COUPON_LIST_RESPONSES
    }
)
async def get_coupons(
    params: CouponListParams = Depends(),
    current_admin: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db)
):
    pass

@router.get(
    "/{coupon_id}",
    response_model=SuccessResponse[CouponResponse],
    summary="쿠폰 상세 조회",
    description="특정 쿠폰의 상세 정보를 조회합니다.",
    operation_id="admin_get_coupon",
    responses={
        200: {"description": "쿠폰 상세 조회 성공"},
        **ADMIN_COUPON_DETAIL_RESPONSES
    }
)
async def get_coupon(
    coupon_id: int,
    current_admin: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db)
):
    pass

@router.post(
    "",
    response_model=SuccessResponse[CouponResponse],
    status_code=status.HTTP_201_CREATED,
    summary="쿠폰 생성",
    description="새로운 쿠폰을 생성합니다.",
    responses={
        201: {"description": "쿠폰 생성 성공"},
        **COUPON_CREATE_RESPONSES
    }
)
async def create_coupon(
    data: CouponCreate,
    current_admin: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db)
):
    pass

@router.patch(
    "/{coupon_id}",
    response_model=SuccessResponse[CouponResponse],
    summary="쿠폰 수정",
    description="쿠폰 정보를 수정합니다.",
    responses={
        200: {"description": "쿠폰 수정 성공"},
        **COUPON_UPDATE_RESPONSES
    }
)
async def update_coupon(
    coupon_id: int,
    data: CouponUpdate,
    current_admin: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db)
):
    pass

@router.delete(
    "/{coupon_id}",
    response_model=MessageResponse,
    summary="쿠폰 삭제",
    description="쿠폰을 삭제합니다.",
    responses={
        200: {"description": "쿠폰 삭제 완료"},
        **COUPON_DELETE_RESPONSES
    }
)
async def delete_coupon(
    coupon_id: int,
    current_admin: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db)
):
    pass
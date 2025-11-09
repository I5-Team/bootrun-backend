from fastapi import APIRouter, Depends, status
from app.schemas.payment import (
    CouponResponse, CouponListParams,
    CouponValidationRequest, CouponValidationResponse
)
from app.schemas.common import SuccessResponse
from app.exceptions.responses import (
    COUPON_VALIDATE_RESPONSES,
    AUTH_RESPONSES,
    READ_RESPONSES,
)
from app.core.dependencies import get_current_user
from app.models.user import User

router = APIRouter(prefix="/coupons", tags=["쿠폰"])

@router.get(
    "",
    response_model=SuccessResponse[list[CouponResponse]],
    summary="쿠폰 목록 조회",
    description="사용 가능한 쿠폰 목록을 조회합니다.",
    responses={
        200: {"description": "쿠폰 목록 조회 성공"},
        **READ_RESPONSES
    }
)
async def get_coupons(params: CouponListParams = Depends()):
    pass

@router.get(
    "/{coupon_id}",
    response_model=SuccessResponse[CouponResponse],
    summary="쿠폰 상세 조회",
    description="특정 쿠폰의 상세 정보를 조회합니다.",
    responses={
        200: {"description": "쿠폰 상세 조회 성공"},
        **READ_RESPONSES
    }
)
async def get_coupon(coupon_id: int):
    pass

@router.post(
    "/validate",
    response_model=SuccessResponse[CouponValidationResponse],
    summary="쿠폰 유효성 검증",
    description="결제 시 쿠폰 코드의 유효성을 검증하고 할인 금액을 계산합니다.",
    responses={
        200: {"description": "쿠폰 유효성 검증 완료"},
        **COUPON_VALIDATE_RESPONSES
    }
)
async def validate_coupon(
    data: CouponValidationRequest,
    current_user: User = Depends(get_current_user)
):
    pass

@router.get(
    "/my",
    response_model=SuccessResponse[list[CouponResponse]],
    summary="내 쿠폰 목록",
    description="사용자가 사용할 수 있는 쿠폰 목록을 조회합니다.",
    responses={
        200: {"description": "내 쿠폰 목록 조회 성공"},
        **AUTH_RESPONSES
    }
)
async def get_my_coupons(current_user: User = Depends(get_current_user)):
    pass
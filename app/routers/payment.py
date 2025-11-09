from fastapi import APIRouter, Depends, status, Path
from sqlalchemy.orm import Session

from app.schemas.payment import (
    # Payment schemas
    PaymentCreate, PaymentResponse, PaymentDetailResponse,
    PaymentPaginatedResponse, PaymentListParams, PaymentConfirmRequest,
    # Refund schemas
    RefundCreate, RefundResponse, RefundCheckResponse
)
from app.schemas.common import MessageResponse
from app.exceptions.responses import (
    PAYMENT_CREATE_RESPONSES,
    PAYMENT_CONFIRM_RESPONSES,
    REFUND_CREATE_RESPONSES,
    AUTH_RESPONSES,
    AUTH_PERMISSION_RESPONSES,
    MODIFY_RESPONSES,
)
from app.core.dependencies import get_current_user, get_current_active_user
from app.core.database import get_db
from app.models.user import User

router = APIRouter(prefix="/payments", tags=["결제 및 환불"])

# ============= 결제 API =============

@router.post(
    "",
    response_model=PaymentResponse,
    status_code=status.HTTP_201_CREATED,
    summary="결제 생성",
    description="강의 결제를 생성합니다. PG사 결제 페이지로 리다이렉트할 정보를 반환합니다.",
    responses={
        201: {"description": "결제 생성 성공"},
        **PAYMENT_CREATE_RESPONSES
    }
)
async def create_payment(
    data: PaymentCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    # TODO: 서비스 로직 구현
    pass

@router.get(
    "",
    response_model=PaymentPaginatedResponse,
    summary="결제 목록 조회",
    description="사용자의 결제 내역을 조회합니다.",
    responses={
        200: {"description": "결제 목록 조회 성공"},
        **AUTH_RESPONSES
    }
)
async def get_payments(
    params: PaymentListParams = Depends(),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # TODO: 서비스 로직 구현
    pass

@router.get(
    "/{payment_id}",
    response_model=PaymentDetailResponse,
    summary="결제 상세 조회",
    description="특정 결제의 상세 정보를 조회합니다.",
    responses={
        200: {"description": "결제 상세 조회 성공"},
        **AUTH_PERMISSION_RESPONSES
    }
)
async def get_payment(
    payment_id: int = Path(..., gt=0, description="결제 ID"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # TODO: 서비스 로직 구현
    pass

@router.post(
    "/{payment_id}/confirm",
    response_model=PaymentResponse,
    summary="결제 확인",
    description="PG사에서 결제 완료 후 최종 확인을 진행합니다.",
    responses={
        200: {"description": "결제 확인 완료"},
        **PAYMENT_CONFIRM_RESPONSES
    }
)
async def confirm_payment(
    payment_id: int = Path(..., gt=0, description="결제 ID"),
    data: PaymentConfirmRequest = ...,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # TODO: 서비스 로직 구현
    pass

@router.post(
    "/{payment_id}/cancel",
    response_model=MessageResponse,
    summary="결제 취소",
    description="결제를 취소합니다. 완료되지 않은 결제만 취소 가능합니다.",
    responses={
        200: {"description": "결제 취소 완료"},
        **MODIFY_RESPONSES,
        400: {
            "description": "결제 취소 불가",
            "content": {
                "application/json": {
                    "example": {
                        "error": "CANCEL_NOT_ALLOWED",
                        "detail": "완료된 결제는 취소할 수 없습니다"
                    }
                }
            }
        }
    }
)
async def cancel_payment(
    payment_id: int = Path(..., gt=0, description="결제 ID"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # TODO: 서비스 로직 구현
    pass

@router.get(
    "/{payment_id}/refund-check",
    response_model=RefundCheckResponse,
    summary="환불 가능 여부 확인",
    description="결제의 환불 가능 여부와 사유를 확인합니다.",
    responses={
        200: {"description": "환불 가능 여부 확인 완료"},
        **MODIFY_RESPONSES
    }
)
async def check_refund_eligibility(
    payment_id: int = Path(..., gt=0, description="결제 ID"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # TODO: 서비스 로직 구현
    pass

# ============= 환불 API =============

@router.post(
    "/refunds",
    response_model=RefundResponse,
    status_code=status.HTTP_201_CREATED,
    summary="환불 요청",
    description="결제에 대한 환불을 요청합니다.",
    responses={
        201: {"description": "환불 요청 성공"},
        **REFUND_CREATE_RESPONSES
    }
)
async def create_refund(
    data: RefundCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    # TODO: 서비스 로직 구현
    pass

@router.get(
    "/refunds/my",
    response_model=list[RefundResponse],
    summary="내 환불 요청 목록",
    description="사용자의 환불 요청 내역을 조회합니다.",
    responses={
        200: {"description": "환불 목록 조회 성공"},
        **AUTH_RESPONSES
    }
)
async def get_my_refunds(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # TODO: 서비스 로직 구현
    pass

@router.get(
    "/refunds/{refund_id}",
    response_model=RefundResponse,
    summary="환불 상세 조회",
    description="특정 환불 요청의 상세 정보를 조회합니다.",
    responses={
        200: {"description": "환불 상세 조회 성공"},
        **AUTH_PERMISSION_RESPONSES
    }
)
async def get_refund(
    refund_id: int = Path(..., gt=0, description="환불 ID"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # TODO: 서비스 로직 구현
    pass

@router.delete(
    "/refunds/{refund_id}",
    response_model=MessageResponse,
    summary="환불 요청 취소",
    description="대기 중인 환불 요청을 취소합니다.",
    responses={
        200: {"description": "환불 요청 취소 완료"},
        **MODIFY_RESPONSES,
        400: {
            "description": "환불 취소 불가",
            "content": {
                "application/json": {
                    "example": {
                        "error": "REFUND_CANCEL_NOT_ALLOWED",
                        "detail": "처리 중이거나 완료된 환불은 취소할 수 없습니다"
                    }
                }
            }
        }
    }
)
async def cancel_refund(
    refund_id: int = Path(..., gt=0, description="환불 ID"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # TODO: 서비스 로직 구현
    pass
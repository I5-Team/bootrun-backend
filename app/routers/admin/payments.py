from fastapi import APIRouter, Depends, Path
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.admin import (
    PaymentManagementListParams, PaymentManagementPaginatedResponse,
    RefundManagementListParams, RefundManagementPaginatedResponse
)
from app.schemas.payment import RefundUpdate, RefundResponse
from app.schemas.common import SuccessResponse
from app.exceptions.responses import (
    ADMIN_REFUND_LIST_RESPONSES,
    ADMIN_REFUND_DETAIL_RESPONSES,
    REFUND_UPDATE_RESPONSES,
    ADMIN_RESPONSES,
)
from app.core.dependencies import get_current_admin, get_db
from app.models.user import User
from app.services.payment_service import AdminPaymentService

router = APIRouter(prefix="/admin/payments", tags=["관리자 - 결제 및 환불 관리"])

@router.get(
    "",
    response_model=PaymentManagementPaginatedResponse,
    summary="결제 목록 조회",
    description="전체 결제 내역을 조회합니다.",
    responses={
        200: {"description": "결제 목록 조회 성공"},
        **ADMIN_RESPONSES
    }
)
async def get_payments(
    params: PaymentManagementListParams = Depends(),
    current_admin: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db)
):
    """
    전체 결제 목록 조회 (관리자용)
    - 필터링: 상태, 결제 방식, 날짜 범위
    - 검색: 사용자명, 이메일, 강의명
    - 페이지네이션
    """
    service = AdminPaymentService(db)
    result = await service.get_payments(params)
    return PaymentManagementPaginatedResponse(
        total=result["total"],
        page=result["page"],
        page_size=result["page_size"],
        total_pages=result["total_pages"],
        items=result["items"]
    )

@router.get(
    "/export",
    summary="결제 내역 내보내기",
    description="결제 내역을 엑셀 파일로 내보냅니다.",
    responses={
        200: {"description": "결제 내역 내보내기 완료"},
        **ADMIN_RESPONSES
    }
)
async def export_payments(
    params: PaymentManagementListParams = Depends(),
    current_admin: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db)
):
    """
    결제 내역 내보내기 (엑셀용)
    """
    service = AdminPaymentService(db)
    items = await service.export_payments(params)
    return {"data": items}

@router.get(
    "/refunds",
    response_model=RefundManagementPaginatedResponse,
    summary="환불 목록 조회",
    description="환불 요청 목록을 조회합니다.",
    responses={
        200: {"description": "환불 목록 조회 성공"},
        **ADMIN_REFUND_LIST_RESPONSES
    }
)
async def get_refunds(
    params: RefundManagementListParams = Depends(),
    current_admin: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db)
):
    """
    전체 환불 목록 조회 (관리자용)
    - 필터링: 상태, 날짜 범위
    - 검색: 사용자명, 이메일
    - 페이지네이션
    """
    service = AdminPaymentService(db)
    result = await service.get_refunds(params)
    return RefundManagementPaginatedResponse(
        total=result["total"],
        page=result["page"],
        page_size=result["page_size"],
        total_pages=result["total_pages"],
        items=result["items"]
    )

@router.get(
    "/refunds/{refund_id}",
    response_model=SuccessResponse[RefundResponse],
    summary="환불 상세 조회",
    description="환불 요청의 상세 정보를 조회합니다.",
    responses={
        200: {"description": "환불 상세 조회 성공"},
        **ADMIN_REFUND_DETAIL_RESPONSES
    }
)
async def get_refund(
    refund_id: int = Path(..., gt=0, description="환불 ID"),
    current_admin: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db)
):
    """
    환불 상세 조회 (관리자용)
    """
    service = AdminPaymentService(db)
    refund = await service.get_refund(refund_id)
    return SuccessResponse(data=refund)

@router.patch(
    "/refunds/{refund_id}",
    response_model=SuccessResponse[RefundResponse],
    summary="환불 상태 변경",
    description="환불 요청을 승인하거나 거절합니다.",
    responses={
        200: {"description": "환불 상태 변경 완료"},
        **REFUND_UPDATE_RESPONSES
    }
)
async def update_refund(
    refund_id: int = Path(..., gt=0, description="환불 ID"),
    data: RefundUpdate = ...,
    current_admin: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db)
):
    """
    환불 상태 변경 (관리자용)
    """
    service = AdminPaymentService(db)
    refund = await service.update_refund(refund_id, data)
    await db.commit()
    return SuccessResponse(data=refund)

@router.get(
    "/refunds/export",
    summary="환불 내역 내보내기",
    description="환불 내역을 엑셀 파일로 내보냅니다.",
    responses={
        200: {"description": "환불 내역 내보내기 완료"},
        **ADMIN_RESPONSES
    }
)
async def export_refunds(
    params: RefundManagementListParams = Depends(),
    current_admin: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db)
):
    """
    환불 내역 내보내기 (엑셀용)
    """
    service = AdminPaymentService(db)
    items = await service.export_refunds(params)
    return {"data": items}
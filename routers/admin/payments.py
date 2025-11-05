"""
관리자 결제 및 환불 관리 API 라우터
결제 내역 조회, 환불 승인/거절 등을 처리합니다.
"""

from fastapi import APIRouter, Depends
from schemas.admin import (
    PaymentManagementListParams, PaymentManagementPaginatedResponse,
    RefundManagementListParams, RefundManagementPaginatedResponse
)
from schemas.payment import RefundUpdate, RefundResponse
from schemas.common import MessageResponse
from exceptions import (
    ADMIN_PAYMENT_MANAGEMENT_RESPONSES,
    REFUND_UPDATE_RESPONSES,
    ADMIN_RESPONSES,
)

router = APIRouter(prefix="/admin/payments", tags=["관리자 - 결제 및 환불 관리"])


@router.get(
    "",
    response_model=PaymentManagementPaginatedResponse,
    summary="결제 목록 조회",
    description="전체 결제 내역을 조회합니다.",
    responses=ADMIN_RESPONSES
)
async def get_payments(params: PaymentManagementListParams = Depends()):
    pass


@router.get(
    "/export",
    summary="결제 내역 내보내기",
    description="결제 내역을 엑셀 파일로 내보냅니다.",
    responses=ADMIN_RESPONSES
)
async def export_payments(params: PaymentManagementListParams = Depends()):
    pass


@router.get(
    "/refunds",
    response_model=RefundManagementPaginatedResponse,
    summary="환불 목록 조회",
    description="환불 요청 목록을 조회합니다.",
    responses=ADMIN_RESPONSES
)
async def get_refunds(params: RefundManagementListParams = Depends()):
    pass


@router.get(
    "/refunds/{refund_id}",
    response_model=RefundResponse,
    summary="환불 상세 조회",
    description="환불 요청의 상세 정보를 조회합니다.",
    responses=ADMIN_PAYMENT_MANAGEMENT_RESPONSES
)
async def get_refund(refund_id: int):
    pass


@router.patch(
    "/refunds/{refund_id}",
    response_model=RefundResponse,
    summary="환불 상태 변경",
    description="환불 요청을 승인하거나 거절합니다.",
    responses=REFUND_UPDATE_RESPONSES
)
async def update_refund(refund_id: int, data: RefundUpdate):
    pass


@router.get(
    "/refunds/export",
    summary="환불 내역 내보내기",
    description="환불 내역을 엑셀 파일로 내보냅니다.",
    responses=ADMIN_RESPONSES
)
async def export_refunds(params: RefundManagementListParams = Depends()):
    pass
import csv
import io
from fastapi import APIRouter, Depends, Path
from fastapi.responses import StreamingResponse
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
    operation_id="admin_get_payments",
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
        200: {
            "description": "결제 내역 내보내기 완료",
            "content": {
                "text/csv": {
                    "schema": {"type": "string"},
                    "example": "id,transaction_id,user_id,user_nickname,user_email,course_id,course_title,amount,discount_amount,final_amount,payment_method,status,paid_at,created_at\n1,TXN001,1,홍길동,hong@example.com,1,Python 기초,50000,0,50000,card,completed,2025-01-15T10:30:00,2025-01-15T10:00:00"
                }
            }
        },
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

    # CSV 파일 생성
    output = io.StringIO()
    if items:
        fieldnames = [
            "id", "transaction_id", "user_id", "user_nickname", "user_email",
            "course_id", "course_title", "amount", "discount_amount", "final_amount",
            "payment_method", "status", "paid_at", "created_at"
        ]
        writer = csv.DictWriter(output, fieldnames=fieldnames)
        writer.writeheader()

        for item in items:
            row = {}
            for field in fieldnames:
                value = getattr(item, field, None)
                # datetime 객체를 문자열로 변환
                if hasattr(value, 'isoformat'):
                    value = value.isoformat()
                row[field] = value
            writer.writerow(row)

    output.seek(0)
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=payments_export.csv"}
    )

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
    operation_id="admin_get_refund",
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
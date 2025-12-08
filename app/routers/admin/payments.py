import csv
import io
from fastapi import APIRouter, Depends, Path
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.admin import *
from app.schemas.payment import RefundUpdate, RefundResponse
from app.schemas.common import SuccessResponse
from app.exceptions.responses import *
from app.core.dependencies import get_current_admin, get_db
from app.models.user import User
from app.services.payment_service import AdminPaymentService

router = APIRouter(prefix="/admin/payments", tags=["관리자 - 결제 및 환불 관리"])

@router.get("", response_model=PaymentManagementPaginatedResponse, summary="결제 목록 조회", operation_id="admin_get_payments", responses={200: {"description": "성공"}, **ADMIN_RESPONSES})
async def get_payments(params: PaymentManagementListParams = Depends(), current_admin: User = Depends(get_current_admin), db: AsyncSession = Depends(get_db)):
    result = await AdminPaymentService(db).get_payments(params)
    return PaymentManagementPaginatedResponse(**result)

@router.get("/export", summary="결제 내역 내보내기", responses={200: {"description": "성공"}, **ADMIN_RESPONSES})
async def export_payments(params: PaymentManagementListParams = Depends(), current_admin: User = Depends(get_current_admin), db: AsyncSession = Depends(get_db)):
    items = await AdminPaymentService(db).export_payments(params)
    output = io.StringIO()
    if items:
        fields = ["id", "transaction_id", "user_id", "user_nickname", "user_email", "course_id", "course_title", "amount", "discount_amount", "final_amount", "payment_method", "status", "paid_at", "created_at"]
        writer = csv.DictWriter(output, fieldnames=fields)
        writer.writeheader()
        for item in items:
            row = {f: item[f] for f in fields}
            for f in fields:
                if hasattr(row[f], 'isoformat'):
                    row[f] = row[f].isoformat()
            writer.writerow(row)
    output.seek(0)
    return StreamingResponse(iter([output.getvalue()]), media_type="text/csv", headers={"Content-Disposition": "attachment; filename=payments_export.csv"})

@router.get("/refunds", response_model=RefundManagementPaginatedResponse, summary="환불 목록 조회", responses={200: {"description": "성공"}, **ADMIN_REFUND_LIST_RESPONSES})
async def get_refunds(params: RefundManagementListParams = Depends(), current_admin: User = Depends(get_current_admin), db: AsyncSession = Depends(get_db)):
    result = await AdminPaymentService(db).get_refunds(params)
    return RefundManagementPaginatedResponse(**result)

@router.get("/refunds/{refund_id}", response_model=SuccessResponse[RefundResponse], summary="환불 상세 조회", operation_id="admin_get_refund", responses={200: {"description": "성공"}, **ADMIN_REFUND_DETAIL_RESPONSES})
async def get_refund(refund_id: int = Path(..., gt=0), current_admin: User = Depends(get_current_admin), db: AsyncSession = Depends(get_db)):
    refund = await AdminPaymentService(db).get_refund(refund_id)
    return SuccessResponse(data=refund)

@router.patch("/refunds/{refund_id}", response_model=SuccessResponse[RefundResponse], summary="환불 상태 변경", responses={200: {"description": "성공"}, **REFUND_UPDATE_RESPONSES})
async def update_refund(refund_id: int = Path(..., gt=0), data: RefundUpdate = ..., current_admin: User = Depends(get_current_admin), db: AsyncSession = Depends(get_db)):
    refund = await AdminPaymentService(db).update_refund(refund_id, data)
    await db.commit()
    return SuccessResponse(data=refund)

@router.get("/refunds/export", summary="환불 내역 내보내기", responses={200: {"description": "성공"}, **ADMIN_RESPONSES})
async def export_refunds(params: RefundManagementListParams = Depends(), current_admin: User = Depends(get_current_admin), db: AsyncSession = Depends(get_db)):
    items = await AdminPaymentService(db).export_refunds(params)
    return {"data": items}
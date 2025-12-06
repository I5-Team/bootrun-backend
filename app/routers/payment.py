from fastapi import APIRouter, Depends, status, Path
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.payment import *
from app.schemas.common import MessageResponse, SuccessResponse
from app.exceptions.responses import *
from app.core.dependencies import get_current_user, get_current_active_user
from app.core.database import get_db
from app.models.user import User
from app.services.payment_service import PaymentService, RefundService

router = APIRouter(prefix="/payments", tags=["결제 및 환불"])


@router.post(
    "",
    response_model=SuccessResponse[PaymentResponse],
    status_code=status.HTTP_201_CREATED,
    summary="결제 생성",
    responses={201: {"description": "결제 생성 성공"}, **PAYMENT_CREATE_RESPONSES}
)
async def create_payment(data: PaymentCreate, current_user: User = Depends(get_current_active_user), db: AsyncSession = Depends(get_db)):
    svc = PaymentService(db)
    payment = await svc.create_payment(current_user.id, data, current_user.id)
    await db.commit()
    return SuccessResponse(data=payment)

@router.get("", response_model=PaymentPaginatedResponse, summary="결제 목록 조회", operation_id="user_get_payments", responses={200: {"description": "성공"}, **AUTH_RESPONSES})
async def get_payments(params: PaymentListParams = Depends(), current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    return await PaymentService(db).get_payments(current_user.id, params)

@router.get("/{payment_id}", response_model=SuccessResponse[PaymentDetailResponse], summary="결제 상세 조회", responses={200: {"description": "성공"}, **AUTH_PERMISSION_RESPONSES})
async def get_payment(payment_id: int = Path(..., gt=0), current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    payment = await PaymentService(db).get_payment(payment_id, current_user.id)
    return SuccessResponse(data=payment)

@router.post("/{payment_id}/confirm", response_model=SuccessResponse[PaymentResponse], summary="결제 승인", responses={200: {"description": "성공"}, **PAYMENT_CONFIRM_RESPONSES})
async def confirm_payment(data: PaymentConfirmRequest, payment_id: int = Path(..., gt=0), current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    svc = PaymentService(db)
    payment = await svc.confirm_payment(payment_id, current_user.id, data)
    await db.commit()
    return SuccessResponse(data=payment)

@router.post("/{payment_id}/cancel", response_model=MessageResponse, summary="결제 취소", responses={200: {"description": "성공"}, **MODIFY_RESPONSES})
async def cancel_payment(payment_id: int = Path(..., gt=0), current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    result = await PaymentService(db).cancel_payment(payment_id, current_user.id)
    await db.commit()
    return MessageResponse(message=result["message"])

@router.post("/refunds", response_model=SuccessResponse[RefundResponse], status_code=status.HTTP_201_CREATED, summary="환불 요청", responses={201: {"description": "성공"}, **REFUND_CREATE_RESPONSES})
async def create_refund(data: RefundCreate, current_user: User = Depends(get_current_active_user), db: AsyncSession = Depends(get_db)):
    refund = await RefundService(db).create_refund(current_user.id, data)
    await db.commit()
    return SuccessResponse(data=refund, status_code=status.HTTP_201_CREATED)

@router.get("/refunds/my", response_model=SuccessResponse[list[RefundResponse]], summary="내 환불 요청 목록", responses={200: {"description": "성공"}, **AUTH_RESPONSES})
async def get_my_refunds(current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    refunds = await RefundService(db).get_my_refunds(current_user.id)
    return SuccessResponse(data=refunds)

@router.get("/refunds/{refund_id}", response_model=SuccessResponse[RefundResponse], summary="환불 상세 조회", operation_id="user_get_refund", responses={200: {"description": "성공"}, **AUTH_PERMISSION_RESPONSES})
async def get_refund(refund_id: int = Path(..., gt=0), current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    refund = await RefundService(db).get_refund(refund_id, current_user.id)
    return SuccessResponse(data=refund)

@router.delete("/refunds/{refund_id}", response_model=MessageResponse, summary="환불 요청 취소", responses={200: {"description": "성공"}, **MODIFY_RESPONSES})
async def cancel_refund(refund_id: int = Path(..., gt=0), current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    result = await RefundService(db).cancel_refund(refund_id, current_user.id)
    await db.commit()
    return MessageResponse(message=result["message"])


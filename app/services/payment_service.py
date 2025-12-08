from typing import List, Optional
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_
import math

from app.models.payment import Payment, Refund, PaymentStatus, PaymentMethod, RefundStatus
from app.models.course import Course
from app.models.progress import Enrollment, Progress
from app.models.user import User
from app.schemas.payment import *
from app.exceptions.base import *
from app.services.toss_payment_client import TossPaymentClient, TossPaymentError


class PaymentService:
    def __init__(self, db: AsyncSession):
        self.db = db

    def _safe_order_id(self, payment: Payment) -> str:
        return payment.order_id or f"LEGACY_{payment.id}"

    async def create_payment(self, user_id: int, data: PaymentCreate, current_user_id: int) -> PaymentResponse:
        course = await self.db.execute(select(Course).where(Course.id == data.course_id))
        course = course.scalar_one_or_none()
        if not course:
            raise CourseNotFoundError()

        existing = await self.db.execute(
            select(Payment).where(
                Payment.user_id == user_id,
                Payment.course_id == data.course_id,
                Payment.status == PaymentStatus.COMPLETED.value
            )
        )
        if existing.scalar_one_or_none():
            raise AlreadyPaidError()

        order_id = f"ORDER_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}_{user_id}_{data.course_id}"

        payment = Payment(
            user_id=user_id,
            course_id=data.course_id,
            amount=course.price,
            discount_amount=0,
            final_amount=course.price,
            payment_method=data.payment_method.value if hasattr(data.payment_method, 'value') else str(data.payment_method),
            status=PaymentStatus.PENDING.value,
            order_id=order_id
        )

        self.db.add(payment)
        await self.db.flush()

        return PaymentResponse(
            id=payment.id,
            user_id=payment.user_id,
            course_id=payment.course_id,
            course_title=course.title,
            amount=payment.amount,
            discount_amount=payment.discount_amount,
            final_amount=payment.final_amount,
            payment_method=payment.payment_method,
            status=payment.status,
            order_id=self._safe_order_id(payment),
            payment_key=payment.payment_key,
            transaction_id=payment.transaction_id,
            receipt_url=payment.receipt_url,
            paid_at=payment.paid_at,
            created_at=payment.created_at
        )

    async def get_payments(self, user_id: int, params: PaymentListParams) -> PaymentPaginatedResponse:
        query = select(Payment).where(Payment.user_id == user_id)

        if params.status:
            query = query.where(Payment.status == params.status)
        if params.payment_method:
            query = query.where(Payment.payment_method == params.payment_method)
        if params.start_date:
            query = query.where(Payment.created_at >= params.start_date)
        if params.end_date:
            query = query.where(Payment.created_at <= params.end_date)
        if params.keyword:
            query = query.join(Course).where(Course.title.ilike(f"%{params.keyword}%"))

        count_query = select(func.count(Payment.id)).where(Payment.user_id == user_id)
        if params.status:
            count_query = count_query.where(Payment.status == params.status)
        if params.payment_method:
            count_query = count_query.where(Payment.payment_method == params.payment_method)
        if params.start_date:
            count_query = count_query.where(Payment.created_at >= params.start_date)
        if params.end_date:
            count_query = count_query.where(Payment.created_at <= params.end_date)

        total = (await self.db.execute(count_query)).scalar()
        offset = (params.page - 1) * params.page_size

        result = await self.db.execute(query.offset(offset).limit(params.page_size).order_by(Payment.created_at.desc()))
        payments = result.scalars().all()

        items = []
        for payment in payments:
            course = await self.db.execute(
                select(Course).where(Course.id == payment.course_id)
            )
            course = course.scalar_one()

            items.append(PaymentResponse(
                id=payment.id,
                user_id=payment.user_id,
                course_id=payment.course_id,
                course_title=course.title,
                amount=payment.amount,
                discount_amount=payment.discount_amount,
                final_amount=payment.final_amount,
                payment_method=payment.payment_method,
                status=payment.status,
                order_id=self._safe_order_id(payment),
                payment_key=payment.payment_key,
                transaction_id=payment.transaction_id,
                receipt_url=payment.receipt_url,
                paid_at=payment.paid_at,
                created_at=payment.created_at,
            ))

        total_pages = math.ceil(total / params.page_size) if total > 0 else 0

        return PaymentPaginatedResponse(
            total=total,
            page=params.page,
            page_size=params.page_size,
            total_pages=total_pages,
            items=items
        )

    async def get_payment(
        self,
        payment_id: int,
        user_id: int
    ) -> PaymentDetailResponse:
        """
        결제 상세 조회
        - 사용자 권한 확인
        - 환불 가능 여부 계산
        """
        payment = await self.db.execute(
            select(Payment).where(
                and_(Payment.id == payment_id, Payment.user_id == user_id)
            )
        )
        payment = payment.scalar_one_or_none()

        if not payment:
            raise PaymentNotFoundError()

        user = (await self.db.execute(select(User).where(User.id == payment.user_id))).scalar_one()
        course = (await self.db.execute(select(Course).where(Course.id == payment.course_id))).scalar_one()
        can_refund, refund_reason = await self._check_refund_eligibility(payment_id, user_id)

        return PaymentDetailResponse(
            id=payment.id,
            user_id=payment.user_id,
            user_nickname=user.nickname or user.email.split("@")[0],
            user_email=user.email,
            course_id=payment.course_id,
            course_title=course.title,
            amount=payment.amount,
            discount_amount=payment.discount_amount,
            final_amount=payment.final_amount,
            payment_method=payment.payment_method,
            status=payment.status,
            order_id=self._safe_order_id(payment),
            payment_key=payment.payment_key,
            transaction_id=payment.transaction_id,
            receipt_url=payment.receipt_url,
            paid_at=payment.paid_at,
            created_at=payment.created_at,
            can_refund=can_refund,
            refund_reason=refund_reason,
        )


    async def confirm_payment(self, payment_id: int, user_id: int, data: PaymentConfirmRequest) -> PaymentResponse:
        payment = await self.db.execute(
            select(Payment)
            .where(and_(Payment.id == payment_id, Payment.user_id == user_id))
            .with_for_update()  # 동시성 제어: 이 행을 잠금
        )
        payment = payment.scalar_one_or_none()

        if not payment:
            raise PaymentNotFoundError()

        if payment.status != PaymentStatus.PENDING.value:
            raise PaymentConfirmFailedError("이미 처리된 결제입니다")

        # orderId 검증
        if payment.order_id != data.order_id:
            raise PaymentConfirmFailedError("주문 ID가 일치하지 않습니다")

        # 결제 금액 검증
        if payment.final_amount != data.amount:
            raise PaymentConfirmFailedError("결제 금액이 일치하지 않습니다")

        # 토스 페이먼츠 승인 API 호출
        toss_client = TossPaymentClient()
        try:
            toss_response = await toss_client.confirm_payment(
                payment_key=data.payment_key,
                order_id=data.order_id,
                amount=data.amount
            )
        except TossPaymentError as e:
            # 토스 API 에러 시 결제 상태를 FAILED로 변경
            payment.status = PaymentStatus.FAILED.value
            await self.db.flush()
            raise PaymentConfirmFailedError(f"결제 승인 실패: {e.message}")
        except Exception as e:
            payment.status = PaymentStatus.FAILED.value
            await self.db.flush()
            raise PaymentConfirmFailedError(f"결제 승인 중 오류 발생: {str(e)}")

        # 승인 성공 - 결제 정보 업데이트
        payment.status = PaymentStatus.COMPLETED.value
        payment.payment_key = data.payment_key
        payment.transaction_id = toss_response.get("transactionKey")
        payment.paid_at = datetime.utcnow()
        payment.receipt_url = toss_response.get("receipt", {}).get("url")

        await self.db.flush()

        # enrollment 생성 (수강 등록)
        # 수강 기간: 결제일로부터 2년
        enrollment = Enrollment(
            user_id=user_id,
            course_id=payment.course_id,
            is_active=True,
            expires_at=datetime.utcnow() + timedelta(days=365*2),
        )
        self.db.add(enrollment)
        await self.db.flush()

        # 강의 정보 조회
        course = await self.db.execute(
            select(Course).where(Course.id == payment.course_id)
        )
        course = course.scalar_one()

        return PaymentResponse(
            id=payment.id,
            user_id=payment.user_id,
            course_id=payment.course_id,
            course_title=course.title,
            amount=payment.amount,
            discount_amount=payment.discount_amount,
            final_amount=payment.final_amount,
            payment_method=payment.payment_method,
            status=payment.status,
            order_id=self._safe_order_id(payment),
            payment_key=payment.payment_key,
            transaction_id=payment.transaction_id,
            receipt_url=payment.receipt_url,
            paid_at=payment.paid_at,
            created_at=payment.created_at,
        )

    async def cancel_payment(self, payment_id: int, user_id: int) -> dict:
        payment = (await self.db.execute(
            select(Payment).where(and_(Payment.id == payment_id, Payment.user_id == user_id))
        )).scalar_one_or_none()

        if not payment:
            raise PaymentNotFoundError()
        if payment.status == PaymentStatus.FAILED.value:
            raise BadRequestError("이미 취소된 결제입니다")
        if payment.status == PaymentStatus.COMPLETED.value:
            raise CancelNotAllowedError("완료된 결제는 취소할 수 없습니다. 환불 요청을 이용해주세요.")

        payment.status = PaymentStatus.FAILED.value
        await self.db.flush()
        return {"message": "결제가 취소되었습니다"}

    async def check_refund_eligibility(self, payment_id: int, user_id: int) -> RefundCheckResponse:
        can_refund, reason = await self._check_refund_eligibility(payment_id, user_id)
        return RefundCheckResponse(can_refund=can_refund, message=reason or "환불 가능합니다")

    async def _check_refund_eligibility(
        self,
        payment_id: int,
        user_id: int
    ) -> tuple[bool, Optional[str]]:
        """
        환불 가능 여부 내부 로직
        Returns: (can_refund, reason)
        """
        payment = await self.db.execute(
            select(Payment).where(
                and_(
                    Payment.id == payment_id,
                    Payment.user_id == user_id,
                    Payment.status == PaymentStatus.COMPLETED.value
                )
            )
        )
        payment = payment.scalar_one_or_none()

        if not payment:
            return False, "결제 정보를 찾을 수 없습니다"

        # 환불 이력 확인
        existing_refund = await self.db.execute(
            select(Refund).where(
                Refund.payment_id == payment_id
            )
        )
        existing_refund = existing_refund.scalar_one_or_none()

        if existing_refund and existing_refund.status in [
            RefundStatus.APPROVED.value,
            RefundStatus.PENDING.value
        ]:
            return False, "이미 환불 요청이 있습니다"

        # 1. 구매일 1주 이내 확인
        if payment.paid_at:
            days_since_purchase = (datetime.utcnow() - payment.paid_at).days
            if days_since_purchase > 7:
                return False, "구매일로부터 1주를 초과했습니다"

        # 2. 진도율 10% 미만 확인
        enrollment = await self.db.execute(
            select(Enrollment).where(
                and_(
                    Enrollment.user_id == user_id,
                    Enrollment.course_id == payment.course_id,
                    Enrollment.is_active == True
                )
            )
        )
        enrollment = enrollment.scalars().first()

        if enrollment:
            # 진행률 계산
            progress_rate = await self._calculate_progress_rate(user_id, payment.course_id)
            if progress_rate >= 10:
                return False, f"진도율이 {progress_rate}%로 10% 이상입니다"

        return True, None

    async def _calculate_progress_rate(
        self,
        user_id: int,
        course_id: int
    ) -> float:
        """
        사용자의 강의별 진도율 계산
        """
        from app.models.course import Lecture, Chapter

        # 총 강의 수
        total_lectures = await self.db.execute(
            select(func.count(Lecture.id)).select_from(Lecture).join(Chapter).where(
                Chapter.course_id == course_id
            )
        )
        total_lectures = total_lectures.scalar() or 1

        # 시청 완료한 강의 수
        completed_lectures = await self.db.execute(
            select(func.count(Progress.id)).where(
                and_(
                    Progress.user_id == user_id,
                    Progress.is_completed == True
                )
            ).join(Lecture).join(Chapter).where(Chapter.course_id == course_id)
        )
        completed_lectures = completed_lectures.scalar() or 0

        progress_rate = (completed_lectures / total_lectures * 100) if total_lectures > 0 else 0
        return min(progress_rate, 100)

    async def _build_refund_response(self, refund: Refund):
        """
        환불 응답 구성 (관리자용 RefundManagementResponse)
        """
        from app.schemas.admin import RefundManagementResponse

        # 결제 정보 조회
        payment = await self.db.execute(
            select(Payment).where(Payment.id == refund.payment_id)
        )
        payment = payment.scalar_one()

        # 사용자 정보 조회
        user = await self.db.execute(
            select(User).where(User.id == refund.user_id)
        )
        user = user.scalar_one()

        # 강의 정보 조회
        course = await self.db.execute(
            select(Course).where(Course.id == payment.course_id)
        )
        course = course.scalar_one()

        # 진도율 계산
        progress_rate = await self._calculate_progress_rate(
            refund.user_id,
            payment.course_id
        )

        return RefundManagementResponse(
            id=refund.id,
            payment_id=refund.payment_id,
            transaction_id=payment.transaction_id or "",
            user_id=refund.user_id,
            user_nickname=user.nickname or user.email.split("@")[0],
            course_title=course.title,
            amount=refund.amount,
            reason=refund.reason,
            status=refund.status,
            payment_date=payment.paid_at or payment.created_at,
            progress_rate=progress_rate,
            requested_at=refund.requested_at,
            processed_at=refund.processed_at,
            admin_note=refund.admin_note,
        )


class RefundService:
    """환불 관련 비즈니스 로직"""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.payment_service = PaymentService(db)


    async def create_refund(
        self,
        user_id: int,
        data: RefundCreate
    ) -> RefundResponse:
        """
        환불 요청 생성
        - 환불 가능 여부 확인
        - 환불 요청 레코드 생성
        """
        # 결제 정보 확인
        payment = await self.db.execute(
            select(Payment).where(
                and_(
                    Payment.id == data.payment_id,
                    Payment.user_id == user_id
                )
            )
        )
        payment = payment.scalar_one_or_none()

        if not payment:
            raise PaymentNotFoundError()

        # 환불 가능 여부 확인
        can_refund, reason = await self.payment_service._check_refund_eligibility(
            data.payment_id, user_id
        )

        if not can_refund:
            raise RefundNotAllowedError(f"환불할 수 없습니다. {reason}")

        # 환불 요청 생성
        refund = Refund(
            payment_id=data.payment_id,
            user_id=user_id,
            amount=payment.final_amount,
            reason=data.reason,
            status=RefundStatus.PENDING.value,
        )

        self.db.add(refund)
        await self.db.flush()

        # 응답 구성
        return await self._build_refund_response(refund)


    async def get_my_refunds(
        self,
        user_id: int
    ) -> List[RefundResponse]:
        """
        사용자의 환불 요청 목록 조회
        """
        result = await self.db.execute(
            select(Refund).where(Refund.user_id == user_id).order_by(
                Refund.requested_at.desc()
            )
        )
        refunds = result.scalars().all()

        responses = []
        for refund in refunds:
            responses.append(await self._build_refund_response(refund))

        return responses

    async def get_refund(
        self,
        refund_id: int,
        user_id: int
    ) -> RefundResponse:
        """
        환불 상세 조회
        - 사용자 권한 확인
        """
        refund = await self.db.execute(
            select(Refund).where(
                and_(
                    Refund.id == refund_id,
                    Refund.user_id == user_id
                )
            )
        )
        refund = refund.scalar_one_or_none()

        if not refund:
            raise RefundNotFoundError()

        return await self._build_refund_response(refund)


    async def cancel_refund(
        self,
        refund_id: int,
        user_id: int
    ) -> dict:
        """
        환불 요청 취소
        - 대기 중인 환불만 취소 가능
        """
        refund = await self.db.execute(
            select(Refund).where(
                and_(
                    Refund.id == refund_id,
                    Refund.user_id == user_id
                )
            )
        )
        refund = refund.scalar_one_or_none()

        if not refund:
            raise RefundNotFoundError()

        if refund.status != RefundStatus.PENDING.value:
            raise BadRequestError("대기 중인 환불만 취소할 수 있습니다")

        await self.db.delete(refund)
        await self.db.flush()

        return {"message": "환불 요청이 취소되었습니다"}


    async def _build_refund_response(self, refund: Refund) -> RefundResponse:
        """
        RefundResponse 구성
        """
        # 결제 정보 조회
        payment = await self.db.execute(
            select(Payment).where(Payment.id == refund.payment_id)
        )
        payment = payment.scalar_one()

        # 사용자 정보 조회
        user = await self.db.execute(
            select(User).where(User.id == refund.user_id)
        )
        user = user.scalar_one()

        # 강의 정보 조회
        course = await self.db.execute(
            select(Course).where(Course.id == payment.course_id)
        )
        course = course.scalar_one()

        # 진도율 계산
        progress_rate = await self.payment_service._calculate_progress_rate(
            refund.user_id,
            payment.course_id
        )

        return RefundResponse(
            id=refund.id,
            payment_id=refund.payment_id,
            user_id=refund.user_id,
            user_nickname=user.nickname or user.email.split("@")[0],
            amount=refund.amount,
            reason=refund.reason,
            status=refund.status,
            admin_note=refund.admin_note,
            requested_at=refund.requested_at,
            processed_at=refund.processed_at,
            payment_date=payment.paid_at or payment.created_at,
            course_title=course.title,
            progress_rate=progress_rate,
        )


class AdminPaymentService:
    """관리자용 결제 관리 비즈니스 로직"""

    def __init__(self, db: AsyncSession):
        self.db = db


    def _convert_refund_status_filter(self, status_str: Optional[str]) -> Optional[RefundStatus]:
        """
        문자열 상태 값을 RefundStatus ENUM으로 변환
        지원 값: pending, approved, rejected
        """
        if not status_str:
            return None

        status_lower = status_str.lower()

        # RefundStatus ENUM 값과 매칭
        for enum_member in RefundStatus:
            if enum_member.value == status_lower:
                return enum_member

        # 매칭되는 값이 없으면 None 반환
        return None

    def _convert_payment_status_filter(self, status_str: Optional[str]) -> Optional[PaymentStatus]:
        """
        문자열 상태 값을 PaymentStatus ENUM으로 변환
        지원 값: pending, completed, failed, refunded
        """
        if not status_str:
            return None

        status_lower = status_str.lower()

        # PaymentStatus ENUM 값과 매칭
        for enum_member in PaymentStatus:
            if enum_member.value == status_lower:
                return enum_member

        # 매칭되는 값이 없으면 None 반환
        return None


    async def get_payments(self, params) -> dict:
        """
        전체 결제 목록 조회 (관리자용)
        - 필터링: 상태, 결제 방식, 날짜 범위
        - 검색: 사용자명, 이메일, 강의명
        - 페이지네이션
        """
        query = select(Payment)

        # 필터링
        if hasattr(params, 'status') and params.status:
            converted_status = self._convert_payment_status_filter(params.status)
            if converted_status:
                query = query.where(Payment.status == converted_status.value)

        if hasattr(params, 'payment_method') and params.payment_method:
            query = query.where(Payment.payment_method == params.payment_method)

        if hasattr(params, 'start_date') and params.start_date:
            query = query.where(Payment.created_at >= params.start_date)

        if hasattr(params, 'end_date') and params.end_date:
            query = query.where(Payment.created_at <= params.end_date)

        # 검색
        if hasattr(params, 'keyword') and params.keyword:
            query = query.join(User).join(Course).where(
                or_(
                    User.nickname.ilike(f"%{params.keyword}%"),
                    User.email.ilike(f"%{params.keyword}%"),
                    Course.title.ilike(f"%{params.keyword}%")
                )
            )

        # 전체 개수 (필터링 조건 포함)
        count_query = query.with_only_columns(func.count(Payment.id))
        count_result = await self.db.execute(count_query)
        total = count_result.scalar() or 0

        # 페이지네이션
        page_size = getattr(params, 'page_size', 20)
        page = getattr(params, 'page', 1)
        offset = (page - 1) * page_size
        query = query.offset(offset).limit(page_size)
        query = query.order_by(Payment.created_at.desc())

        result = await self.db.execute(query)
        payments = result.scalars().all()

        # 응답 구성
        items = []
        for payment in payments:
            user = await self.db.execute(
                select(User).where(User.id == payment.user_id)
            )
            user = user.scalar_one()

            course = await self.db.execute(
                select(Course).where(Course.id == payment.course_id)
            )
            course = course.scalar_one()

            items.append({
                "id": payment.id,
                "transaction_id": payment.transaction_id or "",
                "user_id": payment.user_id,
                "user_nickname": user.nickname or user.email.split("@")[0],
                "user_email": user.email,
                "course_id": payment.course_id,
                "course_title": course.title,
                "amount": payment.amount,
                "discount_amount": payment.discount_amount,
                "final_amount": payment.final_amount,
                "payment_method": payment.payment_method.value if hasattr(payment.payment_method, 'value') else str(payment.payment_method),
                "status": payment.status.value if hasattr(payment.status, 'value') else str(payment.status),
                "paid_at": payment.paid_at,
                "created_at": payment.created_at,
            })

        total_pages = math.ceil(total / page_size) if total > 0 else 0

        return {
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": total_pages,
            "items": items
        }

    async def export_payments(self, params) -> list:
        """
        결제 내역 내보내기 (엑셀용)
        """
        data = await self.get_payments(params)
        return data["items"]


    async def get_refunds(self, params) -> dict:
        """
        전체 환불 목록 조회 (관리자용)
        - 필터링: 상태, 날짜 범위
        - 검색: 사용자명, 이메일
        - 페이지네이션
        """
        query = select(Refund)

        # 필터링
        if hasattr(params, 'status') and params.status:
            converted_status = self._convert_refund_status_filter(params.status)
            if converted_status:
                query = query.where(Refund.status == converted_status.value)

        if hasattr(params, 'start_date') and params.start_date:
            query = query.where(Refund.requested_at >= params.start_date)

        if hasattr(params, 'end_date') and params.end_date:
            query = query.where(Refund.requested_at <= params.end_date)

        # 검색
        if hasattr(params, 'keyword') and params.keyword:
            query = query.join(User).where(
                or_(
                    User.nickname.ilike(f"%{params.keyword}%"),
                    User.email.ilike(f"%{params.keyword}%")
                )
            )

        # 전체 개수
        count_result = await self.db.execute(
            select(func.count(Refund.id)).select_from(Refund)
        )
        total = count_result.scalar() or 0

        # 페이지네이션
        page_size = getattr(params, 'page_size', 20)
        page = getattr(params, 'page', 1)
        offset = (page - 1) * page_size
        query = query.offset(offset).limit(page_size)
        query = query.order_by(Refund.requested_at.desc())

        result = await self.db.execute(query)
        refunds = result.scalars().all()

        # 응답 구성
        items = []
        payment_service = PaymentService(self.db)

        for refund in refunds:
            items.append(await payment_service._build_refund_response(refund))

        total_pages = math.ceil(total / page_size) if total > 0 else 0

        return {
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": total_pages,
            "items": items
        }

    async def get_refund(self, refund_id: int):
        """
        환불 상세 조회 (관리자용)
        """
        refund = await self.db.execute(
            select(Refund).where(Refund.id == refund_id)
        )
        refund = refund.scalar_one_or_none()

        if not refund:
            raise RefundNotFoundError()

        payment_service = PaymentService(self.db)
        return await payment_service._build_refund_response(refund)

    async def update_refund(
        self,
        refund_id: int,
        data
    ):
        """
        환불 상태 변경 (관리자용)
        - 승인 시 토스 페이먼츠 API 호출하여 실제 환불 처리
        """
        refund = await self.db.execute(
            select(Refund).where(Refund.id == refund_id)
        )
        refund = refund.scalar_one_or_none()

        if not refund:
            raise RefundNotFoundError()

        if refund.status != RefundStatus.PENDING.value:
            raise RefundAlreadyProcessedError()

        # 결제 정보 조회
        payment = await self.db.execute(
            select(Payment).where(Payment.id == refund.payment_id)
        )
        payment = payment.scalar_one_or_none()

        if not payment:
            raise PaymentNotFoundError()

        # 환불이 승인되면 토스 API 호출
        if data.status == RefundStatus.APPROVED:
            # payment_key가 없으면 환불 불가 (기존 데이터)
            if not payment.payment_key:
                raise BadRequestError("토스 결제가 아니므로 자동 환불이 불가능합니다. 수동 처리가 필요합니다.")

            toss_client = TossPaymentClient()
            try:
                # 토스 API 호출하여 실제 환불 처리
                await toss_client.cancel_payment(
                    payment_key=payment.payment_key,
                    cancel_reason=refund.reason,
                    cancel_amount=refund.amount
                )
            except TossPaymentError as e:
                # 토스 API 실패 시 환불 상태를 APPROVED로 변경하지 않음
                raise BadRequestError(f"토스 환불 처리 실패: {e.message}")
            except Exception as e:
                raise BadRequestError(f"환불 처리 중 오류 발생: {str(e)}")

            # 토스 API 성공 시에만 DB 업데이트
            payment.status = PaymentStatus.REFUNDED.value

        # 상태 업데이트
        refund.status = data.status.value if hasattr(data.status, 'value') else data.status
        refund.admin_note = data.admin_note
        refund.processed_at = datetime.utcnow()

        await self.db.flush()

        payment_service = PaymentService(self.db)
        return await payment_service._build_refund_response(refund)

    async def export_refunds(self, params) -> list:
        """
        환불 내역 내보내기 (엑셀용)
        """
        data = await self.get_refunds(params)
        return data["items"]

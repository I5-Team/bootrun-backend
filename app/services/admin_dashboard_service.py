"""
관리자 대시보드 서비스
- 통계 데이터 조회 및 분석
"""

from sqlalchemy import func, select, and_, or_
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, date, timedelta, timezone
from typing import List, Optional
from app.models.user import User, UserRole
from app.models.course import Course, CategoryType
from app.models.payment import Payment, PaymentStatus, Refund, RefundStatus
from app.models.progress import Enrollment, Progress
from app.schemas.admin import (
    DashboardStats, DailyStats, RevenueStats,
    CourseStats, CategoryStats, SystemSettings
)


class AdminDashboardService:
    """관리자 대시보드 관련 비즈니스 로직을 처리하는 서비스"""

    def __init__(self, db: AsyncSession):
        self.db = db

    # ============= 대시보드 기본 통계 =============

    async def get_dashboard_stats(self) -> DashboardStats:
        """
        대시보드 기본 통계 조회
        - 전체 사용자 수
        - 전체 강의 수
        - 전체 수강 등록 수
        - 활성 수강 수
        - 전체 매출
        - 대기 중인 환불 건수
        - 오늘 방문자 수 (고유 IP)
        - 오늘 조회수
        - 오늘 매출
        """
        today_start = datetime.now(timezone.utc).replace(
            hour=0, minute=0, second=0, microsecond=0
        )
        today_end = today_start + timedelta(days=1)

        # 전체 사용자 수
        user_count_result = await self.db.execute(
            select(func.count(User.id))
        )
        total_users = user_count_result.scalar() or 0

        # 전체 강의 수
        course_count_result = await self.db.execute(
            select(func.count(Course.id))
        )
        total_courses = course_count_result.scalar() or 0

        # 전체 수강 등록 수
        enrollment_count_result = await self.db.execute(
            select(func.count(Enrollment.id))
        )
        total_enrollments = enrollment_count_result.scalar() or 0

        # 활성 수강 수 (만료되지 않은)
        active_enrollments_result = await self.db.execute(
            select(func.count(Enrollment.id)).where(
                Enrollment.expires_at > datetime.now(timezone.utc),
                Enrollment.is_active == True
            )
        )
        active_enrollments = active_enrollments_result.scalar() or 0

        # 전체 매출 (완료된 결제만)
        revenue_result = await self.db.execute(
            select(func.sum(Payment.final_amount)).where(
                Payment.status == PaymentStatus.COMPLETED
            )
        )
        total_revenue = revenue_result.scalar() or 0

        # 대기 중인 환불 건수
        pending_refunds_result = await self.db.execute(
            select(func.count(Refund.id)).where(
                Refund.status == RefundStatus.PENDING
            )
        )
        pending_refunds = pending_refunds_result.scalar() or 0

        # 오늘 방문자 수 (조회되지 않음 - 추후 로그 테이블 필요)
        # 현재는 0으로 반환
        today_visitors = 0

        # 오늘 조회수 (조회되지 않음 - 추후 로그 테이블 필요)
        # 현재는 0으로 반환
        today_views = 0

        # 오늘 매출
        today_revenue_result = await self.db.execute(
            select(func.sum(Payment.final_amount)).where(
                and_(
                    Payment.status == PaymentStatus.COMPLETED,
                    Payment.paid_at >= today_start,
                    Payment.paid_at < today_end
                )
            )
        )
        today_revenue = today_revenue_result.scalar() or 0

        return DashboardStats(
            total_users=total_users,
            total_courses=total_courses,
            total_enrollments=total_enrollments,
            active_enrollments=active_enrollments,
            total_revenue=total_revenue,
            pending_refunds=pending_refunds,
            today_visitors=today_visitors,
            today_views=today_views,
            today_revenue=today_revenue
        )

    # ============= 일별 통계 =============

    async def get_daily_stats(
        self,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        days: int = 30
    ) -> List[DailyStats]:
        """
        일별 통계 조회
        - 날짜별 방문자 수 (고유 IP 기준)
        - 날짜별 조회수
        - 날짜별 매출
        - 날짜별 수강 등록 수
        - 날짜별 신규 사용자
        """
        # 날짜 범위 설정
        if end_date is None:
            end_date = date.today()
        if start_date is None:
            start_date = end_date - timedelta(days=days)

        # 날짜별 결제 통계 (매출)
        revenue_by_date = await self.db.execute(
            select(
                func.date(Payment.paid_at).label("date"),
                func.sum(Payment.final_amount).label("revenue"),
                func.count(Payment.id).label("payment_count")
            ).where(
                and_(
                    Payment.status == PaymentStatus.COMPLETED,
                    func.date(Payment.paid_at) >= start_date,
                    func.date(Payment.paid_at) <= end_date
                )
            ).group_by(func.date(Payment.paid_at))
            .order_by(func.date(Payment.paid_at))
        )

        revenue_data = {
            row[0]: {"revenue": row[1] or 0, "payment_count": row[2] or 0}
            for row in revenue_by_date.fetchall()
        }

        # 날짜별 수강 등록 통계
        enrollments_by_date = await self.db.execute(
            select(
                func.date(Enrollment.enrolled_at).label("date"),
                func.count(Enrollment.id).label("enrollment_count")
            ).where(
                and_(
                    func.date(Enrollment.enrolled_at) >= start_date,
                    func.date(Enrollment.enrolled_at) <= end_date
                )
            ).group_by(func.date(Enrollment.enrolled_at))
            .order_by(func.date(Enrollment.enrolled_at))
        )

        enrollment_data = {
            row[0]: row[1] or 0
            for row in enrollments_by_date.fetchall()
        }

        # 날짜별 신규 사용자
        new_users_by_date = await self.db.execute(
            select(
                func.date(User.created_at).label("date"),
                func.count(User.id).label("new_users")
            ).where(
                and_(
                    func.date(User.created_at) >= start_date,
                    func.date(User.created_at) <= end_date
                )
            ).group_by(func.date(User.created_at))
            .order_by(func.date(User.created_at))
        )

        new_users_data = {
            row[0]: row[1] or 0
            for row in new_users_by_date.fetchall()
        }

        # 결과 생성
        current_date = start_date
        result = []

        while current_date <= end_date:
            daily_data = revenue_data.get(current_date, {"revenue": 0, "payment_count": 0})

            result.append(DailyStats(
                date=current_date,
                visitors=0,  # 로그 테이블 필요
                views=0,     # 로그 테이블 필요
                revenue=daily_data.get("revenue", 0),
                enrollments=enrollment_data.get(current_date, 0),
                new_users=new_users_data.get(current_date, 0)
            ))

            current_date += timedelta(days=1)

        return result

    # ============= 매출 통계 =============

    async def get_revenue_stats(
        self,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        days: int = 30
    ) -> List[RevenueStats]:
        """
        매출 통계 조회
        - 날짜별 매출
        - 날짜별 결제 건수
        - 날짜별 환불 금액 및 건수
        - 날짜별 순수익
        """
        # 날짜 범위 설정
        if end_date is None:
            end_date = date.today()
        if start_date is None:
            start_date = end_date - timedelta(days=days)

        # 날짜별 매출 및 결제 건수
        revenue_by_date = await self.db.execute(
            select(
                func.date(Payment.paid_at).label("date"),
                func.sum(Payment.final_amount).label("revenue"),
                func.count(Payment.id).label("payment_count")
            ).where(
                and_(
                    Payment.status == PaymentStatus.COMPLETED,
                    func.date(Payment.paid_at) >= start_date,
                    func.date(Payment.paid_at) <= end_date
                )
            ).group_by(func.date(Payment.paid_at))
        )

        revenue_data = {}
        for row in revenue_by_date.fetchall():
            revenue_data[row[0]] = {
                "revenue": row[1] or 0,
                "payment_count": row[2] or 0
            }

        # 날짜별 환불 금액 및 건수
        refund_by_date = await self.db.execute(
            select(
                func.date(Refund.processed_at).label("date"),
                func.sum(Refund.amount).label("refund_amount"),
                func.count(Refund.id).label("refund_count")
            ).where(
                and_(
                    Refund.status == RefundStatus.APPROVED,
                    Refund.processed_at.isnot(None),
                    func.date(Refund.processed_at) >= start_date,
                    func.date(Refund.processed_at) <= end_date
                )
            ).group_by(func.date(Refund.processed_at))
        )

        refund_data = {}
        for row in refund_by_date.fetchall():
            refund_data[row[0]] = {
                "refund_amount": row[1] or 0,
                "refund_count": row[2] or 0
            }

        # 결과 생성
        current_date = start_date
        result = []

        while current_date <= end_date:
            revenue_info = revenue_data.get(current_date, {"revenue": 0, "payment_count": 0})
            refund_info = refund_data.get(current_date, {"refund_amount": 0, "refund_count": 0})

            revenue = revenue_info.get("revenue", 0)
            refund_amount = refund_info.get("refund_amount", 0)
            net_revenue = revenue - refund_amount

            result.append(RevenueStats(
                date=current_date,
                revenue=revenue,
                payment_count=revenue_info.get("payment_count", 0),
                refund_amount=refund_amount,
                refund_count=refund_info.get("refund_count", 0),
                net_revenue=net_revenue
            ))

            current_date += timedelta(days=1)

        return result

    # ============= 강의별 통계 =============

    async def get_course_stats(
        self,
        category_type: Optional[CategoryType] = None,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
    ) -> List[CourseStats]:
        """
        강의별 통계 조회
        - 강의별 수강 등록 수
        - 강의별 활성 수강 수
        - 강의별 평균 진행률
        - 강의별 완료 건수
        - 강의별 완료율
        - 강의별 매출
        """
        # 기본 쿼리: 강의 목록
        courses_query = select(Course).where(Course.is_published == True)

        if category_type:
            courses_query = courses_query.where(Course.category_type == category_type)

        courses_result = await self.db.execute(courses_query)
        courses = courses_result.scalars().all()

        result = []

        for course in courses:
            # 수강 등록 수
            enrollment_count_result = await self.db.execute(
                select(func.count(Enrollment.id)).where(
                    Enrollment.course_id == course.id
                )
            )
            total_enrollments = enrollment_count_result.scalar() or 0

            # 활성 수강 수
            active_enrollments_result = await self.db.execute(
                select(func.count(Enrollment.id)).where(
                    and_(
                        Enrollment.course_id == course.id,
                        Enrollment.is_active == True,
                        Enrollment.expires_at > datetime.now(timezone.utc)
                    )
                )
            )
            active_enrollments = active_enrollments_result.scalar() or 0

            # 평균 진행률
            avg_progress_result = await self.db.execute(
                select(func.avg(Enrollment.progress_rate)).where(
                    Enrollment.course_id == course.id
                )
            )
            avg_progress = float(avg_progress_result.scalar() or 0)

            # 완료 건수 (100% 진행률)
            completion_count_result = await self.db.execute(
                select(func.count(Enrollment.id)).where(
                    and_(
                        Enrollment.course_id == course.id,
                        Enrollment.progress_rate >= 100
                    )
                )
            )
            completion_count = completion_count_result.scalar() or 0

            # 완료율
            completion_rate = (completion_count / total_enrollments * 100) if total_enrollments > 0 else 0

            # 매출
            revenue_result = await self.db.execute(
                select(func.sum(Payment.final_amount)).where(
                    and_(
                        Payment.course_id == course.id,
                        Payment.status == PaymentStatus.COMPLETED
                    )
                )
            )
            total_revenue = revenue_result.scalar() or 0

            result.append(CourseStats(
                course_id=course.id,
                course_title=course.title,
                category_name=course.category_type.value,
                total_enrollments=total_enrollments,
                active_enrollments=active_enrollments,
                avg_progress=round(avg_progress, 2),
                completion_count=completion_count,
                completion_rate=round(completion_rate, 2),
                total_revenue=total_revenue
            ))

        return result

    # ============= 카테고리별 통계 =============

    async def get_category_stats(self) -> List[CategoryStats]:
        """
        카테고리별 통계 조회
        - 카테고리별 강의 수
        - 카테고리별 수강 등록 수
        - 카테고리별 매출
        - 카테고리별 평균 완료율
        """
        result = []

        for category in CategoryType:
            # 카테고리별 강의 수
            course_count_result = await self.db.execute(
                select(func.count(Course.id)).where(
                    and_(
                        Course.category_type == category,
                        Course.is_published == True
                    )
                )
            )
            course_count = course_count_result.scalar() or 0

            # 카테고리별 수강 등록 수
            enrollment_count_result = await self.db.execute(
                select(func.count(Enrollment.id)).where(
                    Enrollment.course_id.in_(
                        select(Course.id).where(
                            Course.category_type == category
                        )
                    )
                )
            )
            total_enrollments = enrollment_count_result.scalar() or 0

            # 카테고리별 매출
            revenue_result = await self.db.execute(
                select(func.sum(Payment.final_amount)).where(
                    and_(
                        Payment.course_id.in_(
                            select(Course.id).where(
                                Course.category_type == category
                            )
                        ),
                        Payment.status == PaymentStatus.COMPLETED
                    )
                )
            )
            total_revenue = revenue_result.scalar() or 0

            # 카테고리별 평균 완료율
            completion_result = await self.db.execute(
                select(func.avg(Enrollment.progress_rate)).where(
                    Enrollment.course_id.in_(
                        select(Course.id).where(
                            Course.category_type == category
                        )
                    )
                )
            )
            avg_completion_rate = float(completion_result.scalar() or 0)

            result.append(CategoryStats(
                category_id=category.value,
                category_name=category.value,
                course_count=course_count,
                total_enrollments=total_enrollments,
                total_revenue=total_revenue,
                avg_completion_rate=round(avg_completion_rate, 2)
            ))

        return result

    # ============= 시스템 설정 =============

    async def get_system_settings(self) -> SystemSettings:
        """
        시스템 설정 조회
        현재는 기본값 반환 (추후 DB에서 조회 가능하도록 확장)
        """
        return SystemSettings()

    async def update_system_settings(self, data: SystemSettings) -> SystemSettings:
        """
        시스템 설정 수정
        현재는 입력된 데이터 반환 (추후 DB에 저장 가능하도록 확장)
        """
        return data
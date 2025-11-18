from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_, desc
from datetime import datetime

from app.models.user import User
from app.models.progress import Enrollment, Progress
from app.models.payment import Payment
from app.models.course import Course
from app.schemas.admin import (
    UserManagementListParams, UserManagementResponse,
    UserDetailForAdmin, UserLearningReport,
    UserProgressDetail, UserAttendanceRecord,
    UserManagementPaginatedResponse
)
from app.exceptions.base import NotFoundError
from app.utils.helpers import calculate_total_pages, calculate_offset


class AdminUserService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_users_list(
        self,
        params: UserManagementListParams
    ) -> UserManagementPaginatedResponse:
        """사용자 목록 조회 (페이지네이션 포함)"""
        conditions = []

        if params.role:
            conditions.append(User.role == params.role)

        if params.is_active is not None:
            conditions.append(User.is_active == params.is_active)

        if params.keyword:
            keyword_pattern = f"%{params.keyword}%"
            conditions.append(
                or_(
                    User.nickname.ilike(keyword_pattern),
                    User.email.ilike(keyword_pattern)
                )
            )

        if params.start_date:
            conditions.append(User.created_at >= params.start_date)

        if params.end_date:
            conditions.append(User.created_at <= params.end_date)

        # 기본 쿼리 구성
        base_query = select(User)
        if conditions:
            base_query = base_query.where(and_(*conditions))

        # 전체 개수 조회
        count_query = select(func.count(User.id))
        if conditions:
            count_query = count_query.where(and_(*conditions))

        count_result = await self.db.execute(count_query)
        total = count_result.scalar() or 0

        # 페이징 처리
        offset = calculate_offset(params.page, params.page_size)
        query = (
            base_query
            .order_by(desc(User.created_at))
            .limit(params.page_size)
            .offset(offset)
        )

        result = await self.db.execute(query)
        users = result.scalars().all()

        # 각 사용자의 통계 정보 조회
        items = []
        for user in users:
            total_enrollments = await self._count_enrollments(user.id)
            total_payments = await self._count_payments(user.id)
            total_spent = await self._calculate_total_spent(user.id)

            item = UserManagementResponse(
                id=user.id,
                email=user.email,
                nickname=user.nickname,
                role=user.role,
                is_active=user.is_active,
                total_enrollments=total_enrollments,
                total_payments=total_payments,
                total_spent=total_spent,
                created_at=user.created_at,
                last_login=user.last_login
            )
            items.append(item)

        total_pages = calculate_total_pages(total, params.page_size)

        return UserManagementPaginatedResponse(
            total=total,
            page=params.page,
            page_size=params.page_size,
            total_pages=total_pages,
            items=items
        )

    async def get_user_detail(self, user_id: int) -> UserDetailForAdmin:
        user = await self._get_user(user_id)

        total_study_time = await self._calculate_total_study_time(user_id)
        total_enrollments = await self._count_enrollments(user_id)
        active_enrollments = await self._count_active_enrollments(user_id)
        completed_courses = await self._count_completed_courses(user_id)
        avg_progress_rate = await self._calculate_avg_progress_rate(user_id)

        total_payments = await self._count_payments(user_id)
        total_spent = await self._calculate_total_spent(user_id)
        total_refunds = await self._calculate_total_refunds(user_id)

        enrollments = await self._get_enrollment_details(user_id)

        return UserDetailForAdmin(
            id=user.id,
            email=user.email,
            nickname=user.nickname,
            gender=user.gender or "미지정",
            birth_date=user.birth_date,
            role=user.role,
            is_active=user.is_active,
            provider=user.social_provider,
            created_at=user.created_at,
            last_login=user.last_login,
            total_study_time=total_study_time,
            total_enrollments=total_enrollments,
            active_enrollments=active_enrollments,
            completed_courses=completed_courses,
            avg_progress_rate=avg_progress_rate,
            total_payments=total_payments,
            total_spent=total_spent,
            total_refunds=total_refunds,
            enrollments=enrollments
        )

    async def activate_user(self, user_id: int) -> None:
        user = await self._get_user(user_id)
        if user.is_active:
            raise ValueError("이미 활성화된 사용자입니다")
        user.is_active = True
        user.updated_at = datetime.utcnow()
        await self.db.commit()

    async def deactivate_user(self, user_id: int) -> None:
        user = await self._get_user(user_id)
        if not user.is_active:
            raise ValueError("이미 비활성화된 사용자입니다")
        user.is_active = False
        user.updated_at = datetime.utcnow()
        await self.db.commit()

    async def delete_user(self, user_id: int) -> None:
        user = await self._get_user(user_id)
        await self.db.delete(user)
        await self.db.commit()

    async def get_user_learning_report(
        self,
        user_id: int,
        report_period: str
    ) -> UserLearningReport:
        user = await self._get_user(user_id)

        try:
            period_parts = report_period.split("-")
            year, month = int(period_parts[0]), int(period_parts[1])
        except (IndexError, ValueError):
            raise ValueError("리포트 기간 형식이 올바르지 않습니다 (예: 2025-01)")

        month_end_year = year + 1 if month == 12 else year
        month_end = 1 if month == 12 else month + 1
        period_start = datetime(year, month, 1)
        period_end = datetime(month_end_year, month_end, 1)

        total_study_time = await self._calculate_total_study_time(user_id, period_start, period_end)

        enrollments_result = await self.db.execute(select(Enrollment).where(
            and_(Enrollment.user_id == user_id, Enrollment.is_active == True)
        ))
        enrollments_list = enrollments_result.scalars().all()

        courses_detail = []
        for enrollment in enrollments_list:
            course = (await self.db.execute(select(Course).where(Course.id == enrollment.course_id))).scalar_one()
            progress_detail = UserProgressDetail(
                course_id=course.id,
                course_title=course.title,
                enrolled_at=enrollment.enrolled_at,
                expires_at=enrollment.expires_at,
                progress_rate=enrollment.progress_rate,
                total_lectures=await self._count_course_lectures(course.id),
                completed_lectures=await self._count_completed_lectures(user_id, course.id),
                total_study_time=await self._calculate_course_study_time(user_id, course.id, period_start, period_end),
                last_watched_at=await self._get_last_watched_time(user_id, course.id)
            )
            courses_detail.append(progress_detail)

        from datetime import timedelta
        attendance_records = []
        current_date = period_start
        while current_date < period_end:
            daily_study = await self._get_daily_study_time(user_id, current_date)
            attendance_records.append(UserAttendanceRecord(
                date=current_date.date(),
                is_present=daily_study > 0,
                study_time=daily_study,
                lectures_watched=await self._count_daily_lectures_watched(user_id, current_date)
            ))
            current_date += timedelta(days=1)

        avg_progress = sum(c.progress_rate for c in courses_detail) / len(courses_detail) if courses_detail else 0
        attendance_rate = sum(1 for a in attendance_records if a.is_present) / len(attendance_records) * 100 if attendance_records else 0

        return UserLearningReport(
            user_id=user.id,
            user_nickname=user.nickname,
            report_period=report_period,
            total_study_time=total_study_time,
            attendance_rate=attendance_rate,
            avg_progress_rate=avg_progress,
            courses=courses_detail,
            attendance=attendance_records
        )

    async def _get_user(self, user_id: int) -> User:
        user = (await self.db.execute(select(User).where(User.id == user_id))).scalar_one_or_none()
        if not user:
            raise NotFoundError("사용자를 찾을 수 없습니다")
        return user

    async def _count_enrollments(self, user_id: int) -> int:
        return (await self.db.execute(select(func.count(Enrollment.id)).where(Enrollment.user_id == user_id))).scalar() or 0

    async def _count_active_enrollments(self, user_id: int) -> int:
        return (await self.db.execute(select(func.count(Enrollment.id)).where(
            and_(Enrollment.user_id == user_id, Enrollment.is_active == True)
        ))).scalar() or 0

    async def _count_completed_courses(self, user_id: int) -> int:
        return (await self.db.execute(select(func.count(Enrollment.id)).where(
            and_(Enrollment.user_id == user_id, Enrollment.progress_rate >= 100)
        ))).scalar() or 0

    async def _count_payments(self, user_id: int) -> int:
        return (await self.db.execute(select(func.count(Payment.id)).where(Payment.user_id == user_id))).scalar() or 0

    async def _calculate_total_spent(self, user_id: int) -> int:
        return (await self.db.execute(select(func.sum(Payment.final_amount)).where(Payment.user_id == user_id))).scalar() or 0

    async def _calculate_total_refunds(self, user_id: int) -> int:
        from app.models.payment import Refund
        return (await self.db.execute(select(func.sum(Refund.amount)).where(Refund.user_id == user_id))).scalar() or 0

    async def _calculate_total_study_time(
        self,
        user_id: int,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> int:
        query = select(func.sum(Progress.watched_seconds)).where(Progress.user_id == user_id)
        if start_date:
            query = query.where(Progress.last_watched_at >= start_date)
        if end_date:
            query = query.where(Progress.last_watched_at < end_date)
        total_seconds = (await self.db.execute(query)).scalar() or 0
        return int(total_seconds / 60)

    async def _calculate_avg_progress_rate(self, user_id: int) -> float:
        avg = (await self.db.execute(select(func.avg(Enrollment.progress_rate)).where(
            and_(Enrollment.user_id == user_id, Enrollment.is_active == True)
        ))).scalar()
        return float(avg) if avg else 0.0

    async def _get_enrollment_details(self, user_id: int) -> List[dict]:
        enrollments = (await self.db.execute(select(Enrollment, Course).join(Course).where(
            Enrollment.user_id == user_id
        ))).all()
        return [{"course_id": c.id, "course_title": c.title, "enrolled_at": e.enrolled_at,
                "expires_at": e.expires_at, "progress_rate": e.progress_rate, "is_active": e.is_active}
                for e, c in enrollments]

    async def _count_course_lectures(self, course_id: int) -> int:
        from app.models.course import Chapter, Lecture
        return (await self.db.execute(select(func.count(Lecture.id)).join(
            Chapter, Chapter.id == Lecture.chapter_id
        ).where(Chapter.course_id == course_id))).scalar() or 0

    async def _count_completed_lectures(self, user_id: int, course_id: int) -> int:
        from app.models.course import Chapter, Lecture
        return (await self.db.execute(select(func.count(Progress.id)).join(
            Lecture, Lecture.id == Progress.lecture_id
        ).join(Chapter, Chapter.id == Lecture.chapter_id).where(
            and_(Progress.user_id == user_id, Chapter.course_id == course_id, Progress.is_completed == True)
        ))).scalar() or 0

    async def _calculate_course_study_time(
        self,
        user_id: int,
        course_id: int,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> int:
        from app.models.course import Chapter, Lecture
        query = select(func.sum(Progress.watched_seconds)).join(
            Lecture, Lecture.id == Progress.lecture_id
        ).join(Chapter, Chapter.id == Lecture.chapter_id).where(
            and_(Progress.user_id == user_id, Chapter.course_id == course_id)
        )
        if start_date:
            query = query.where(Progress.last_watched_at >= start_date)
        if end_date:
            query = query.where(Progress.last_watched_at < end_date)
        total_seconds = (await self.db.execute(query)).scalar() or 0
        return int(total_seconds / 60)

    async def _get_last_watched_time(self, user_id: int, course_id: int) -> Optional[datetime]:
        from app.models.course import Chapter, Lecture
        return (await self.db.execute(select(func.max(Progress.last_watched_at)).join(
            Lecture, Lecture.id == Progress.lecture_id
        ).join(Chapter, Chapter.id == Lecture.chapter_id).where(
            and_(Progress.user_id == user_id, Chapter.course_id == course_id)
        ))).scalar()

    async def _get_daily_study_time(self, user_id: int, date: datetime) -> int:
        from datetime import timedelta
        next_date = date + timedelta(days=1)
        total_seconds = (await self.db.execute(select(func.sum(Progress.watched_seconds)).where(
            and_(Progress.user_id == user_id, Progress.last_watched_at >= date, Progress.last_watched_at < next_date)
        ))).scalar() or 0
        return int(total_seconds / 60)

    async def _count_daily_lectures_watched(self, user_id: int, date: datetime) -> int:
        from datetime import timedelta
        next_date = date + timedelta(days=1)
        return (await self.db.execute(select(func.count(Progress.id)).where(
            and_(Progress.user_id == user_id, Progress.last_watched_at >= date, Progress.last_watched_at < next_date)
        ))).scalar() or 0
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_
from sqlalchemy.orm import selectinload, joinedload
from datetime import datetime, timedelta
import math

from app.models.progress import Enrollment, Progress
from app.models.course import Course, Chapter, Lecture
from app.models.user import User
from app.schemas.enrollment import (
    EnrollmentCreate,
    EnrollmentResponse,
    EnrollmentDetailResponse,
    EnrollmentPaginatedResponse,
    MyEnrollmentListParams,
    ProgressCreate,
    ProgressUpdate,
    ProgressResponse,
    CourseProgressDetail,
    ChapterProgressSummary,
    LectureProgressSummary,
    StudentDashboard,
)
from app.exceptions.base import (
    CourseNotFoundError,
    EnrollmentAlreadyExistsError,
    EnrollmentNotFoundError,
    LectureNotFoundError,
    ProgressNotFoundError,
)
from app.utils.helpers import get_current_utc_datetime, get_days_until


class EnrollmentService:

    def __init__(self, db: AsyncSession):
        self.db = db

    # ==================== 수강 등록 ====================

    async def create_enrollment(
        self,
        user_id: int,
        data: EnrollmentCreate
    ) -> EnrollmentResponse:
        """수강 등록 생성 (결제 완료 후 호출)"""

        # 강의 존재 확인
        course_result = await self.db.execute(
            select(Course).where(Course.id == data.course_id)
        )
        course = course_result.scalar_one_or_none()

        if not course:
            raise CourseNotFoundError(f'ID {data.course_id}인 강의를 찾을 수 없습니다')

        # 이미 등록되어 있는지 확인
        existing_result = await self.db.execute(
            select(Enrollment).where(
                Enrollment.user_id == user_id,
                Enrollment.course_id == data.course_id
            )
        )
        existing = existing_result.scalar_one_or_none()

        if existing:
            raise EnrollmentAlreadyExistsError('이미 수강 등록된 강의입니다')

        # 수강 등록 생성 (만료일: 등록일 + 2년)
        now = get_current_utc_datetime()
        expires_at = now + timedelta(days=730)  # 2년

        enrollment = Enrollment(
            user_id=user_id,
            course_id=data.course_id,
            enrolled_at=now,
            expires_at=expires_at,
            is_active=True,
            progress_rate=0.0
        )

        self.db.add(enrollment)
        await self.db.commit()
        await self.db.refresh(enrollment)

        # 응답 데이터 생성
        return await self._build_enrollment_response(enrollment, course)

    async def get_my_enrollments(
        self,
        user_id: int,
        params: MyEnrollmentListParams
    ) -> EnrollmentPaginatedResponse:
        """내 수강 목록 조회"""

        # 기본 쿼리
        query = (
            select(Enrollment)
            .options(joinedload(Enrollment.course))
            .where(Enrollment.user_id == user_id)
        )

        # 필터링
        if params.category_id is not None:
            query = query.where(Course.category_type == params.category_id)

        if params.difficulty is not None:
            query = query.where(Course.difficulty == params.difficulty)

        if params.is_active is not None:
            query = query.where(Enrollment.is_active == params.is_active)

        # 정렬: 최근 등록순
        query = query.order_by(Enrollment.enrolled_at.desc())

        # 전체 개수
        count_query = select(func.count()).select_from(query.subquery())
        total_result = await self.db.execute(count_query)
        total = total_result.scalar()

        # 페이지네이션
        offset = (params.page - 1) * params.page_size
        query = query.offset(offset).limit(params.page_size)

        result = await self.db.execute(query)
        enrollments = result.scalars().all()

        # 응답 데이터 생성
        items = []
        for enrollment in enrollments:
            course = enrollment.course

            # 총 강의 수와 완료된 강의 수 계산
            total_lectures, completed_lectures = await self._get_lecture_counts(
                user_id, course.id
            )

            items.append(EnrollmentResponse(
                id=enrollment.id,
                user_id=enrollment.user_id,
                course_id=enrollment.course_id,
                course_title=course.title,
                course_thumbnail=course.thumbnail_url,
                category_name=course.category_type.value,
                difficulty=course.difficulty.value,
                enrolled_at=enrollment.enrolled_at,
                expires_at=enrollment.expires_at,
                is_active=enrollment.is_active,
                progress_rate=enrollment.progress_rate,
                days_until_expiry=get_days_until(enrollment.expires_at),
                total_lectures=total_lectures,
                completed_lectures=completed_lectures
            ))

        total_pages = math.ceil(total / params.page_size) if total > 0 else 0

        return EnrollmentPaginatedResponse(
            total=total,
            page=params.page,
            page_size=params.page_size,
            total_pages=total_pages,
            items=items
        )

    async def get_enrollment_detail(
        self,
        user_id: int,
        enrollment_id: int
    ) -> EnrollmentDetailResponse:
        """수강 상세 조회"""

        result = await self.db.execute(
            select(Enrollment)
            .options(joinedload(Enrollment.course))
            .where(
                Enrollment.id == enrollment_id,
                Enrollment.user_id == user_id
            )
        )
        enrollment = result.scalar_one_or_none()

        if not enrollment:
            raise EnrollmentNotFoundError('수강 등록 정보를 찾을 수 없습니다')

        course = enrollment.course

        # 통계 계산
        total_lectures, completed_lectures = await self._get_lecture_counts(
            user_id, course.id
        )
        watched_duration = await self._get_total_watched_duration(
            user_id, course.id
        )

        # TODO: 미션 정보는 나중에 추가
        total_missions = 0
        completed_missions = 0

        return EnrollmentDetailResponse(
            id=enrollment.id,
            user_id=enrollment.user_id,
            course_id=enrollment.course_id,
            course_title=course.title,
            course_description=course.description,
            course_thumbnail=course.thumbnail_url,
            instructor_name=course.instructor_name,
            category_name=course.category_type.value,
            difficulty=course.difficulty.value,
            enrolled_at=enrollment.enrolled_at,
            expires_at=enrollment.expires_at,
            is_active=enrollment.is_active,
            progress_rate=enrollment.progress_rate,
            days_until_expiry=get_days_until(enrollment.expires_at),
            total_duration=course.total_duration,
            watched_duration=watched_duration,
            total_lectures=total_lectures,
            completed_lectures=completed_lectures,
            total_missions=total_missions,
            completed_missions=completed_missions
        )

    # ==================== 학습 진행 ====================

    async def create_progress(
        self,
        user_id: int,
        data: ProgressCreate
    ) -> ProgressResponse:
        """학습 진행 생성"""

        # 강의 영상 존재 확인
        lecture_result = await self.db.execute(
            select(Lecture).where(Lecture.id == data.lecture_id)
        )
        lecture = lecture_result.scalar_one_or_none()

        if not lecture:
            raise LectureNotFoundError(f'ID {data.lecture_id}인 강의 영상을 찾을 수 없습니다')

        # 이미 진행 기록이 있는지 확인
        existing_result = await self.db.execute(
            select(Progress).where(
                Progress.user_id == user_id,
                Progress.lecture_id == data.lecture_id
            )
        )
        existing = existing_result.scalar_one_or_none()

        if existing:
            # 이미 존재하면 업데이트
            return await self.update_progress(user_id, data.lecture_id, ProgressUpdate(
                watched_seconds=data.watched_seconds,
                last_position=data.last_position,
                is_completed=data.is_completed
            ))

        # 새로운 진행 기록 생성
        now = get_current_utc_datetime()
        progress = Progress(
            user_id=user_id,
            lecture_id=data.lecture_id,
            watched_seconds=data.watched_seconds,
            last_position=data.last_position,
            is_completed=data.is_completed,
            last_watched_at=now,
            completed_at=now if data.is_completed else None
        )

        self.db.add(progress)
        await self.db.commit()
        await self.db.refresh(progress)

        # 강의 진행률 업데이트
        await self._update_course_progress(user_id, lecture.chapter.course_id)

        return await self._build_progress_response(progress, lecture)

    async def update_progress(
        self,
        user_id: int,
        lecture_id: int,
        data: ProgressUpdate
    ) -> ProgressResponse:
        """학습 진행 업데이트"""

        # 진행 기록 조회
        result = await self.db.execute(
            select(Progress)
            .options(joinedload(Progress.lecture))
            .where(
                Progress.user_id == user_id,
                Progress.lecture_id == lecture_id
            )
        )
        progress = result.scalar_one_or_none()

        if not progress:
            raise ProgressNotFoundError('학습 진행 기록을 찾을 수 없습니다')

        # 업데이트
        progress.watched_seconds = data.watched_seconds
        progress.last_position = data.last_position
        progress.is_completed = data.is_completed
        progress.last_watched_at = get_current_utc_datetime()

        if data.is_completed and progress.completed_at is None:
            progress.completed_at = get_current_utc_datetime()

        await self.db.commit()
        await self.db.refresh(progress)

        # 강의 진행률 업데이트
        await self._update_course_progress(user_id, progress.lecture.chapter.course_id)

        return await self._build_progress_response(progress, progress.lecture)

    async def get_course_progress(
        self,
        user_id: int,
        course_id: int
    ) -> CourseProgressDetail:
        """강의별 학습 진행 조회"""

        # 강의 조회
        course_result = await self.db.execute(
            select(Course)
            .options(
                selectinload(Course.chapters)
                .selectinload(Chapter.lectures)
            )
            .where(Course.id == course_id)
        )
        course = course_result.scalar_one_or_none()

        if not course:
            raise CourseNotFoundError(f'ID {course_id}인 강의를 찾을 수 없습니다')

        # 모든 lecture_id 수집
        all_lecture_ids = []
        for chapter in course.chapters:
            for lecture in chapter.lectures:
                all_lecture_ids.append(lecture.id)

        # 진행 기록 조회
        progress_dict = {}
        if all_lecture_ids:
            progress_result = await self.db.execute(
                select(Progress).where(
                    Progress.user_id == user_id,
                    Progress.lecture_id.in_(all_lecture_ids)
                )
            )
            progresses = progress_result.scalars().all()
            progress_dict = {p.lecture_id: p for p in progresses}

        # 챕터별 진행 상황 생성
        chapters_data = []
        total_watched_duration = 0
        total_completed = 0
        last_watched_at = None

        for chapter in sorted(course.chapters, key=lambda c: c.order_number):
            lectures_data = []
            chapter_watched = 0
            chapter_completed = 0
            chapter_duration = 0

            for lecture in sorted(chapter.lectures, key=lambda l: l.order_number):
                progress = progress_dict.get(lecture.id)

                watched_seconds = progress.watched_seconds if progress else 0
                last_position = progress.last_position if progress else 0
                is_completed = progress.is_completed if progress else False
                lecture_last_watched = progress.last_watched_at if progress else None

                completion_rate = (watched_seconds / lecture.duration_seconds * 100) if lecture.duration_seconds > 0 else 0

                lectures_data.append(LectureProgressSummary(
                    lecture_id=lecture.id,
                    lecture_title=lecture.title,
                    duration_seconds=lecture.duration_seconds,
                    watched_seconds=watched_seconds,
                    last_position=last_position,
                    is_completed=is_completed,
                    completion_rate=completion_rate,
                    last_watched_at=lecture_last_watched
                ))

                chapter_watched += watched_seconds
                chapter_duration += lecture.duration_seconds
                if is_completed:
                    chapter_completed += 1

                if lecture_last_watched:
                    if last_watched_at is None or lecture_last_watched > last_watched_at:
                        last_watched_at = lecture_last_watched

            total_watched_duration += chapter_watched
            total_completed += chapter_completed

            chapter_progress_rate = (chapter_completed / len(chapter.lectures) * 100) if len(chapter.lectures) > 0 else 0

            chapters_data.append(ChapterProgressSummary(
                chapter_id=chapter.id,
                chapter_title=chapter.title,
                total_lectures=len(chapter.lectures),
                completed_lectures=chapter_completed,
                total_duration=chapter_duration,
                watched_duration=chapter_watched,
                progress_rate=chapter_progress_rate,
                lectures=lectures_data
            ))

        # 전체 진행률 계산
        total_lectures = len(all_lecture_ids)
        progress_rate = (total_completed / total_lectures * 100) if total_lectures > 0 else 0

        return CourseProgressDetail(
            course_id=course.id,
            course_title=course.title,
            total_duration=course.total_duration,
            watched_duration=total_watched_duration,
            progress_rate=progress_rate,
            total_lectures=total_lectures,
            completed_lectures=total_completed,
            last_watched_at=last_watched_at,
            chapters=chapters_data
        )

    async def get_lecture_progress(
        self,
        user_id: int,
        lecture_id: int
    ) -> ProgressResponse:
        """강의 영상별 진행 조회"""

        # 강의 영상 조회
        lecture_result = await self.db.execute(
            select(Lecture).where(Lecture.id == lecture_id)
        )
        lecture = lecture_result.scalar_one_or_none()

        if not lecture:
            raise LectureNotFoundError(f'ID {lecture_id}인 강의 영상을 찾을 수 없습니다')

        # 진행 기록 조회
        progress_result = await self.db.execute(
            select(Progress).where(
                Progress.user_id == user_id,
                Progress.lecture_id == lecture_id
            )
        )
        progress = progress_result.scalar_one_or_none()

        if not progress:
            # 진행 기록이 없으면 기본값 반환
            now = get_current_utc_datetime()
            return ProgressResponse(
                id=0,
                user_id=user_id,
                lecture_id=lecture_id,
                lecture_title=lecture.title,
                watched_seconds=0,
                last_position=0,
                is_completed=False,
                completion_rate=0.0,
                last_watched_at=now,
                completed_at=None
            )

        return await self._build_progress_response(progress, lecture)

    async def get_student_dashboard(self, user_id: int) -> StudentDashboard:
        """학습자 대시보드"""

        # 총 수강 등록 수
        total_enrollments_result = await self.db.execute(
            select(func.count(Enrollment.id))
            .where(Enrollment.user_id == user_id)
        )
        total_enrollments = total_enrollments_result.scalar() or 0

        # 활성 수강 수
        active_enrollments_result = await self.db.execute(
            select(func.count(Enrollment.id))
            .where(
                Enrollment.user_id == user_id,
                Enrollment.is_active == True
            )
        )
        active_enrollments = active_enrollments_result.scalar() or 0

        # 완료한 강의 수 (진행률 100%)
        completed_courses_result = await self.db.execute(
            select(func.count(Enrollment.id))
            .where(
                Enrollment.user_id == user_id,
                Enrollment.progress_rate >= 100.0
            )
        )
        completed_courses = completed_courses_result.scalar() or 0

        # 평균 진행률
        avg_progress_result = await self.db.execute(
            select(func.avg(Enrollment.progress_rate))
            .where(
                Enrollment.user_id == user_id,
                Enrollment.is_active == True
            )
        )
        avg_progress_rate = avg_progress_result.scalar() or 0.0

        # 총 학습 시간 (분)
        total_study_time_result = await self.db.execute(
            select(func.sum(Progress.watched_seconds))
            .where(Progress.user_id == user_id)
        )
        total_study_seconds = total_study_time_result.scalar() or 0
        total_study_time = total_study_seconds // 60

        # TODO: 최근 활동, 만료 임박 강의 등은 나중에 추가
        recent_activities = []
        upcoming_expiries = []

        return StudentDashboard(
            total_enrollments=total_enrollments,
            active_enrollments=active_enrollments,
            completed_courses=completed_courses,
            total_study_time=total_study_time,
            avg_progress_rate=float(avg_progress_rate),
            recent_activities=recent_activities,
            upcoming_expiries=upcoming_expiries
        )

    # ==================== 헬퍼 메서드 ====================

    async def _build_enrollment_response(
        self,
        enrollment: Enrollment,
        course: Course
    ) -> EnrollmentResponse:
        """수강 등록 응답 생성"""

        total_lectures, completed_lectures = await self._get_lecture_counts(
            enrollment.user_id, course.id
        )

        return EnrollmentResponse(
            id=enrollment.id,
            user_id=enrollment.user_id,
            course_id=enrollment.course_id,
            course_title=course.title,
            course_thumbnail=course.thumbnail_url,
            category_name=course.category_type.value,
            difficulty=course.difficulty.value,
            enrolled_at=enrollment.enrolled_at,
            expires_at=enrollment.expires_at,
            is_active=enrollment.is_active,
            progress_rate=enrollment.progress_rate,
            days_until_expiry=get_days_until(enrollment.expires_at),
            total_lectures=total_lectures,
            completed_lectures=completed_lectures
        )

    async def _build_progress_response(
        self,
        progress: Progress,
        lecture: Lecture
    ) -> ProgressResponse:
        """학습 진행 응답 생성"""

        completion_rate = (
            progress.watched_seconds / lecture.duration_seconds * 100
        ) if lecture.duration_seconds > 0 else 0

        return ProgressResponse(
            id=progress.id,
            user_id=progress.user_id,
            lecture_id=progress.lecture_id,
            lecture_title=lecture.title,
            watched_seconds=progress.watched_seconds,
            last_position=progress.last_position,
            is_completed=progress.is_completed,
            completion_rate=completion_rate,
            last_watched_at=progress.last_watched_at,
            completed_at=progress.completed_at
        )

    async def _get_lecture_counts(
        self,
        user_id: int,
        course_id: int
    ) -> tuple[int, int]:
        """총 강의 수와 완료된 강의 수 반환"""

        # 총 강의 수
        total_result = await self.db.execute(
            select(func.count(Lecture.id))
            .join(Chapter, Lecture.chapter_id == Chapter.id)
            .where(Chapter.course_id == course_id)
        )
        total_lectures = total_result.scalar() or 0

        # 완료된 강의 수
        completed_result = await self.db.execute(
            select(func.count(Progress.id))
            .join(Lecture, Progress.lecture_id == Lecture.id)
            .join(Chapter, Lecture.chapter_id == Chapter.id)
            .where(
                Chapter.course_id == course_id,
                Progress.user_id == user_id,
                Progress.is_completed == True
            )
        )
        completed_lectures = completed_result.scalar() or 0

        return total_lectures, completed_lectures

    async def _get_total_watched_duration(
        self,
        user_id: int,
        course_id: int
    ) -> int:
        """총 시청 시간 반환 (초)"""

        result = await self.db.execute(
            select(func.sum(Progress.watched_seconds))
            .join(Lecture, Progress.lecture_id == Lecture.id)
            .join(Chapter, Lecture.chapter_id == Chapter.id)
            .where(
                Chapter.course_id == course_id,
                Progress.user_id == user_id
            )
        )

        return result.scalar() or 0

    async def _update_course_progress(
        self,
        user_id: int,
        course_id: int
    ):
        """강의 진행률 업데이트"""

        total_lectures, completed_lectures = await self._get_lecture_counts(
            user_id, course_id
        )

        progress_rate = (
            completed_lectures / total_lectures * 100
        ) if total_lectures > 0 else 0

        # Enrollment 업데이트
        result = await self.db.execute(
            select(Enrollment).where(
                Enrollment.user_id == user_id,
                Enrollment.course_id == course_id
            )
        )
        enrollment = result.scalar_one_or_none()

        if enrollment:
            enrollment.progress_rate = progress_rate
            await self.db.commit()

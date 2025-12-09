from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_
from sqlalchemy.orm import selectinload, joinedload
from datetime import datetime, timedelta
import math

from app.models.progress import Enrollment, Progress
from app.models.course import Course, Chapter, Lecture
from app.models.user import User
from app.schemas.enrollment import (
    ProgressCreate,
    ProgressUpdate,
    ProgressResponse,
    CourseProgressDetail,
    ChapterProgressSummary,
    LectureProgressSummary,
    StudentDashboard,
    MyCourseListParams,
    MyCoursePaginatedResponse,
    MyCourseSummary,
    MyCourseDetail,
    MyChapterWithLectures,
    MyLectureProgress,
    EnrollmentStatus,
    LearningStatus,
)
from app.exceptions.base import (
    CourseNotFoundError,
    EnrollmentNotFoundError,
    LectureNotFoundError,
    ProgressNotFoundError,
)
from app.utils.helpers import get_current_utc_datetime, get_days_until


class EnrollmentService:

    def __init__(self, db: AsyncSession):
        self.db = db

    # ==================== 학습 진행 ====================

    async def create_progress(
        self,
        user_id: int,
        data: ProgressCreate
    ) -> ProgressResponse:
        """학습 진행 생성 또는 업데이트 (Upsert)"""

        # 강의 영상 존재 확인 (chapter와 course_id도 함께 로드)
        lecture_result = await self.db.execute(
            select(Lecture)
            .options(joinedload(Lecture.chapter))
            .where(Lecture.id == data.lecture_id)
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
            # 이미 존재하면 자동으로 업데이트 (Upsert 패턴)
            return await self.update_progress(user_id, data.lecture_id, ProgressUpdate(
                watched_seconds=data.watched_seconds,
                last_position=data.last_position,
                is_completed=data.is_completed
            ))

        # 새로운 진행 기록 생성
        now = get_current_utc_datetime()

        # last_position을 duration_seconds 이하로 제한
        last_position = min(data.last_position, lecture.duration_seconds) if lecture.duration_seconds > 0 else 0

        # unique_watched_seconds 계산 (진행률 계산용)
        # last_position을 기준으로 유니크 시청 시간 계산
        unique_watched_seconds = last_position

        # 시청률이 95% 이상이면 자동으로 완료 처리
        is_completed = data.is_completed
        completed_at = None

        if lecture.duration_seconds > 0:
            completion_rate = (unique_watched_seconds / lecture.duration_seconds) * 100
            if completion_rate >= 95 or data.is_completed:
                is_completed = True
                completed_at = now
        elif data.is_completed:
            completed_at = now

        progress = Progress(
            user_id=user_id,
            lecture_id=data.lecture_id,
            watched_seconds=data.watched_seconds,
            unique_watched_seconds=unique_watched_seconds,
            last_position=last_position,
            is_completed=is_completed,
            last_watched_at=now,
            completed_at=completed_at
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

        # 진행 기록 조회 (lecture와 chapter도 함께 로드)
        result = await self.db.execute(
            select(Progress)
            .options(
                joinedload(Progress.lecture)
                .joinedload(Lecture.chapter)
            )
            .where(
                Progress.user_id == user_id,
                Progress.lecture_id == lecture_id
            )
        )
        progress = result.scalar_one_or_none()

        if not progress:
            raise ProgressNotFoundError('학습 진행 기록을 찾을 수 없습니다')

        # last_position을 duration_seconds 이하로 제한
        last_position = min(data.last_position, progress.lecture.duration_seconds) if progress.lecture.duration_seconds > 0 else 0

        # unique_watched_seconds 계산 (진행률 계산용)
        # last_position 값을 unique_watched_seconds로 사용
        unique_watched_seconds = max(progress.unique_watched_seconds or 0, last_position)

        # 업데이트
        progress.watched_seconds = data.watched_seconds
        progress.unique_watched_seconds = unique_watched_seconds
        progress.last_position = last_position
        progress.last_watched_at = get_current_utc_datetime()

        # 시청률이 95% 이상이면 자동으로 완료 처리
        if progress.lecture.duration_seconds > 0:
            completion_rate = (unique_watched_seconds / progress.lecture.duration_seconds) * 100
            if completion_rate >= 95 or data.is_completed:
                progress.is_completed = True
                if progress.completed_at is None:
                    progress.completed_at = get_current_utc_datetime()
            else:
                progress.is_completed = data.is_completed
        else:
            progress.is_completed = data.is_completed
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

                # watched_seconds는 누적 시청 시간 (분석용)
                watched_seconds = progress.watched_seconds if progress else 0
                # unique_watched_seconds는 유니크 시청 시간 (진행률 계산용)
                unique_watched_seconds = progress.unique_watched_seconds if progress else 0
                last_position = progress.last_position if progress else 0
                is_completed = progress.is_completed if progress else False
                lecture_last_watched = progress.last_watched_at if progress else None

                # unique_watched_seconds를 사용하여 completion_rate 계산
                completion_rate = (unique_watched_seconds / lecture.duration_seconds * 100) if lecture.duration_seconds > 0 else 0
                # 100% 초과 방지
                completion_rate = min(completion_rate, 100.0)

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

                # 챕터 진행률 계산에는 unique_watched_seconds 사용
                chapter_watched += unique_watched_seconds
                chapter_duration += lecture.duration_seconds
                if is_completed:
                    chapter_completed += 1

                if lecture_last_watched:
                    if last_watched_at is None or lecture_last_watched > last_watched_at:
                        last_watched_at = lecture_last_watched

            total_watched_duration += chapter_watched
            total_completed += chapter_completed

            # 챕터 진행률: 시간 기반
            chapter_progress_rate = (chapter_watched / chapter_duration * 100) if chapter_duration > 0 else 0
            chapter_progress_rate = min(chapter_progress_rate, 100.0)

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

        # 전체 진행률 계산: 시간 기반
        total_lectures = len(all_lecture_ids)
        progress_rate = (total_watched_duration / course.total_duration * 100) if course.total_duration > 0 else 0
        progress_rate = min(progress_rate, 100.0)

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

        return StudentDashboard(
            total_enrollments=total_enrollments,
            active_enrollments=active_enrollments,
            completed_courses=completed_courses,
            total_study_time=total_study_time,
            avg_progress_rate=float(avg_progress_rate)
        )

    # ==================== 헬퍼 메서드 ====================

    async def _build_progress_response(
        self,
        progress: Progress,
        lecture: Lecture
    ) -> ProgressResponse:
        """학습 진행 응답 생성"""

        # unique_watched_seconds를 사용하여 completion_rate 계산
        completion_rate = (
            progress.unique_watched_seconds / lecture.duration_seconds * 100
        ) if lecture.duration_seconds > 0 else 0

        # 100% 초과 방지
        completion_rate = min(completion_rate, 100.0)

        # 시청률이 95% 이상이면 완료로 간주
        is_completed = progress.is_completed
        if lecture.duration_seconds > 0 and completion_rate >= 95:
            is_completed = True

        return ProgressResponse(
            id=progress.id,
            user_id=progress.user_id,
            lecture_id=progress.lecture_id,
            lecture_title=lecture.title,
            watched_seconds=progress.watched_seconds,
            last_position=progress.last_position,
            is_completed=is_completed,
            completion_rate=completion_rate,
            last_watched_at=progress.last_watched_at,
            completed_at=progress.completed_at
        )

    async def _get_total_watched_duration(
        self,
        user_id: int,
        course_id: int
    ) -> int:
        """총 유니크 시청 시간 반환 (초) - 진행률 계산용"""

        result = await self.db.execute(
            select(func.sum(Progress.unique_watched_seconds))
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
        """강의 진행률 업데이트 (시간 기반)"""

        # 강의 조회 (총 시간)
        course_result = await self.db.execute(
            select(Course).where(Course.id == course_id)
        )
        course = course_result.scalar_one_or_none()

        if not course:
            return

        # 총 시청 시간 조회
        total_watched = await self._get_total_watched_duration(user_id, course_id)

        # 시간 기반 진행률 계산
        progress_rate = (
            total_watched / course.total_duration * 100
        ) if course.total_duration > 0 else 0

        # 100% 초과 방지
        progress_rate = min(progress_rate, 100.0)

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

    # ==================== 내 강의실 ====================

    async def get_my_courses(
        self,
        user_id: int,
        params: MyCourseListParams
    ) -> MyCoursePaginatedResponse:
        """내 강의 목록 조회"""

        # 서브쿼리: 강의별 총 강의 영상 수
        total_lectures_subquery = (
            select(
                Chapter.course_id,
                func.count(Lecture.id).label('total_lectures')
            )
            .join(Lecture, Chapter.id == Lecture.chapter_id)
            .group_by(Chapter.course_id)
            .subquery()
        )

        # 서브쿼리: 사용자가 완료한 강의 영상 수
        completed_lectures_subquery = (
            select(
                Chapter.course_id,
                func.count(Progress.id).label('completed_lectures')
            )
            .join(Lecture, Chapter.id == Lecture.chapter_id)
            .join(
                Progress,
                and_(
                    Progress.lecture_id == Lecture.id,
                    Progress.user_id == user_id,
                    Progress.is_completed == True
                )
            )
            .group_by(Chapter.course_id)
            .subquery()
        )

        # 서브쿼리: 최근 시청 정보
        latest_progress_subquery = (
            select(
                Chapter.course_id,
                Chapter.title.label('chapter_title'),
                Lecture.title.label('lecture_title'),
                Progress.updated_at.label('last_watched_at')
            )
            .join(Lecture, Chapter.id == Lecture.chapter_id)
            .join(
                Progress,
                and_(
                    Progress.lecture_id == Lecture.id,
                    Progress.user_id == user_id
                )
            )
            .distinct(Chapter.course_id)
            .order_by(Chapter.course_id, Progress.updated_at.desc())
            .subquery()
        )

        # 메인 쿼리
        query = (
            select(
                Course,
                Enrollment,
                func.coalesce(total_lectures_subquery.c.total_lectures, 0).label('total_lectures'),
                func.coalesce(completed_lectures_subquery.c.completed_lectures, 0).label('completed_lectures'),
                latest_progress_subquery.c.chapter_title,
                latest_progress_subquery.c.lecture_title,
                latest_progress_subquery.c.last_watched_at
            )
            .join(Enrollment, Course.id == Enrollment.course_id)
            .outerjoin(
                total_lectures_subquery,
                Course.id == total_lectures_subquery.c.course_id
            )
            .outerjoin(
                completed_lectures_subquery,
                Course.id == completed_lectures_subquery.c.course_id
            )
            .outerjoin(
                latest_progress_subquery,
                Course.id == latest_progress_subquery.c.course_id
            )
            .where(
                Enrollment.user_id == user_id,
                Enrollment.is_active == True
            )
        )

        # 필터링: 강의 유형
        if params.course_type:
            query = query.where(Course.course_type == params.course_type)

        # 필터링: 카테고리
        if params.category_type:
            query = query.where(Course.category_type == params.category_type)

        # 필터링: 난이도
        if params.difficulty:
            query = query.where(Course.difficulty == params.difficulty)

        # 필터링: 수강 상태 (학습 가능 / 만료)
        from app.utils.helpers import get_current_utc_datetime
        now = get_current_utc_datetime()
        if params.enrollment_status == EnrollmentStatus.AVAILABLE:
            query = query.where(
                or_(
                    Enrollment.expires_at.is_(None),
                    Enrollment.expires_at > now
                )
            )
        elif params.enrollment_status == EnrollmentStatus.EXPIRED:
            query = query.where(
                and_(
                    Enrollment.expires_at.isnot(None),
                    Enrollment.expires_at <= now
                )
            )

        # 필터링: 학습 상태 (학습 예정 / 학습 중 / 학습 완료)
        if params.learning_status == LearningStatus.NOT_STARTED:
            query = query.where(Enrollment.progress_rate == 0)
        elif params.learning_status == LearningStatus.IN_PROGRESS:
            query = query.where(
                and_(
                    Enrollment.progress_rate > 0,
                    Enrollment.progress_rate < 100
                )
            )
        elif params.learning_status == LearningStatus.COMPLETED:
            query = query.where(Enrollment.progress_rate >= 100)

        # 정렬 (최근 수강 등록순)
        query = query.order_by(Enrollment.created_at.desc())

        # 전체 개수
        count_query = select(func.count()).select_from(query.subquery())
        total_result = await self.db.execute(count_query)
        total = total_result.scalar() or 0

        # 페이지네이션
        offset = (params.page - 1) * params.page_size
        query = query.offset(offset).limit(params.page_size)

        result = await self.db.execute(query)
        rows = result.all()

        # 응답 데이터 생성
        items = []
        for course, enrollment, total_lectures, completed_lectures, chapter_title, lecture_title, last_watched_at in rows:
            # 수강 상태 계산
            enrollment_status = EnrollmentStatus.AVAILABLE
            if enrollment.expires_at and enrollment.expires_at <= now:
                enrollment_status = EnrollmentStatus.EXPIRED

            # 학습 상태 계산
            learning_status = LearningStatus.NOT_STARTED
            if enrollment.progress_rate >= 100:
                learning_status = LearningStatus.COMPLETED
            elif enrollment.progress_rate > 0:
                learning_status = LearningStatus.IN_PROGRESS

            item = MyCourseSummary(
                id=course.id,
                title=course.title,
                thumbnail_url=course.thumbnail_url,
                course_type=course.course_type,
                category_type=course.category_type,
                difficulty=course.difficulty,
                instructor_name=course.instructor_name,
                total_lectures=total_lectures,
                completed_lectures=completed_lectures,
                progress_rate=enrollment.progress_rate,
                enrollment_status=enrollment_status,
                learning_status=learning_status,
                enrolled_at=enrollment.created_at,
                expires_at=enrollment.expires_at,
                last_watched_chapter=chapter_title,
                last_watched_lecture=lecture_title,
                last_watched_at=last_watched_at
            )
            items.append(item)

        total_pages = math.ceil(total / params.page_size) if total > 0 else 0

        return MyCoursePaginatedResponse(
            items=items,
            total=total,
            page=params.page,
            page_size=params.page_size,
            total_pages=total_pages,
        )

    async def get_my_course_detail(
        self,
        user_id: int,
        course_id: int
    ) -> MyCourseDetail:
        """내 강의 상세 조회"""

        # 수강 등록 확인
        enrollment_result = await self.db.execute(
            select(Enrollment)
            .where(
                Enrollment.user_id == user_id,
                Enrollment.course_id == course_id,
                Enrollment.is_active == True
            )
        )
        enrollment = enrollment_result.scalar_one_or_none()

        if not enrollment:
            raise EnrollmentNotFoundError(f'수강 등록 정보를 찾을 수 없습니다')

        # 강의 조회 (챕터와 강의 영상 eager loading)
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
        lecture_ids = []
        for chapter in course.chapters:
            for lecture in chapter.lectures:
                lecture_ids.append(lecture.id)

        # 진행 정보 조회
        progress_dict = {}
        total_lectures = len(lecture_ids)
        completed_lectures = 0
        last_watched_chapter_id = None
        last_watched_lecture_id = None
        last_watched_at = None

        if lecture_ids:
            # 한 번의 쿼리로 모든 Progress 가져오기
            progress_result = await self.db.execute(
                select(Progress)
                .where(
                    Progress.user_id == user_id,
                    Progress.lecture_id.in_(lecture_ids)
                )
                .order_by(Progress.updated_at.desc())
            )
            progresses = progress_result.scalars().all()

            # Dictionary로 변환 및 통계 계산
            for progress in progresses:
                progress_dict[progress.lecture_id] = progress
                if progress.is_completed:
                    completed_lectures += 1

            # 가장 최근 시청한 강의 찾기
            if progresses:
                latest_progress = progresses[0]
                last_watched_lecture_id = latest_progress.lecture_id
                last_watched_at = latest_progress.updated_at

                # 해당 강의가 속한 챕터 찾기
                for chapter in course.chapters:
                    for lecture in chapter.lectures:
                        if lecture.id == last_watched_lecture_id:
                            last_watched_chapter_id = chapter.id
                            break
                    if last_watched_chapter_id:
                        break

        # 수강 상태 계산
        from app.utils.helpers import get_current_utc_datetime
        now = get_current_utc_datetime()
        enrollment_status = EnrollmentStatus.AVAILABLE
        if enrollment.expires_at and enrollment.expires_at <= now:
            enrollment_status = EnrollmentStatus.EXPIRED

        # 학습 상태 계산
        learning_status = LearningStatus.NOT_STARTED
        if enrollment.progress_rate >= 100:
            learning_status = LearningStatus.COMPLETED
        elif enrollment.progress_rate > 0:
            learning_status = LearningStatus.IN_PROGRESS

        # 챕터 및 강의 영상 데이터 변환
        chapters_data = []
        sorted_chapters = sorted(course.chapters, key=lambda c: c.order_number)

        for chapter in sorted_chapters:
            sorted_lectures = sorted(chapter.lectures, key=lambda l: l.order_number)
            chapter_duration = sum(lecture.duration_seconds for lecture in sorted_lectures)

            lectures_data = []
            for lecture in sorted_lectures:
                # Progress 정보 가져오기
                progress = progress_dict.get(lecture.id)

                # 완료 여부 계산 (시청률 95% 이상이면 자동 완료)
                is_completed = False
                watched_seconds = 0
                last_position = 0

                if progress:
                    watched_seconds = progress.watched_seconds
                    last_position = progress.last_position

                    if lecture.duration_seconds > 0:
                        completion_rate = (watched_seconds / lecture.duration_seconds) * 100
                        is_completed = completion_rate >= 95 or progress.is_completed
                    else:
                        is_completed = progress.is_completed

                lecture_data = MyLectureProgress(
                    id=lecture.id,
                    chapter_id=lecture.chapter_id,
                    title=lecture.title,
                    description=lecture.description,
                    video_url=lecture.video_url,
                    video_type=lecture.video_type,
                    duration_seconds=lecture.duration_seconds,
                    order_number=lecture.order_number,
                    material_url=lecture.material_url,
                    created_at=lecture.created_at,
                    updated_at=lecture.updated_at,
                    is_completed=is_completed,
                    last_position=last_position,
                    watched_seconds=watched_seconds
                )
                lectures_data.append(lecture_data)

            chapter_data = MyChapterWithLectures(
                id=chapter.id,
                course_id=chapter.course_id,
                title=chapter.title,
                description=chapter.description,
                order_number=chapter.order_number,
                total_duration=chapter_duration,
                lectures=lectures_data
            )
            chapters_data.append(chapter_data)

        # 강의 상세 응답 생성
        course_detail = MyCourseDetail(
            id=course.id,
            category_type=course.category_type,
            course_type=course.course_type,
            title=course.title,
            description=course.description,
            thumbnail_url=course.thumbnail_url,
            instructor_name=course.instructor_name,
            instructor_bio=course.instructor_bio,
            instructor_description=course.instructor_description,
            instructor_image=course.instructor_image,
            price_type=course.price_type,
            price=course.price,
            difficulty=course.difficulty,
            total_duration=course.total_duration,
            enrollment_status=enrollment_status,
            learning_status=learning_status,
            enrolled_at=enrollment.created_at,
            expires_at=enrollment.expires_at,
            total_lectures=total_lectures,
            completed_lectures=completed_lectures,
            progress_rate=enrollment.progress_rate,
            last_watched_chapter_id=last_watched_chapter_id,
            last_watched_lecture_id=last_watched_lecture_id,
            last_watched_at=last_watched_at,
            chapters=chapters_data,
            created_at=course.created_at,
            updated_at=course.updated_at
        )

        return course_detail

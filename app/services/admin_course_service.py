"""
관리자 강의 관리 서비스

이 모듈은 관리자가 강의, 챕터, 강의 영상을 생성/수정/삭제하는 비즈니스 로직을 제공합니다.
"""

from typing import List, Optional
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, or_, and_, case
from sqlalchemy.orm import selectinload
import math

from app.models.course import Course, Chapter, Lecture
from app.models.progress import Enrollment, Progress
from app.models.payment import Payment
from app.schemas.course import (
    CourseCreate, CourseUpdate, CourseResponse,
    ChapterCreate, ChapterUpdate, ChapterResponse,
    LectureCreate, LectureUpdate, LectureResponse,
)
from app.schemas.admin import (
    CourseManagementListParams,
    CourseManagementPaginatedResponse,
    CourseManagementResponse,
)
from app.utils.cache import invalidate_course_cache
from app.exceptions.base import (
    CourseNotFoundError,
    ChapterNotFoundError,
    LectureNotFoundError,
    BadRequestError,
)
from app.core.logging_config import configure_logging
from app.utils.helpers import get_current_utc_datetime
from app.utils.video_duration import get_video_duration
from app.core.config import settings

logger = configure_logging()


class AdminCourseService:
    """관리자 강의 관리 서비스"""

    def __init__(self, db: AsyncSession):
        self.db = db

    # ==================== 파일 업로드 ====================
    # 파일 업로드 기능은 /storage API를 사용하세요
    # - POST /storage/upload/image - 이미지 업로드
    # - POST /storage/upload/video - 동영상 업로드
    # - POST /storage/upload - 일반 파일 업로드
    # - DELETE /storage/delete/{file_path} - 파일 삭제
    # - GET /storage/list - 파일 목록 조회

    # ==================== 강의 관리 ====================

    async def get_courses_for_admin(
        self,
        params: CourseManagementListParams
    ) -> CourseManagementPaginatedResponse:
        """관리자용 강의 목록 조회 (수강생 수, 매출, 진행률 포함)"""

        # 서브쿼리: 강의별 수강 인원 및 평균 진행률
        enrollment_subquery = (
            select(
                Enrollment.course_id,
                func.count(Enrollment.id).label('enrollment_count'),
                func.avg(Enrollment.progress_rate).label('avg_progress')
            )
            .where(Enrollment.is_active == True)
            .group_by(Enrollment.course_id)
            .subquery()
        )

        # 서브쿼리: 강의별 총 매출
        payment_subquery = (
            select(
                Payment.course_id,
                func.sum(Payment.final_amount).label('total_revenue')
            )
            .where(Payment.status == 'completed')
            .group_by(Payment.course_id)
            .subquery()
        )

        # 서브쿼리: 강의별 완료율 (진행률 100% 달성한 수강생 수)
        completion_subquery = (
            select(
                Enrollment.course_id,
                func.count(
                    case(
                        (Enrollment.progress_rate >= 100, 1),
                        else_=None
                    )
                ).label('completion_count')
            )
            .where(Enrollment.is_active == True)
            .group_by(Enrollment.course_id)
            .subquery()
        )

        # 서브쿼리: 강의별 챕터 개수
        chapter_subquery = (
            select(
                Chapter.course_id,
                func.count(Chapter.id).label('chapter_count')
            )
            .group_by(Chapter.course_id)
            .subquery()
        )

        # 메인 쿼리
        query = (
            select(
                Course,
                func.coalesce(enrollment_subquery.c.enrollment_count, 0).label('enrollment_count'),
                func.coalesce(enrollment_subquery.c.avg_progress, 0.0).label('avg_progress'),
                func.coalesce(payment_subquery.c.total_revenue, 0).label('total_revenue'),
                func.coalesce(completion_subquery.c.completion_count, 0).label('completion_count'),
                func.coalesce(chapter_subquery.c.chapter_count, 0).label('chapter_count')
            )
            .outerjoin(
                enrollment_subquery,
                Course.id == enrollment_subquery.c.course_id
            )
            .outerjoin(
                payment_subquery,
                Course.id == payment_subquery.c.course_id
            )
            .outerjoin(
                completion_subquery,
                Course.id == completion_subquery.c.course_id
            )
            .outerjoin(
                chapter_subquery,
                Course.id == chapter_subquery.c.course_id
            )
        )

        # 필터링
        if params.category_type:
            query = query.where(Course.category_type == params.category_type)

        if params.difficulty:
            query = query.where(Course.difficulty == params.difficulty)

        if params.is_published is not None:
            query = query.where(Course.is_published == params.is_published)

        if params.keyword:
            keyword_filter = or_(
                Course.title.ilike(f'%{params.keyword}%'),
                Course.instructor_name.ilike(f'%{params.keyword}%')
            )
            query = query.where(keyword_filter)

        # 정렬 (최신순)
        query = query.order_by(Course.created_at.desc())

        # 전체 개수
        count_query = select(func.count()).select_from(query.subquery())
        total_result = await self.db.execute(count_query)
        total = total_result.scalar()

        # 페이지네이션
        offset = (params.page - 1) * params.page_size
        query = query.offset(offset).limit(params.page_size)

        result = await self.db.execute(query)
        rows = result.all()

        # 응답 데이터 생성
        items = []
        for course, enrollment_count, avg_progress, total_revenue, completion_count, chapter_count in rows:
            # 완료율 계산 (완료한 수강생 수 / 전체 수강생 수 * 100)
            completion_rate = 0.0
            if enrollment_count > 0:
                completion_rate = (completion_count / enrollment_count) * 100

            item = CourseManagementResponse(
                id=course.id,
                title=course.title,
                category_name=course.category_type.value,
                instructor_name=course.instructor_name,
                difficulty=course.difficulty.value,
                price=course.price,
                total_duration=course.total_duration,
                chapter_count=chapter_count,
                enrollment_count=enrollment_count,
                is_published=course.is_published,
                created_at=course.created_at,
                total_revenue=total_revenue,
                avg_progress=round(avg_progress, 2),
                completion_rate=round(completion_rate, 2)
            )
            items.append(item)

        total_pages = math.ceil(total / params.page_size) if total > 0 else 0

        return CourseManagementPaginatedResponse(
            items=items,
            total=total,
            page=params.page,
            page_size=params.page_size,
            total_pages=total_pages,
        )

    async def get_course_by_id(self, course_id: int) -> CourseResponse:
        """관리자용 강의 상세 조회"""

        # 강의 조회
        result = await self.db.execute(
            select(Course).where(Course.id == course_id)
        )
        course = result.scalar_one_or_none()

        if not course:
            raise CourseNotFoundError(f'ID {course_id}인 강의를 찾을 수 없습니다')

        # 수강 인원 수 조회
        enrollment_result = await self.db.execute(
            select(func.count(Enrollment.id))
            .where(
                Enrollment.course_id == course_id,
                Enrollment.is_active == True
            )
        )
        enrollment_count = enrollment_result.scalar() or 0

        course_response = CourseResponse.model_validate(course)
        course_response.enrollment_count = enrollment_count

        return course_response

    async def create_course(self, data: CourseCreate) -> CourseResponse:
        """강의 생성"""

        # 새 강의 생성
        new_course = Course(
            category_type=data.category_type,
            course_type=data.course_type,
            title=data.title,
            description=data.description,
            thumbnail_url=data.thumbnail_url,
            instructor_name=data.instructor_name,
            instructor_bio=data.instructor_bio,
            instructor_description=data.instructor_description,
            instructor_image=data.instructor_image,
            difficulty=data.difficulty,
            price_type=data.price_type,
            price=data.price,
            access_duration_days=data.access_duration_days,
            max_students=data.max_students,
            recruitment_start_date=data.recruitment_start_date,
            recruitment_end_date=data.recruitment_end_date,
            course_start_date=data.course_start_date,
            course_end_date=data.course_end_date,
            student_reviews=data.student_reviews,
            faq=data.faq,
            is_published=False,  # 기본값: 비공개
            total_duration=0  # 초기값: 0초
        )

        self.db.add(new_course)
        await self.db.commit()
        await self.db.refresh(new_course)

        # 응답 생성
        course_response = CourseResponse.model_validate(new_course)
        course_response.enrollment_count = 0

        return course_response

    async def update_course(
        self,
        course_id: int,
        data: CourseUpdate
    ) -> CourseResponse:
        """강의 수정"""

        # 강의 조회
        result = await self.db.execute(
            select(Course).where(Course.id == course_id)
        )
        course = result.scalar_one_or_none()

        if not course:
            raise CourseNotFoundError(f'ID {course_id}인 강의를 찾을 수 없습니다')

        # 업데이트할 필드만 수정
        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(course, field, value)

        await self.db.commit()
        await self.db.refresh(course)

        # 캐시 무효화
        await invalidate_course_cache(course_id)

        # 수강 인원 수 조회
        enrollment_result = await self.db.execute(
            select(func.count(Enrollment.id))
            .where(
                Enrollment.course_id == course_id,
                Enrollment.is_active == True
            )
        )
        enrollment_count = enrollment_result.scalar() or 0

        course_response = CourseResponse.model_validate(course)
        course_response.enrollment_count = enrollment_count

        return course_response

    async def delete_course(self, course_id: int) -> None:
        """강의 삭제 (CASCADE로 챕터, 강의 영상 모두 삭제됨)"""

        # 강의 조회
        result = await self.db.execute(
            select(Course).where(Course.id == course_id)
        )
        course = result.scalar_one_or_none()

        if not course:
            raise CourseNotFoundError(f'ID {course_id}인 강의를 찾을 수 없습니다')

        # 강의 삭제 (CASCADE로 연결된 데이터도 삭제)
        await self.db.delete(course)
        await self.db.commit()

        # 캐시 무효화
        await invalidate_course_cache(course_id)

    async def publish_course(self, course_id: int) -> None:
        """강의 공개"""

        result = await self.db.execute(
            select(Course).where(Course.id == course_id)
        )
        course = result.scalar_one_or_none()

        if not course:
            raise CourseNotFoundError(f'ID {course_id}인 강의를 찾을 수 없습니다')

        course.is_published = True
        await self.db.commit()

        # 캐시 무효화
        await invalidate_course_cache(course_id)

    async def unpublish_course(self, course_id: int) -> None:
        """강의 비공개"""

        result = await self.db.execute(
            select(Course).where(Course.id == course_id)
        )
        course = result.scalar_one_or_none()

        if not course:
            raise CourseNotFoundError(f'ID {course_id}인 강의를 찾을 수 없습니다')

        course.is_published = False
        await self.db.commit()

        # 캐시 무효화
        await invalidate_course_cache(course_id)

    # ==================== 챕터 관리 ====================

    async def get_chapters(self, course_id: int) -> List[ChapterResponse]:
        """특정 강의의 챕터 목록 조회"""

        # 강의 존재 확인
        course_result = await self.db.execute(
            select(Course).where(Course.id == course_id)
        )
        if not course_result.scalar_one_or_none():
            raise CourseNotFoundError(f'ID {course_id}인 강의를 찾을 수 없습니다')

        # 서브쿼리: 챕터별 총 재생 시간 계산 (N+1 쿼리 문제 방지)
        duration_subquery = (
            select(
                Lecture.chapter_id,
                func.sum(Lecture.duration_seconds).label('total_duration')
            )
            .group_by(Lecture.chapter_id)
            .subquery()
        )

        # 챕터 목록 조회 with LEFT JOIN (한 번의 쿼리로 처리)
        query = (
            select(
                Chapter,
                func.coalesce(duration_subquery.c.total_duration, 0).label('total_duration')
            )
            .outerjoin(
                duration_subquery,
                Chapter.id == duration_subquery.c.chapter_id
            )
            .where(Chapter.course_id == course_id)
            .order_by(Chapter.order_number.asc())
        )

        result = await self.db.execute(query)
        rows = result.all()

        # 응답 생성
        chapter_responses = []
        for chapter, total_duration in rows:
            chapter_response = ChapterResponse.model_validate(chapter)
            chapter_response.total_duration = total_duration
            chapter_responses.append(chapter_response)

        return chapter_responses

    async def create_chapter(
        self,
        course_id: int,
        data: ChapterCreate
    ) -> ChapterResponse:
        """챕터 생성"""

        # 강의 존재 확인
        course_result = await self.db.execute(
            select(Course).where(Course.id == course_id)
        )
        course = course_result.scalar_one_or_none()

        if not course:
            raise CourseNotFoundError(f'ID {course_id}인 강의를 찾을 수 없습니다')

        # 새 챕터 생성
        new_chapter = Chapter(
            course_id=course_id,
            title=data.title,
            description=data.description,
            order_number=data.order_number
        )

        self.db.add(new_chapter)
        await self.db.commit()
        await self.db.refresh(new_chapter)

        # 응답 생성
        chapter_response = ChapterResponse.model_validate(new_chapter)
        chapter_response.total_duration = 0

        return chapter_response

    async def update_chapter(
        self,
        course_id: int,
        chapter_id: int,
        data: ChapterUpdate
    ) -> ChapterResponse:
        """챕터 수정"""

        # 강의 존재 확인
        course_result = await self.db.execute(
            select(Course).where(Course.id == course_id)
        )
        if not course_result.scalar_one_or_none():
            raise CourseNotFoundError(f'ID {course_id}인 강의를 찾을 수 없습니다')

        # 챕터 조회
        chapter_result = await self.db.execute(
            select(Chapter).where(
                Chapter.id == chapter_id,
                Chapter.course_id == course_id
            )
        )
        chapter = chapter_result.scalar_one_or_none()

        if not chapter:
            raise ChapterNotFoundError(f'ID {chapter_id}인 챕터를 찾을 수 없습니다')

        # 업데이트할 필드만 수정
        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(chapter, field, value)

        await self.db.commit()
        await self.db.refresh(chapter)

        # 챕터별 총 재생 시간 계산
        duration_result = await self.db.execute(
            select(func.sum(Lecture.duration_seconds))
            .where(Lecture.chapter_id == chapter_id)
        )
        total_duration = duration_result.scalar() or 0

        chapter_response = ChapterResponse.model_validate(chapter)
        chapter_response.total_duration = total_duration

        return chapter_response

    async def delete_chapter(self, course_id: int, chapter_id: int) -> None:
        """챕터 삭제 (CASCADE로 강의 영상도 삭제됨)"""

        # 강의 존재 확인
        course_result = await self.db.execute(
            select(Course).where(Course.id == course_id)
        )
        if not course_result.scalar_one_or_none():
            raise CourseNotFoundError(f'ID {course_id}인 강의를 찾을 수 없습니다')

        # 챕터 조회
        chapter_result = await self.db.execute(
            select(Chapter).where(
                Chapter.id == chapter_id,
                Chapter.course_id == course_id
            )
        )
        chapter = chapter_result.scalar_one_or_none()

        if not chapter:
            raise ChapterNotFoundError(f'ID {chapter_id}인 챕터를 찾을 수 없습니다')

        # 삭제된 강의 영상들의 총 시간 계산
        duration_result = await self.db.execute(
            select(func.sum(Lecture.duration_seconds))
            .where(Lecture.chapter_id == chapter_id)
        )
        deleted_duration = duration_result.scalar() or 0

        # 챕터 삭제
        await self.db.delete(chapter)
        await self.db.commit()

        # 강의 전체 시간 업데이트
        await self._update_course_total_duration(course_id, -deleted_duration)

    # ==================== 강의 영상 관리 ====================

    async def get_lectures(
        self,
        course_id: int,
        chapter_id: int
    ) -> List[LectureResponse]:
        """특정 챕터의 강의 영상 목록 조회"""

        # 강의 존재 확인
        course_result = await self.db.execute(
            select(Course).where(Course.id == course_id)
        )
        if not course_result.scalar_one_or_none():
            raise CourseNotFoundError(f'ID {course_id}인 강의를 찾을 수 없습니다')

        # 챕터 존재 확인
        chapter_result = await self.db.execute(
            select(Chapter).where(
                Chapter.id == chapter_id,
                Chapter.course_id == course_id
            )
        )
        if not chapter_result.scalar_one_or_none():
            raise ChapterNotFoundError(f'ID {chapter_id}인 챕터를 찾을 수 없습니다')

        # 강의 영상 목록 조회 (order_number 순서로 정렬)
        lectures_result = await self.db.execute(
            select(Lecture)
            .where(Lecture.chapter_id == chapter_id)
            .order_by(Lecture.order_number.asc())
        )
        lectures = lectures_result.scalars().all()

        return [LectureResponse.model_validate(lecture) for lecture in lectures]

    async def create_lecture(
        self,
        course_id: int,
        chapter_id: int,
        data: LectureCreate
    ) -> LectureResponse:
        """강의 영상 생성"""

        # 강의 존재 확인
        course_result = await self.db.execute(
            select(Course).where(Course.id == course_id)
        )
        if not course_result.scalar_one_or_none():
            raise CourseNotFoundError(f'ID {course_id}인 강의를 찾을 수 없습니다')

        # 챕터 존재 확인
        chapter_result = await self.db.execute(
            select(Chapter).where(
                Chapter.id == chapter_id,
                Chapter.course_id == course_id
            )
        )
        chapter = chapter_result.scalar_one_or_none()

        if not chapter:
            raise ChapterNotFoundError(f'ID {chapter_id}인 챕터를 찾을 수 없습니다')

        # 재생시간 자동 계산 (입력되지 않은 경우)
        duration_seconds = data.duration_seconds
        if duration_seconds is None:
            logger.info(f"영상 재생시간 자동 계산 시도: {data.video_url}")
            try:
                calculated_duration = await get_video_duration(
                    data.video_url,
                    data.video_type.value,
                    settings.youtube_api_key if settings.youtube_api_key else None
                )
                if calculated_duration:
                    duration_seconds = calculated_duration
                    logger.info(f"재생시간 자동 계산 성공: {duration_seconds}초")
                else:
                    logger.warning("재생시간 자동 계산 실패, 기본값 0초로 설정")
                    duration_seconds = 0
            except Exception as e:
                logger.error(f"재생시간 자동 계산 중 오류: {e}")
                duration_seconds = 0

        # 새 강의 영상 생성
        new_lecture = Lecture(
            chapter_id=chapter_id,
            title=data.title,
            description=data.description,
            video_url=data.video_url,
            video_type=data.video_type,
            duration_seconds=duration_seconds,
            order_number=data.order_number,
            material_url=data.material_url
        )

        self.db.add(new_lecture)
        await self.db.commit()
        await self.db.refresh(new_lecture)

        # 강의 전체 시간 업데이트
        await self._update_course_total_duration(course_id, duration_seconds)

        return LectureResponse.model_validate(new_lecture)

    async def update_lecture(
        self,
        course_id: int,
        chapter_id: int,
        lecture_id: int,
        data: LectureUpdate
    ) -> LectureResponse:
        """강의 영상 수정"""

        # 강의 존재 확인
        course_result = await self.db.execute(
            select(Course).where(Course.id == course_id)
        )
        if not course_result.scalar_one_or_none():
            raise CourseNotFoundError(f'ID {course_id}인 강의를 찾을 수 없습니다')

        # 챕터 존재 확인
        chapter_result = await self.db.execute(
            select(Chapter).where(
                Chapter.id == chapter_id,
                Chapter.course_id == course_id
            )
        )
        if not chapter_result.scalar_one_or_none():
            raise ChapterNotFoundError(f'ID {chapter_id}인 챕터를 찾을 수 없습니다')

        # 강의 영상 조회
        lecture_result = await self.db.execute(
            select(Lecture).where(
                Lecture.id == lecture_id,
                Lecture.chapter_id == chapter_id
            )
        )
        lecture = lecture_result.scalar_one_or_none()

        if not lecture:
            raise LectureNotFoundError(f'ID {lecture_id}인 강의 영상을 찾을 수 없습니다')

        # 재생 시간이 변경되는 경우 차이 계산
        old_duration = lecture.duration_seconds
        duration_diff = 0

        # 업데이트할 필드만 수정
        update_data = data.model_dump(exclude_unset=True)

        # video_url 또는 video_type이 변경되고 duration_seconds가 명시되지 않은 경우 자동 계산
        if ('video_url' in update_data or 'video_type' in update_data) and 'duration_seconds' not in update_data:
            video_url = update_data.get('video_url', lecture.video_url)
            video_type = update_data.get('video_type', lecture.video_type)

            # 빈 문자열이거나 공백만 있는 경우 0으로 설정
            if not video_url or not video_url.strip():
                logger.info(f"영상 URL이 비어있어 재생시간을 0으로 설정합니다.")
                update_data['duration_seconds'] = 0
            else:
                logger.info(f"영상 정보가 변경되어 재생시간 자동 계산 시도: {video_url}")
                try:
                    calculated_duration = await get_video_duration(
                        video_url,
                        video_type.value,
                        settings.youtube_api_key if settings.youtube_api_key else None
                    )
                    if calculated_duration:
                        update_data['duration_seconds'] = calculated_duration
                        logger.info(f"재생시간 자동 계산 성공: {calculated_duration}초")
                    else:
                        logger.warning("재생시간 자동 계산 실패, 기존 값 유지")
                except Exception as e:
                    logger.error(f"재생시간 자동 계산 중 오류: {e}, 기존 값 유지")

        for field, value in update_data.items():
            setattr(lecture, field, value)

        # 재생 시간 변경 여부 확인
        if 'duration_seconds' in update_data:
            duration_diff = lecture.duration_seconds - old_duration

        await self.db.commit()
        await self.db.refresh(lecture)

        # 재생 시간이 변경된 경우 강의 전체 시간 업데이트
        if duration_diff != 0:
            await self._update_course_total_duration(course_id, duration_diff)

        return LectureResponse.model_validate(lecture)

    async def delete_lecture(
        self,
        course_id: int,
        chapter_id: int,
        lecture_id: int
    ) -> None:
        """강의 영상 삭제"""

        # 강의 존재 확인
        course_result = await self.db.execute(
            select(Course).where(Course.id == course_id)
        )
        if not course_result.scalar_one_or_none():
            raise CourseNotFoundError(f'ID {course_id}인 강의를 찾을 수 없습니다')

        # 챕터 존재 확인
        chapter_result = await self.db.execute(
            select(Chapter).where(
                Chapter.id == chapter_id,
                Chapter.course_id == course_id
            )
        )
        if not chapter_result.scalar_one_or_none():
            raise ChapterNotFoundError(f'ID {chapter_id}인 챕터를 찾을 수 없습니다')

        # 강의 영상 조회
        lecture_result = await self.db.execute(
            select(Lecture).where(
                Lecture.id == lecture_id,
                Lecture.chapter_id == chapter_id
            )
        )
        lecture = lecture_result.scalar_one_or_none()

        if not lecture:
            raise LectureNotFoundError(f'ID {lecture_id}인 강의 영상을 찾을 수 없습니다')

        # 삭제될 강의 영상의 재생 시간 저장
        deleted_duration = lecture.duration_seconds

        # 강의 영상 삭제
        await self.db.delete(lecture)
        await self.db.commit()

        # 강의 전체 시간 업데이트
        await self._update_course_total_duration(course_id, -deleted_duration)

    # ==================== 내부 헬퍼 메서드 ====================

    async def _update_course_total_duration(
        self,
        course_id: int,
        duration_change: int
    ) -> None:
        """강의 전체 재생 시간 업데이트"""

        # 강의 조회
        result = await self.db.execute(
            select(Course).where(Course.id == course_id)
        )
        course = result.scalar_one_or_none()

        if course:
            # 전체 시간 재계산 (음수 방지)
            new_duration = max(0, course.total_duration + duration_change)
            course.total_duration = new_duration
            await self.db.commit()

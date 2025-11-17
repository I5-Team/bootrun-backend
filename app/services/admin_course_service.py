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
import os
import uuid
import aiofiles
from fastapi import UploadFile

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
from app.schemas.common import ImageUploadResponse, FileUploadResponse, FileListResponse, UploadedFileInfo
from app.exceptions.base import (
    CourseNotFoundError,
    ChapterNotFoundError,
    LectureNotFoundError,
    BadRequestError,
)
from app.core.logging_config import configure_logging
from app.utils.helpers import get_current_utc_datetime

logger = configure_logging()


class AdminCourseService:
    """관리자 강의 관리 서비스"""

    def __init__(self, db: AsyncSession):
        self.db = db

    # ==================== 파일 업로드 ====================

    async def upload_thumbnail(self, file: UploadFile) -> ImageUploadResponse:
        """강의 썸네일 업로드"""
        # 파일 검증
        allowed_extensions = ['jpg', 'jpeg', 'png', 'webp']
        file_extension = file.filename.split('.')[-1].lower()

        if file_extension not in allowed_extensions:
            raise BadRequestError(
                f'지원하지 않는 파일 형식입니다. 허용: {", ".join(allowed_extensions)}'
            )

        # 파일 크기 확인 (10MB)
        file_content = await file.read()
        file_size = len(file_content)
        max_size = 10 * 1024 * 1024  # 10MB

        if file_size > max_size:
            raise BadRequestError('파일 크기는 10MB를 초과할 수 없습니다')

        # 고유 파일명 생성
        new_filename = f'{uuid.uuid4()}.{file_extension}'

        # 업로드 디렉토리 생성
        upload_dir = '/app/uploads/thumbnails'
        os.makedirs(upload_dir, exist_ok=True)

        # 파일 저장 경로
        file_path = os.path.join(upload_dir, new_filename)

        # 파일을 디스크에 비동기로 저장
        async with aiofiles.open(file_path, 'wb') as f:
            await f.write(file_content)

        image_url = f'/uploads/thumbnails/{new_filename}'

        logger.info(f'썸네일 업로드 완료: {file_path}')

        return ImageUploadResponse(
            image_url=image_url,
            file_size=file_size,
            uploaded_at=get_current_utc_datetime()
        )

    async def upload_instructor_image(self, file: UploadFile) -> ImageUploadResponse:
        """강사 이미지 업로드"""
        # 파일 검증
        allowed_extensions = ['jpg', 'jpeg', 'png', 'webp']
        file_extension = file.filename.split('.')[-1].lower()

        if file_extension not in allowed_extensions:
            raise BadRequestError(
                f'지원하지 않는 파일 형식입니다. 허용: {", ".join(allowed_extensions)}'
            )

        # 파일 크기 확인 (10MB)
        file_content = await file.read()
        file_size = len(file_content)
        max_size = 10 * 1024 * 1024  # 10MB

        if file_size > max_size:
            raise BadRequestError('파일 크기는 10MB를 초과할 수 없습니다')

        # 고유 파일명 생성
        new_filename = f'{uuid.uuid4()}.{file_extension}'

        # 업로드 디렉토리 생성
        upload_dir = '/app/uploads/instructors'
        os.makedirs(upload_dir, exist_ok=True)

        # 파일 저장 경로
        file_path = os.path.join(upload_dir, new_filename)

        # 파일을 디스크에 비동기로 저장
        async with aiofiles.open(file_path, 'wb') as f:
            await f.write(file_content)

        image_url = f'/uploads/instructors/{new_filename}'

        logger.info(f'강사 이미지 업로드 완료: {file_path}')

        return ImageUploadResponse(
            image_url=image_url,
            file_size=file_size,
            uploaded_at=get_current_utc_datetime()
        )

    async def upload_material(self, file: UploadFile) -> FileUploadResponse:
        """강의 자료 업로드"""
        # 파일 검증 (더 넓은 범위)
        allowed_extensions = ['pdf', 'zip', 'docx', 'pptx', 'txt', 'xlsx', 'doc', 'ppt', 'xls']
        file_extension = file.filename.split('.')[-1].lower()

        if file_extension not in allowed_extensions:
            raise BadRequestError(
                f'지원하지 않는 파일 형식입니다. 허용: {", ".join(allowed_extensions)}'
            )

        # 파일 크기 확인 (50MB)
        file_content = await file.read()
        file_size = len(file_content)
        max_size = 50 * 1024 * 1024  # 50MB

        if file_size > max_size:
            raise BadRequestError('파일 크기는 50MB를 초과할 수 없습니다')

        # 고유 파일명 생성
        new_filename = f'{uuid.uuid4()}.{file_extension}'

        # 업로드 디렉토리 생성
        upload_dir = '/app/uploads/materials'
        os.makedirs(upload_dir, exist_ok=True)

        # 파일 저장 경로
        file_path = os.path.join(upload_dir, new_filename)

        # 파일을 디스크에 비동기로 저장
        async with aiofiles.open(file_path, 'wb') as f:
            await f.write(file_content)

        file_url = f'/uploads/materials/{new_filename}'

        logger.info(f'강의 자료 업로드 완료: {file_path}')

        return FileUploadResponse(
            file_url=file_url,
            file_name=file.filename,
            file_size=file_size,
            content_type=file.content_type or 'application/octet-stream',
            uploaded_at=get_current_utc_datetime()
        )

    async def delete_file(self, file_url: str) -> None:
        """업로드된 파일 삭제"""
        # URL에서 파일 경로 추출 (예: /uploads/thumbnails/abc.jpg -> uploads/thumbnails/abc.jpg)
        if not file_url.startswith('/uploads/'):
            raise BadRequestError('유효하지 않은 파일 URL입니다')

        # 앞의 '/' 제거
        file_path = file_url.lstrip('/')

        # 파일이 존재하는지 확인
        if not os.path.exists(file_path):
            raise BadRequestError('파일을 찾을 수 없습니다')

        # 파일 삭제
        try:
            os.remove(file_path)
            logger.info(f'파일 삭제 완료: {file_path}')
        except Exception as e:
            logger.error(f'파일 삭제 실패: {file_path}, 오류: {str(e)}')
            raise BadRequestError('파일 삭제 중 오류가 발생했습니다')

    async def list_uploaded_files(self, file_type: Optional[str] = None) -> FileListResponse:
        """업로드된 파일 목록 조회"""
        upload_dirs = {
            'thumbnails': 'uploads/thumbnails',
            'instructors': 'uploads/instructors',
            'materials': 'uploads/materials'
        }

        # file_type이 지정되면 해당 타입만, 아니면 전체
        if file_type:
            if file_type not in upload_dirs:
                raise BadRequestError(f'유효하지 않은 파일 타입입니다. 허용: {", ".join(upload_dirs.keys())}')
            dirs_to_scan = {file_type: upload_dirs[file_type]}
        else:
            dirs_to_scan = upload_dirs

        files = []
        total_size = 0

        for ftype, dir_path in dirs_to_scan.items():
            if not os.path.exists(dir_path):
                continue

            # 디렉토리 내 파일 목록 가져오기
            for filename in os.listdir(dir_path):
                file_path = os.path.join(dir_path, filename)

                # 파일인지 확인 (디렉토리 제외)
                if not os.path.isfile(file_path):
                    continue

                # 파일 정보 가져오기
                file_stat = os.stat(file_path)
                file_size = file_stat.st_size

                files.append(UploadedFileInfo(
                    file_name=filename,
                    file_url=f'/uploads/{ftype}/{filename}',
                    file_size=file_size,
                    file_type=ftype,
                    created_at=datetime.fromtimestamp(file_stat.st_ctime)
                ))
                total_size += file_size

        # 최신순으로 정렬
        files.sort(key=lambda x: x.created_at, reverse=True)

        return FileListResponse(
            files=files,
            total=len(files),
            total_size=total_size
        )

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

        # 새 강의 영상 생성
        new_lecture = Lecture(
            chapter_id=chapter_id,
            title=data.title,
            description=data.description,
            video_url=data.video_url,
            video_type=data.video_type,
            duration_seconds=data.duration_seconds,
            order_number=data.order_number,
            material_url=data.material_url
        )

        self.db.add(new_lecture)
        await self.db.commit()
        await self.db.refresh(new_lecture)

        # 강의 전체 시간 업데이트
        await self._update_course_total_duration(course_id, data.duration_seconds)

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

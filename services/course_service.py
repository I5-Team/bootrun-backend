from typing import List, Optional, Dict
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, or_
from sqlalchemy.orm import selectinload
import math

from models.course import Course, Chapter, Lecture, CategoryType, Difficulty, PriceType, CourseType
from models.progress import Enrollment, Progress
from schemas.course import (
    CourseListParams,
    CourseResponse,
    CourseDetailResponse,
    CoursePaginatedResponse,
    ChapterResponse,
    ChapterWithLectures,
    LectureResponse,
    CourseMetadataResponse,
    CategoryMetadata,
    CourseTypeMetadata,
    DifficultyMetadata,
    PriceTypeMetadata,
)
from exceptions.base import (
    CourseNotFoundError,
    ChapterNotFoundError,
    LectureNotFoundError,
)


class CourseService:
    """강의 관련 비즈니스 로직 (완전 비동기)"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    # ==================== 강의 목록/상세 ====================
    
    async def get_courses(
        self,
        params: CourseListParams,
        user_id: Optional[int] = None
    ) -> CoursePaginatedResponse:
        """강의 목록 조회 (필터링, 페이지네이션, 검색)"""
        
        # 서브쿼리: 강의별 수강 인원
        enrollment_subquery = (
            select(
                Enrollment.course_id,
                func.count(Enrollment.id).label('enrollment_count')
            )
            .where(Enrollment.is_active == True)
            .group_by(Enrollment.course_id)
            .subquery()
        )
        
        # 메인 쿼리
        query = (
            select(
                Course,
                func.coalesce(enrollment_subquery.c.enrollment_count, 0).label('enrollment_count')
            )
            .outerjoin(
                enrollment_subquery,
                Course.id == enrollment_subquery.c.course_id
            )
        )
        
        # 필터링
        if params.category_type:
            query = query.where(Course.category_type == params.category_type)
        
        if params.difficulty:
            query = query.where(Course.difficulty == params.difficulty)
        
        if params.price_type:
            query = query.where(Course.price_type == params.price_type)
        
        if params.is_published is not None:
            query = query.where(Course.is_published == params.is_published)
        
        if params.keyword:
            keyword_filter = or_(
                Course.title.ilike(f'%{params.keyword}%'),
                Course.description.ilike(f'%{params.keyword}%')
            )
            query = query.where(keyword_filter)
        
        # 정렬
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
        for course, enrollment_count in rows:
            course_data = CourseResponse.model_validate(course)
            course_data.enrollment_count = enrollment_count
            items.append(course_data)
        
        total_pages = math.ceil(total / params.page_size) if total > 0 else 0
        
        return CoursePaginatedResponse(
            items=items,
            total=total,
            page=params.page,
            page_size=params.page_size,
            total_pages=total_pages,
        )
    
    async def get_course_by_id(
        self,
        course_id: int,
        user_id: Optional[int] = None
    ) -> CourseDetailResponse:
        """강의 상세 조회 (N+1 문제 해결)"""
        
        # 강의 조회 (챕터와 강의 영상 eager loading)
        query = (
            select(Course)
            .options(
                selectinload(Course.chapters)
                .selectinload(Chapter.lectures)
            )
            .where(Course.id == course_id)
        )
        
        result = await self.db.execute(query)
        course = result.scalar_one_or_none()
        
        if not course:
            raise CourseNotFoundError(f'ID {course_id}인 강의를 찾을 수 없습니다')
        
        # 수강 인원 수
        enrollment_result = await self.db.execute(
            select(func.count(Enrollment.id))
            .where(
                Enrollment.course_id == course_id,
                Enrollment.is_active == True
            )
        )
        enrollment_count = enrollment_result.scalar() or 0
        
        # 사용자의 수강 여부 및 진행률
        is_enrolled = False
        my_progress = None
        progress_dict = {}
        
        if user_id:
            enrollment_result = await self.db.execute(
                select(Enrollment)
                .where(
                    Enrollment.user_id == user_id,
                    Enrollment.course_id == course_id,
                    Enrollment.is_active == True
                )
            )
            enrollment = enrollment_result.scalar_one_or_none()
            
            if enrollment:
                is_enrolled = True
                my_progress = enrollment.progress_rate
                
                # 모든 lecture_id 수집
                lecture_ids = []
                for chapter in course.chapters:
                    for lecture in chapter.lectures:
                        lecture_ids.append(lecture.id)
                
                if lecture_ids:
                    # 한 번의 쿼리로 모든 Progress 가져오기
                    progress_result = await self.db.execute(
                        select(Progress)
                        .where(
                            Progress.user_id == user_id,
                            Progress.lecture_id.in_(lecture_ids)
                        )
                    )
                    progresses = progress_result.scalars().all()
                    
                    # Dictionary로 변환
                    progress_dict = {
                        progress.lecture_id: progress
                        for progress in progresses
                    }
        
        # 챕터 및 강의 영상 데이터 변환
        chapters_data = []
        sorted_chapters = sorted(course.chapters, key=lambda c: c.order_number)
        
        for chapter in sorted_chapters:
            sorted_lectures = sorted(chapter.lectures, key=lambda l: l.order_number)
            chapter_duration = sum(lecture.duration_seconds for lecture in sorted_lectures)
            
            lectures_data = []
            for lecture in sorted_lectures:
                lecture_data = LectureResponse.model_validate(lecture)
                
                # Progress 정보 추가 (Dictionary에서 조회)
                if user_id and is_enrolled:
                    progress = progress_dict.get(lecture.id)
                    if progress:
                        lecture_data.is_completed = progress.is_completed
                        lecture_data.last_position = progress.last_position
                        lecture_data.watched_seconds = progress.watched_seconds
                
                lectures_data.append(lecture_data)
            
            chapter_data = ChapterWithLectures.model_validate(chapter)
            chapter_data.total_duration = chapter_duration
            chapter_data.lectures = lectures_data
            chapters_data.append(chapter_data)
        
        # 강의 상세 응답 생성
        course_detail = CourseDetailResponse.model_validate(course)
        course_detail.enrollment_count = enrollment_count
        course_detail.chapters = chapters_data
        course_detail.is_enrolled = is_enrolled
        course_detail.my_progress = my_progress
        
        return course_detail
    
    async def get_course_metadata(self) -> CourseMetadataResponse:
        """강의 메타데이터 조회"""
        
        categories = [
            CategoryMetadata(value=CategoryType.FRONTEND, label="프론트엔드"),
            CategoryMetadata(value=CategoryType.BACKEND, label="백엔드"),
            CategoryMetadata(value=CategoryType.DATA_ANALYSIS, label="데이터분석"),
            CategoryMetadata(value=CategoryType.AI, label="AI"),
            CategoryMetadata(value=CategoryType.DESIGN, label="디자인"),
            CategoryMetadata(value=CategoryType.OTHER, label="기타"),
        ]
        
        course_types = [
            CourseTypeMetadata(value=CourseType.VOD, label="VOD"),
            CourseTypeMetadata(value=CourseType.BOOST_COMMUNITY, label="부스트캠프"),
            CourseTypeMetadata(value=CourseType.KDC, label="KDC"),
        ]
        
        difficulties = [
            DifficultyMetadata(value=Difficulty.BEGINNER, label="초급"),
            DifficultyMetadata(value=Difficulty.INTERMEDIATE, label="중급"),
            DifficultyMetadata(value=Difficulty.ADVANCED, label="고급"),
        ]
        
        price_types = [
            PriceTypeMetadata(value=PriceType.FREE, label="무료"),
            PriceTypeMetadata(value=PriceType.PAID, label="유료"),
            PriceTypeMetadata(value=PriceType.NATIONAL_SUPPORT, label="국비지원"),
        ]
        
        return CourseMetadataResponse(
            categories=categories,
            course_types=course_types,
            difficulties=difficulties,
            price_types=price_types,
        )
    
    # ==================== 챕터 조회 ====================
    
    async def get_chapters_by_course(self, course_id: int) -> List[ChapterResponse]:
        """특정 강의의 챕터 목록 조회"""
        
        # 강의 존재 확인
        course_result = await self.db.execute(
            select(Course).where(Course.id == course_id)
        )
        course = course_result.scalar_one_or_none()
        
        if not course:
            raise CourseNotFoundError(f'ID {course_id}인 강의를 찾을 수 없습니다')
        
        # 챕터 목록 조회
        chapters_result = await self.db.execute(
            select(Chapter)
            .where(Chapter.course_id == course_id)
            .order_by(Chapter.order_number.asc())
        )
        chapters = chapters_result.scalars().all()
        
        # 챕터별 총 재생 시간 계산
        chapter_responses = []
        for chapter in chapters:
            duration_result = await self.db.execute(
                select(func.sum(Lecture.duration_seconds))
                .where(Lecture.chapter_id == chapter.id)
            )
            total_duration = duration_result.scalar() or 0
            
            chapter_data = ChapterResponse.model_validate(chapter)
            chapter_data.total_duration = total_duration
            chapter_responses.append(chapter_data)
        
        return chapter_responses
    
    async def get_chapter_by_id(
        self,
        course_id: int,
        chapter_id: int
    ) -> ChapterWithLectures:
        """특정 챕터의 상세 정보 조회"""
        
        # 강의 존재 확인
        course_result = await self.db.execute(
            select(Course).where(Course.id == course_id)
        )
        if not course_result.scalar_one_or_none():
            raise CourseNotFoundError(f'ID {course_id}인 강의를 찾을 수 없습니다')
        
        # 챕터 조회
        chapter_result = await self.db.execute(
            select(Chapter)
            .options(selectinload(Chapter.lectures))
            .where(
                Chapter.id == chapter_id,
                Chapter.course_id == course_id
            )
        )
        chapter = chapter_result.scalar_one_or_none()
        
        if not chapter:
            raise ChapterNotFoundError(f'ID {chapter_id}인 챕터를 찾을 수 없습니다')
        
        sorted_lectures = sorted(chapter.lectures, key=lambda l: l.order_number)
        total_duration = sum(lecture.duration_seconds for lecture in sorted_lectures)
        
        lectures_data = [
            LectureResponse.model_validate(lecture)
            for lecture in sorted_lectures
        ]
        
        chapter_detail = ChapterWithLectures.model_validate(chapter)
        chapter_detail.total_duration = total_duration
        chapter_detail.lectures = lectures_data
        
        return chapter_detail
    
    # ==================== 강의 영상 조회 ====================
    
    async def get_lectures_by_chapter(
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
        
        # 강의 영상 목록 조회
        lectures_result = await self.db.execute(
            select(Lecture)
            .where(Lecture.chapter_id == chapter_id)
            .order_by(Lecture.order_number.asc())
        )
        lectures = lectures_result.scalars().all()
        
        return [
            LectureResponse.model_validate(lecture)
            for lecture in lectures
        ]
    
    async def get_lecture_by_id(
        self,
        course_id: int,
        chapter_id: int,
        lecture_id: int,
        user_id: Optional[int] = None
    ) -> LectureResponse:
        """특정 강의 영상의 상세 정보 조회"""
        
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
        
        # 사용자의 시청 정보 조회
        progress = None
        if user_id:
            progress_result = await self.db.execute(
                select(Progress).where(
                    Progress.user_id == user_id,
                    Progress.lecture_id == lecture_id
                )
            )
            progress = progress_result.scalar_one_or_none()
        
        lecture_data = LectureResponse.model_validate(lecture)
        
        if progress:
            lecture_data.is_completed = progress.is_completed
            lecture_data.last_position = progress.last_position
            lecture_data.watched_seconds = progress.watched_seconds
        
        return lecture_data
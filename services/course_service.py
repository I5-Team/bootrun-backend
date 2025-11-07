"""
Course Service
강의 관련 비즈니스 로직

"""

from typing import List, Optional, Tuple
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func, or_, and_
import math

from models.course import Course, Chapter, Lecture, CategoryType, Difficulty, PriceType
from models.progress import Enrollment
from models.progress import Progress
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
    """강의 관련 비즈니스 로직을 처리하는 서비스 클래스"""
    
    def __init__(self, db: Session):
        """
        서비스 초기화
        
        Args:
            db: 데이터베이스 세션
        """
        self.db = db
    
    # ==================== 강의 목록/상세 조회 ====================
    
    def get_courses(
        self,
        params: CourseListParams,
        user_id: Optional[int] = None
    ) -> CoursePaginatedResponse:
        """
        강의 목록 조회 (필터링, 페이지네이션, 검색)
        
        Args:
            params: 필터 파라미터 (카테고리, 난이도, 가격 타입, 키워드 등)
            user_id: 현재 로그인한 사용자 ID (선택사항, 수강 여부 확인용)
        
        Returns:
            CoursePaginatedResponse: 페이지네이션된 강의 목록
        """
        # 기본 쿼리 생성
        query = self.db.query(Course)
        
        # === 필터링 ===
        
        # 1. 카테고리 필터
        if params.category_type:
            query = query.filter(Course.category_type == params.category_type)
        
        # 2. 난이도 필터
        if params.difficulty:
            query = query.filter(Course.difficulty == params.difficulty)
        
        # 3. 가격 타입 필터
        if params.price_type:
            query = query.filter(Course.price_type == params.price_type)
        
        # 4. 공개 여부 필터 (기본값: 공개된 강의만)
        if params.is_published is not None:
            query = query.filter(Course.is_published == params.is_published)
        
        # 5. 키워드 검색 (강의명, 강의 설명)
        if params.keyword:
            keyword_filter = or_(
                Course.title.ilike(f'%{params.keyword}%'),
                Course.description.ilike(f'%{params.keyword}%')
            )
            query = query.filter(keyword_filter)
        
        # === 정렬 ===
        # 최신순 정렬 (생성일 기준 내림차순)
        query = query.order_by(Course.created_at.desc())
        
        # === 전체 개수 계산 ===
        total = query.count()
        
        # === 페이지네이션 ===
        offset = (params.page - 1) * params.page_size
        courses = query.offset(offset).limit(params.page_size).all()
        
        # === 응답 데이터 생성 ===
        
        # 강의별 수강 인원 수 계산
        course_ids = [course.id for course in courses]
        enrollment_counts = {}
        
        if course_ids:
            enrollment_count_query = (
                self.db.query(
                    Enrollment.course_id,
                    func.count(Enrollment.id).label('count')
                )
                .filter(Enrollment.course_id.in_(course_ids))
                .filter(Enrollment.is_active == True)
                .group_by(Enrollment.course_id)
            )
            
            for course_id, count in enrollment_count_query:
                enrollment_counts[course_id] = count
        
        # CourseResponse 리스트 생성
        items = []
        for course in courses:
            # Pydantic의 model_validate 사용 (from_attributes=True 활용)
            course_data = CourseResponse.model_validate(course)
            # enrollment_count만 별도로 설정 (DB에 없는 계산 필드)
            course_data.enrollment_count = enrollment_counts.get(course.id, 0)
            items.append(course_data)
        
        # 전체 페이지 수 계산
        total_pages = math.ceil(total / params.page_size) if total > 0 else 0
        
        return CoursePaginatedResponse(
            items=items,
            total=total,
            page=params.page,
            page_size=params.page_size,
            total_pages=total_pages,
        )
    
    def get_course_by_id(
        self,
        course_id: int,
        user_id: Optional[int] = None
    ) -> CourseDetailResponse:
        """
        강의 상세 조회
        
        Args:
            course_id: 강의 ID
            user_id: 현재 로그인한 사용자 ID (선택사항)
        
        Returns:
            CourseDetailResponse: 강의 상세 정보 (챕터, 강의 영상 포함)
        
        Raises:
            CourseNotFoundError: 강의를 찾을 수 없는 경우
        """
        # 강의 조회 (챕터와 강의 영상을 함께 로드)
        course = (
            self.db.query(Course)
            .options(
                joinedload(Course.chapters)
                .joinedload(Chapter.lectures)
            )
            .filter(Course.id == course_id)
            .first()
        )
        
        if not course:
            raise CourseNotFoundError(f'ID {course_id}인 강의를 찾을 수 없습니다')
        
        # 수강 인원 수 계산
        enrollment_count = (
            self.db.query(func.count(Enrollment.id))
            .filter(Enrollment.course_id == course_id)
            .filter(Enrollment.is_active == True)
            .scalar()
        ) or 0
        
        # 사용자의 수강 여부 및 진행률 확인
        is_enrolled = False
        my_progress = None
        
        if user_id:
            enrollment = (
                self.db.query(Enrollment)
                .filter(Enrollment.user_id == user_id)
                .filter(Enrollment.course_id == course_id)
                .filter(Enrollment.is_active == True)
                .first()
            )
            
            if enrollment:
                is_enrolled = True
                my_progress = enrollment.progress_rate
        
        # 챕터 및 강의 영상 데이터 변환
        chapters_data = []
        
        # 챕터를 순서대로 정렬
        sorted_chapters = sorted(course.chapters, key=lambda c: c.order_number)
        
        for chapter in sorted_chapters:
            # 강의 영상을 순서대로 정렬
            sorted_lectures = sorted(chapter.lectures, key=lambda l: l.order_number)
            
            # 챕터의 총 재생 시간 계산
            chapter_duration = sum(lecture.duration_seconds for lecture in sorted_lectures)
            
            # 강의 영상 데이터 생성
            lectures_data = []
            for lecture in sorted_lectures:
                # Pydantic model_validate 사용
                lecture_data = LectureResponse.model_validate(lecture)
                
                # 사용자가 수강 중이면 시청 정보 추가
                if user_id and is_enrolled:
                    progress = (
                        self.db.query(Progress)
                        .filter(Progress.user_id == user_id)
                        .filter(Progress.lecture_id == lecture.id)
                        .first()
                    )
                    
                    if progress:
                        lecture_data.is_completed = progress.is_completed
                        lecture_data.last_position = progress.last_position
                        lecture_data.watched_seconds = progress.watched_seconds
                
                lectures_data.append(lecture_data)
            
            # 챕터 데이터 생성
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
    
    def get_course_metadata(self) -> CourseMetadataResponse:
        """
        강의 필터링에 사용할 메타데이터 조회
        
        카테고리, 강의 유형, 난이도, 가격 타입 정보를 반환합니다.
        
        Returns:
            CourseMetadataResponse: 메타데이터 정보
        """
        # 카테고리 메타데이터
        categories = [
            CategoryMetadata(
                value=CategoryType.FRONTEND,
                label="프론트엔드",
                description="HTML, CSS, JavaScript, React, Vue 등"
            ),
            CategoryMetadata(
                value=CategoryType.BACKEND,
                label="백엔드",
                description="Python, Java, Node.js, Spring, Django 등"
            ),
            CategoryMetadata(
                value=CategoryType.DATA_ANALYSIS,
                label="데이터분석",
                description="SQL, Python, 데이터 시각화, 통계 등"
            ),
            CategoryMetadata(
                value=CategoryType.AI,
                label="AI",
                description="머신러닝, 딥러닝, 자연어처리 등"
            ),
            CategoryMetadata(
                value=CategoryType.DESIGN,
                label="디자인",
                description="UI/UX, Figma, 그래픽 디자인 등"
            ),
            CategoryMetadata(
                value=CategoryType.OTHER,
                label="기타",
                description="기타 IT 관련 강의"
            ),
        ]
        
        # 강의 유형 메타데이터
        from models.course import CourseType
        course_types = [
            CourseTypeMetadata(
                value=CourseType.VOD,
                label="VOD 강의"
            ),
            CourseTypeMetadata(
                value=CourseType.BOOST_COMMUNITY,
                label="부스트 커뮤니티"
            ),
            CourseTypeMetadata(
                value=CourseType.KDC,
                label="KDC"
            ),
        ]
        
        # 난이도 메타데이터
        difficulties = [
            DifficultyMetadata(
                value=Difficulty.BEGINNER,
                label="초급"
            ),
            DifficultyMetadata(
                value=Difficulty.INTERMEDIATE,
                label="중급"
            ),
            DifficultyMetadata(
                value=Difficulty.ADVANCED,
                label="고급"
            ),
        ]
        
        # 가격 타입 메타데이터
        price_types = [
            PriceTypeMetadata(
                value=PriceType.FREE,
                label="무료"
            ),
            PriceTypeMetadata(
                value=PriceType.PAID,
                label="유료"
            ),
            PriceTypeMetadata(
                value=PriceType.NATIONAL_SUPPORT,
                label="국비지원"
            ),
        ]
        
        return CourseMetadataResponse(
            categories=categories,
            course_types=course_types,
            difficulties=difficulties,
            price_types=price_types,
        )
    
    # ==================== 챕터 조회 ====================
    
    def get_chapters_by_course(self, course_id: int) -> List[ChapterResponse]:
        """
        특정 강의의 챕터 목록 조회
        
        Args:
            course_id: 강의 ID
        
        Returns:
            List[ChapterResponse]: 챕터 목록
        
        Raises:
            CourseNotFoundError: 강의를 찾을 수 없는 경우
        """
        # 강의 존재 여부 확인
        course = self.db.query(Course).filter(Course.id == course_id).first()
        if not course:
            raise CourseNotFoundError(f'ID {course_id}인 강의를 찾을 수 없습니다')
        
        # 챕터 목록 조회 (순서대로 정렬)
        chapters = (
            self.db.query(Chapter)
            .filter(Chapter.course_id == course_id)
            .order_by(Chapter.order_number.asc())
            .all()
        )
        
        # 챕터별 총 재생 시간 계산
        chapter_responses = []
        for chapter in chapters:
            # 해당 챕터의 모든 강의 영상의 재생 시간 합계
            total_duration = (
                self.db.query(func.sum(Lecture.duration_seconds))
                .filter(Lecture.chapter_id == chapter.id)
                .scalar()
            ) or 0
            
            # Pydantic model_validate 사용
            chapter_data = ChapterResponse.model_validate(chapter)
            chapter_data.total_duration = total_duration
            chapter_responses.append(chapter_data)
        
        return chapter_responses
    
    def get_chapter_by_id(
        self,
        course_id: int,
        chapter_id: int
    ) -> ChapterWithLectures:
        """
        특정 챕터의 상세 정보 조회 (강의 영상 포함)
        
        Args:
            course_id: 강의 ID
            chapter_id: 챕터 ID
        
        Returns:
            ChapterWithLectures: 챕터 상세 정보
        
        Raises:
            CourseNotFoundError: 강의를 찾을 수 없는 경우
            ChapterNotFoundError: 챕터를 찾을 수 없는 경우
        """
        # 강의 존재 여부 확인
        course = self.db.query(Course).filter(Course.id == course_id).first()
        if not course:
            raise CourseNotFoundError(f'ID {course_id}인 강의를 찾을 수 없습니다')
        
        # 챕터 조회 (강의 영상 포함)
        chapter = (
            self.db.query(Chapter)
            .options(joinedload(Chapter.lectures))
            .filter(Chapter.id == chapter_id)
            .filter(Chapter.course_id == course_id)
            .first()
        )
        
        if not chapter:
            raise ChapterNotFoundError(f'ID {chapter_id}인 챕터를 찾을 수 없습니다')
        
        # 강의 영상을 순서대로 정렬
        sorted_lectures = sorted(chapter.lectures, key=lambda l: l.order_number)
        
        # 챕터의 총 재생 시간 계산
        total_duration = sum(lecture.duration_seconds for lecture in sorted_lectures)
        
        # 강의 영상 데이터 생성
        lectures_data = [
            LectureResponse.model_validate(lecture)
            for lecture in sorted_lectures
        ]
        
        # 챕터 상세 응답 생성
        chapter_detail = ChapterWithLectures.model_validate(chapter)
        chapter_detail.total_duration = total_duration
        chapter_detail.lectures = lectures_data
        
        return chapter_detail
    
    # ==================== 강의 영상 조회 ====================
    
    def get_lectures_by_chapter(
        self,
        course_id: int,
        chapter_id: int
    ) -> List[LectureResponse]:
        """
        특정 챕터의 강의 영상 목록 조회
        
        Args:
            course_id: 강의 ID
            chapter_id: 챕터 ID
        
        Returns:
            List[LectureResponse]: 강의 영상 목록
        
        Raises:
            CourseNotFoundError: 강의를 찾을 수 없는 경우
            ChapterNotFoundError: 챕터를 찾을 수 없는 경우
        """
        # 강의 존재 여부 확인
        course = self.db.query(Course).filter(Course.id == course_id).first()
        if not course:
            raise CourseNotFoundError(f'ID {course_id}인 강의를 찾을 수 없습니다')
        
        # 챕터 존재 여부 확인
        chapter = (
            self.db.query(Chapter)
            .filter(Chapter.id == chapter_id)
            .filter(Chapter.course_id == course_id)
            .first()
        )
        if not chapter:
            raise ChapterNotFoundError(f'ID {chapter_id}인 챕터를 찾을 수 없습니다')
        
        # 강의 영상 목록 조회 (순서대로 정렬)
        lectures = (
            self.db.query(Lecture)
            .filter(Lecture.chapter_id == chapter_id)
            .order_by(Lecture.order_number.asc())
            .all()
        )
        
        # LectureResponse 리스트 생성
        return [
            LectureResponse.model_validate(lecture)
            for lecture in lectures
        ]
    
    def get_lecture_by_id(
        self,
        course_id: int,
        chapter_id: int,
        lecture_id: int,
        user_id: Optional[int] = None
    ) -> LectureResponse:
        """
        특정 강의 영상의 상세 정보 조회
        
        Args:
            course_id: 강의 ID
            chapter_id: 챕터 ID
            lecture_id: 강의 영상 ID
            user_id: 현재 로그인한 사용자 ID (선택사항, 시청 정보 조회용)
        
        Returns:
            LectureResponse: 강의 영상 상세 정보
        
        Raises:
            CourseNotFoundError: 강의를 찾을 수 없는 경우
            ChapterNotFoundError: 챕터를 찾을 수 없는 경우
            LectureNotFoundError: 강의 영상을 찾을 수 없는 경우
        """
        # 강의 존재 여부 확인
        course = self.db.query(Course).filter(Course.id == course_id).first()
        if not course:
            raise CourseNotFoundError(f'ID {course_id}인 강의를 찾을 수 없습니다')
        
        # 챕터 존재 여부 확인
        chapter = (
            self.db.query(Chapter)
            .filter(Chapter.id == chapter_id)
            .filter(Chapter.course_id == course_id)
            .first()
        )
        if not chapter:
            raise ChapterNotFoundError(f'ID {chapter_id}인 챕터를 찾을 수 없습니다')
        
        # 강의 영상 조회
        lecture = (
            self.db.query(Lecture)
            .filter(Lecture.id == lecture_id)
            .filter(Lecture.chapter_id == chapter_id)
            .first()
        )
        
        if not lecture:
            raise LectureNotFoundError(f'ID {lecture_id}인 강의 영상을 찾을 수 없습니다')
        
        # 강의 영상 응답 데이터 생성
        lecture_data = LectureResponse.model_validate(lecture)
        
        # 사용자의 시청 정보 조회
        if user_id:
            progress = (
                self.db.query(Progress)
                .filter(Progress.user_id == user_id)
                .filter(Progress.lecture_id == lecture_id)
                .first()
            )
            
            if progress:
                lecture_data.is_completed = progress.is_completed
                lecture_data.last_position = progress.last_position
                lecture_data.watched_seconds = progress.watched_seconds
        
        return lecture_data
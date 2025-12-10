"""
테스트 설정 및 Fixture
"""
import pytest
import asyncio
from typing import AsyncGenerator, Generator
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.pool import StaticPool

from app.models.base import Base
from app.models.course import Course, Chapter, Lecture, CategoryType, CourseType, Difficulty, PriceType, VideoType
from app.models.user import User, UserRole
from app.models.progress import Enrollment, Progress
from app.utils.helpers import get_current_utc_datetime


# 테스트용 인메모리 데이터베이스
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"


@pytest.fixture(scope="session")
def event_loop() -> Generator:
    """세션 스코프 이벤트 루프"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="function")
async def async_db() -> AsyncGenerator[AsyncSession, None]:
    """테스트용 비동기 데이터베이스 세션"""

    # 엔진 생성
    engine = create_async_engine(
        TEST_DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
        echo=False
    )

    # 테이블 생성
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # 세션 팩토리
    async_session_factory = async_sessionmaker(
        engine,
        class_=AsyncSession,
        expire_on_commit=False
    )

    # 세션 생성
    async with async_session_factory() as session:
        yield session

    # 테이블 삭제
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

    await engine.dispose()


@pytest.fixture
async def test_user(async_db: AsyncSession) -> User:
    """테스트용 사용자 생성"""
    user = User(
        email="test@example.com",
        password_hash="hashed_password",
        nickname="테스트사용자",
        role=UserRole.STUDENT,
        is_active=True,
        created_at=get_current_utc_datetime(),
        updated_at=get_current_utc_datetime()
    )
    async_db.add(user)
    await async_db.commit()
    await async_db.refresh(user)
    return user


@pytest.fixture
async def test_course(async_db: AsyncSession) -> Course:
    """테스트용 강의 생성 (10분 영상 2개, 총 20분)"""

    # 강의 생성
    course = Course(
        category_type=CategoryType.BACKEND,
        course_type=CourseType.VOD,
        title="테스트 강의",
        description="진행률 계산 테스트용 강의",
        thumbnail_url="https://example.com/thumbnail.jpg",
        instructor_name="테스트 강사",
        instructor_bio="테스트 강사 소개",
        instructor_image="https://example.com/instructor.jpg",
        price_type=PriceType.FREE,
        price=0,
        difficulty=Difficulty.BEGINNER,
        total_duration=1200,  # 20분 (600초 * 2)
        created_at=get_current_utc_datetime(),
        updated_at=get_current_utc_datetime()
    )
    async_db.add(course)
    await async_db.flush()

    # 챕터 생성
    chapter = Chapter(
        course_id=course.id,
        title="테스트 챕터",
        description="테스트 챕터 설명",
        order_number=1,
        created_at=get_current_utc_datetime(),
        updated_at=get_current_utc_datetime()
    )
    async_db.add(chapter)
    await async_db.flush()

    # 강의 영상 1 (10분 = 600초)
    lecture1 = Lecture(
        chapter_id=chapter.id,
        title="강의 영상 1",
        description="첫 번째 영상",
        video_url="https://example.com/video1.mp4",
        video_type=VideoType.VOD,
        duration_seconds=600,  # 10분
        order_number=1,
        created_at=get_current_utc_datetime(),
        updated_at=get_current_utc_datetime()
    )
    async_db.add(lecture1)

    # 강의 영상 2 (10분 = 600초)
    lecture2 = Lecture(
        chapter_id=chapter.id,
        title="강의 영상 2",
        description="두 번째 영상",
        video_url="https://example.com/video2.mp4",
        video_type=VideoType.VOD,
        duration_seconds=600,  # 10분
        order_number=2,
        created_at=get_current_utc_datetime(),
        updated_at=get_current_utc_datetime()
    )
    async_db.add(lecture2)

    await async_db.commit()
    await async_db.refresh(course)
    return course


@pytest.fixture
async def test_enrollment(async_db: AsyncSession, test_user: User, test_course: Course) -> Enrollment:
    """테스트용 수강 등록"""
    from datetime import timedelta

    now = get_current_utc_datetime()
    enrollment = Enrollment(
        user_id=test_user.id,
        course_id=test_course.id,
        enrolled_at=now,
        expires_at=now + timedelta(days=365),
        is_active=True,
        progress_rate=0.0,
        created_at=now,
        updated_at=now
    )
    async_db.add(enrollment)
    await async_db.commit()
    await async_db.refresh(enrollment)
    return enrollment

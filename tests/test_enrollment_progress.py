"""
진행률 계산 로직 테스트

사용자 시나리오:
- 강의: 10분 영상 2개 (총 20분)
- 1번 영상 5분 시청 → 진행률 25% (5분 / 20분)
- 1번 영상 10분 완료 → 진행률 50% (10분 / 20분)
- 2번 영상 5분 시청 → 진행률 75% (15분 / 20분)
- 2번 영상 10분 완료 → 진행률 100% (20분 / 20분)
"""
import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.user import User
from app.models.course import Course, Lecture, Chapter
from app.models.progress import Enrollment, Progress
from app.services.enrollment_service import EnrollmentService
from app.schemas.enrollment import ProgressCreate, ProgressUpdate


@pytest.mark.asyncio
class TestProgressCalculation:
    """진행률 계산 테스트"""

    async def test_시간_기반_진행률_계산(
        self,
        async_db: AsyncSession,
        test_user: User,
        test_course: Course,
        test_enrollment: Enrollment
    ):
        """
        시간 기반 진행률이 제대로 계산되는지 테스트

        핵심: 영상을 완료하지 않아도, 시청한 만큼 진행률에 반영되어야 함
        """
        service = EnrollmentService(async_db)

        # 강의 영상 조회
        result = await async_db.execute(
            select(Lecture)
            .join(Chapter, Lecture.chapter_id == Chapter.id)
            .where(Chapter.course_id == test_course.id)
            .order_by(Lecture.order_number)
        )
        lectures = result.scalars().all()
        lecture1, lecture2 = lectures[0], lectures[1]

        # ==================== 시나리오 1 ====================
        # 1번 영상 5분 시청 (300초 / 1200초 = 25%)
        await service.create_progress(
            user_id=test_user.id,
            data=ProgressCreate(
                lecture_id=lecture1.id,
                watched_seconds=300,
                last_position=300,
                is_completed=False
            )
        )

        # Enrollment 새로고침
        await async_db.refresh(test_enrollment)

        # 진행률 검증: 25% 이어야 함
        assert test_enrollment.progress_rate == pytest.approx(25.0, rel=1e-2), \
            f"[FAIL] 1번 영상 5분 시청 시 진행률이 25%가 아닙니다: {test_enrollment.progress_rate}%"

        print(f"[PASS] 시나리오 1 통과: 1번 영상 5분 시청 -> 진행률 {test_enrollment.progress_rate}%")

        # ==================== 시나리오 2 ====================
        # 1번 영상 10분 완료 (600초 / 1200초 = 50%)
        await service.update_progress(
            user_id=test_user.id,
            lecture_id=lecture1.id,
            data=ProgressUpdate(
                watched_seconds=600,
                last_position=600,
                is_completed=False
            )
        )

        await async_db.refresh(test_enrollment)

        # 진행률 검증: 50% 이어야 함
        assert test_enrollment.progress_rate == pytest.approx(50.0, rel=1e-2), \
            f"[FAIL] 1번 영상 완료 시 진행률이 50%가 아닙니다: {test_enrollment.progress_rate}%"

        print(f"[PASS] 시나리오 2 통과: 1번 영상 10분 완료 -> 진행률 {test_enrollment.progress_rate}%")

        # ==================== 시나리오 3 ====================
        # 2번 영상 5분 시청 (900초 / 1200초 = 75%)
        await service.create_progress(
            user_id=test_user.id,
            data=ProgressCreate(
                lecture_id=lecture2.id,
                watched_seconds=300,
                last_position=300,
                is_completed=False
            )
        )

        await async_db.refresh(test_enrollment)

        # 진행률 검증: 75% 이어야 함
        assert test_enrollment.progress_rate == pytest.approx(75.0, rel=1e-2), \
            f"[FAIL] 2번 영상 5분 시청 시 진행률이 75%가 아닙니다: {test_enrollment.progress_rate}%"

        print(f"[PASS] 시나리오 3 통과: 2번 영상 5분 시청 -> 진행률 {test_enrollment.progress_rate}%")

        # ==================== 시나리오 4 ====================
        # 2번 영상 10분 완료 (1200초 / 1200초 = 100%)
        await service.update_progress(
            user_id=test_user.id,
            lecture_id=lecture2.id,
            data=ProgressUpdate(
                watched_seconds=600,
                last_position=600,
                is_completed=False
            )
        )

        await async_db.refresh(test_enrollment)

        # 진행률 검증: 100% 이어야 함
        assert test_enrollment.progress_rate == pytest.approx(100.0, rel=1e-2), \
            f"[FAIL] 2번 영상 완료 시 진행률이 100%가 아닙니다: {test_enrollment.progress_rate}%"

        print(f"[PASS] 시나리오 4 통과: 2번 영상 10분 완료 -> 진행률 {test_enrollment.progress_rate}%")

        print("\n[SUCCESS] 모든 시나리오 통과! 백엔드는 시간 기반으로 진행률을 정확히 계산하고 있습니다.")

    async def test_되감기_시_진행률_유지(
        self,
        async_db: AsyncSession,
        test_user: User,
        test_course: Course,
        test_enrollment: Enrollment
    ):
        """
        사용자가 영상을 되감기해도 진행률이 감소하지 않아야 함
        """
        service = EnrollmentService(async_db)

        # 강의 영상 조회
        result = await async_db.execute(
            select(Lecture)
            .join(Chapter, Lecture.chapter_id == Chapter.id)
            .where(Chapter.course_id == test_course.id)
            .order_by(Lecture.order_number)
            .limit(1)
        )
        lecture1 = result.scalar_one()

        # 1번 영상 8분 시청 (480초)
        await service.create_progress(
            user_id=test_user.id,
            data=ProgressCreate(
                lecture_id=lecture1.id,
                watched_seconds=480,
                last_position=480,
                is_completed=False
            )
        )

        await async_db.refresh(test_enrollment)
        progress_before = test_enrollment.progress_rate

        # 사용자가 되감기 (2분으로 이동, 120초)
        await service.update_progress(
            user_id=test_user.id,
            lecture_id=lecture1.id,
            data=ProgressUpdate(
                watched_seconds=600,  # 누적 시청 시간은 증가
                last_position=120,    # 하지만 현재 위치는 2분
                is_completed=False
            )
        )

        await async_db.refresh(test_enrollment)
        progress_after = test_enrollment.progress_rate

        # 진행률이 감소하지 않아야 함
        assert progress_after >= progress_before, \
            f"[FAIL] 되감기 시 진행률이 감소했습니다: {progress_before}% -> {progress_after}%"

        print(f"[PASS] 되감기 테스트 통과: 진행률이 유지됩니다 ({progress_before}% -> {progress_after}%)")

    async def test_영상_완료_판정_95퍼센트(
        self,
        async_db: AsyncSession,
        test_user: User,
        test_course: Course,
        test_enrollment: Enrollment
    ):
        """
        영상 시청률이 95% 이상이면 자동으로 완료 처리되어야 함
        """
        service = EnrollmentService(async_db)

        # 강의 영상 조회
        result = await async_db.execute(
            select(Lecture)
            .join(Chapter, Lecture.chapter_id == Chapter.id)
            .where(Chapter.course_id == test_course.id)
            .order_by(Lecture.order_number)
            .limit(1)
        )
        lecture1 = result.scalar_one()

        # 1번 영상 95% 시청 (570초 / 600초)
        progress_response = await service.create_progress(
            user_id=test_user.id,
            data=ProgressCreate(
                lecture_id=lecture1.id,
                watched_seconds=570,
                last_position=570,
                is_completed=False
            )
        )

        # 자동으로 완료 처리되어야 함
        assert progress_response.is_completed is True, \
            f"[FAIL] 95% 이상 시청했지만 완료 처리되지 않았습니다"

        print(f"[PASS] 자동 완료 테스트 통과: 95% 이상 시청 시 자동 완료됩니다")

    async def test_get_course_progress_API(
        self,
        async_db: AsyncSession,
        test_user: User,
        test_course: Course,
        test_enrollment: Enrollment
    ):
        """
        GET /enrollments/progress/course/{course_id} API가 올바른 진행률을 반환하는지 테스트
        """
        service = EnrollmentService(async_db)

        # 강의 영상 조회
        result = await async_db.execute(
            select(Lecture)
            .join(Chapter, Lecture.chapter_id == Chapter.id)
            .where(Chapter.course_id == test_course.id)
            .order_by(Lecture.order_number)
        )
        lectures = result.scalars().all()

        # 1번 영상 5분 시청
        await service.create_progress(
            user_id=test_user.id,
            data=ProgressCreate(
                lecture_id=lectures[0].id,
                watched_seconds=300,
                last_position=300,
                is_completed=False
            )
        )

        # 강의 진행 상황 조회
        course_progress = await service.get_course_progress(
            user_id=test_user.id,
            course_id=test_course.id
        )

        # 진행률 검증
        assert course_progress.progress_rate == pytest.approx(25.0, rel=1e-2), \
            f"[FAIL] API 응답의 진행률이 25%가 아닙니다: {course_progress.progress_rate}%"

        assert course_progress.watched_duration == 300, \
            f"[FAIL] API 응답의 시청 시간이 300초가 아닙니다: {course_progress.watched_duration}초"

        print(f"[PASS] API 테스트 통과: get_course_progress가 올바른 진행률을 반환합니다")
        print(f"   - 진행률: {course_progress.progress_rate}%")
        print(f"   - 시청 시간: {course_progress.watched_duration}초 / {course_progress.total_duration}초")

    async def test_진행률_100퍼센트_초과_방지(
        self,
        async_db: AsyncSession,
        test_user: User,
        test_course: Course,
        test_enrollment: Enrollment
    ):
        """
        진행률이 100%를 초과하지 않는지 테스트
        - 모든 영상을 완료해도 100% 이하
        - 영상 길이보다 긴 시청 시간을 보내도 100% 이하
        """
        service = EnrollmentService(async_db)

        # 강의 영상 조회
        result = await async_db.execute(
            select(Lecture)
            .join(Chapter, Lecture.chapter_id == Chapter.id)
            .where(Chapter.course_id == test_course.id)
            .order_by(Lecture.order_number)
        )
        lectures = result.scalars().all()

        # 1번 영상 완료
        await service.create_progress(
            user_id=test_user.id,
            data=ProgressCreate(
                lecture_id=lectures[0].id,
                watched_seconds=600,
                last_position=600,
                is_completed=True
            )
        )

        # 2번 영상 완료
        await service.create_progress(
            user_id=test_user.id,
            data=ProgressCreate(
                lecture_id=lectures[1].id,
                watched_seconds=600,
                last_position=600,
                is_completed=True
            )
        )

        await async_db.refresh(test_enrollment)

        # 진행률이 100% 이하여야 함
        assert test_enrollment.progress_rate <= 100.0, \
            f"[FAIL] 진행률이 100%를 초과했습니다: {test_enrollment.progress_rate}%"

        print(f"[PASS] 진행률 100% 초과 방지 테스트 통과: {test_enrollment.progress_rate}%")

    async def test_last_position_영상_길이_초과_방지(
        self,
        async_db: AsyncSession,
        test_user: User,
        test_course: Course,
        test_enrollment: Enrollment
    ):
        """
        last_position이 영상 길이를 초과하는 경우 제한되는지 테스트
        - 영상 길이: 600초 (10분)
        - 전송: last_position=1000초
        - 기대: last_position이 600초로 제한됨
        """
        service = EnrollmentService(async_db)

        # 강의 영상 조회
        result = await async_db.execute(
            select(Lecture)
            .join(Chapter, Lecture.chapter_id == Chapter.id)
            .where(Chapter.course_id == test_course.id)
            .order_by(Lecture.order_number)
            .limit(1)
        )
        lecture1 = result.scalar_one()

        # 영상 길이(600초)보다 긴 last_position(1000초) 전송
        await service.create_progress(
            user_id=test_user.id,
            data=ProgressCreate(
                lecture_id=lecture1.id,
                watched_seconds=1000,  # 반복 재생으로 1000초
                last_position=1000,    # 영상 길이 초과!
                is_completed=False
            )
        )

        # Progress 조회
        progress_result = await async_db.execute(
            select(Progress).where(
                Progress.user_id == test_user.id,
                Progress.lecture_id == lecture1.id
            )
        )
        progress = progress_result.scalar_one()

        # last_position이 영상 길이(600초) 이하로 제한되어야 함
        assert progress.last_position <= lecture1.duration_seconds, \
            f"[FAIL] last_position이 영상 길이를 초과했습니다: {progress.last_position}초 > {lecture1.duration_seconds}초"

        # unique_watched_seconds도 영상 길이 이하여야 함
        assert progress.unique_watched_seconds <= lecture1.duration_seconds, \
            f"[FAIL] unique_watched_seconds가 영상 길이를 초과했습니다: {progress.unique_watched_seconds}초 > {lecture1.duration_seconds}초"

        # 진행률 확인
        await async_db.refresh(test_enrollment)

        # 진행률이 100%를 초과하지 않아야 함
        assert test_enrollment.progress_rate <= 100.0, \
            f"[FAIL] 진행률이 100%를 초과했습니다: {test_enrollment.progress_rate}%"

        print(f"[PASS] last_position 제한 테스트 통과:")
        print(f"   - 전송한 last_position: 1000초")
        print(f"   - 실제 저장된 last_position: {progress.last_position}초 (영상 길이: {lecture1.duration_seconds}초)")
        print(f"   - unique_watched_seconds: {progress.unique_watched_seconds}초")
        print(f"   - 진행률: {test_enrollment.progress_rate}%")

    async def test_watched_seconds_반복_재생_허용(
        self,
        async_db: AsyncSession,
        test_user: User,
        test_course: Course,
        test_enrollment: Enrollment
    ):
        """
        watched_seconds는 영상 길이를 초과할 수 있는지 테스트 (반복 재생)
        - 영상 길이: 600초
        - watched_seconds: 1500초 (2.5번 반복 재생)
        - 진행률: unique_watched_seconds 기준으로 계산되므로 100% 이하
        """
        service = EnrollmentService(async_db)

        # 강의 영상 조회
        result = await async_db.execute(
            select(Lecture)
            .join(Chapter, Lecture.chapter_id == Chapter.id)
            .where(Chapter.course_id == test_course.id)
            .order_by(Lecture.order_number)
            .limit(1)
        )
        lecture1 = result.scalar_one()

        # 영상을 여러 번 반복 재생 (watched_seconds는 누적)
        await service.create_progress(
            user_id=test_user.id,
            data=ProgressCreate(
                lecture_id=lecture1.id,
                watched_seconds=1500,  # 2.5번 반복 재생
                last_position=300,      # 현재 위치는 5분
                is_completed=False
            )
        )

        # Progress 조회
        progress_result = await async_db.execute(
            select(Progress).where(
                Progress.user_id == test_user.id,
                Progress.lecture_id == lecture1.id
            )
        )
        progress = progress_result.scalar_one()

        # watched_seconds는 영상 길이를 초과할 수 있음 (반복 재생)
        assert progress.watched_seconds == 1500, \
            f"[FAIL] watched_seconds가 제대로 저장되지 않았습니다: {progress.watched_seconds}초"

        # 하지만 unique_watched_seconds는 영상 길이 이하여야 함
        assert progress.unique_watched_seconds <= lecture1.duration_seconds, \
            f"[FAIL] unique_watched_seconds가 영상 길이를 초과했습니다: {progress.unique_watched_seconds}초"

        # 진행률 확인
        await async_db.refresh(test_enrollment)

        # 진행률은 unique_watched_seconds 기준이므로 100% 이하
        assert test_enrollment.progress_rate <= 100.0, \
            f"[FAIL] 진행률이 100%를 초과했습니다: {test_enrollment.progress_rate}%"

        print(f"[PASS] watched_seconds 반복 재생 테스트 통과:")
        print(f"   - watched_seconds: {progress.watched_seconds}초 (반복 재생 허용)")
        print(f"   - unique_watched_seconds: {progress.unique_watched_seconds}초 (진행률 계산용)")
        print(f"   - last_position: {progress.last_position}초")
        print(f"   - 진행률: {test_enrollment.progress_rate}% (100% 이하 유지)")

    async def test_모든_영상_초과_시청_시_100퍼센트_유지(
        self,
        async_db: AsyncSession,
        test_user: User,
        test_course: Course,
        test_enrollment: Enrollment
    ):
        """
        모든 영상을 초과 시청해도 진행률이 100%를 유지하는지 테스트
        """
        service = EnrollmentService(async_db)

        # 강의 영상 조회
        result = await async_db.execute(
            select(Lecture)
            .join(Chapter, Lecture.chapter_id == Chapter.id)
            .where(Chapter.course_id == test_course.id)
            .order_by(Lecture.order_number)
        )
        lectures = result.scalars().all()

        # 1번 영상 - 영상 길이보다 긴 시청
        await service.create_progress(
            user_id=test_user.id,
            data=ProgressCreate(
                lecture_id=lectures[0].id,
                watched_seconds=800,   # 영상 길이 600초보다 200초 더 시청
                last_position=650,     # 영상 길이 초과
                is_completed=True
            )
        )

        # 2번 영상 - 영상 길이보다 긴 시청
        await service.create_progress(
            user_id=test_user.id,
            data=ProgressCreate(
                lecture_id=lectures[1].id,
                watched_seconds=900,   # 영상 길이 600초보다 300초 더 시청
                last_position=700,     # 영상 길이 초과
                is_completed=True
            )
        )

        await async_db.refresh(test_enrollment)

        # 진행률이 정확히 100%여야 함 (초과하지 않음)
        assert test_enrollment.progress_rate <= 100.0, \
            f"[FAIL] 진행률이 100%를 초과했습니다: {test_enrollment.progress_rate}%"

        assert test_enrollment.progress_rate == pytest.approx(100.0, rel=1e-2), \
            f"[FAIL] 모든 영상 완료 시 진행률이 100%가 아닙니다: {test_enrollment.progress_rate}%"

        print(f"[PASS] 모든 영상 초과 시청 테스트 통과:")
        print(f"   - 1번 영상: watched_seconds=800초, last_position=650초 (길이: 600초)")
        print(f"   - 2번 영상: watched_seconds=900초, last_position=700초 (길이: 600초)")
        print(f"   - 최종 진행률: {test_enrollment.progress_rate}% (100% 유지)")

    async def test_영상_완료_후_last_position_유지(
        self,
        async_db: AsyncSession,
        test_user: User,
        test_course: Course,
        test_enrollment: Enrollment
    ):
        """
        영상 완료 후 last_position이 마지막 위치에 있는 것은 백엔드 문제가 아님을 증명

        백엔드 역할:
        - 프론트가 보낸 last_position을 그대로 저장
        - 조회 시 저장된 값을 그대로 반환

        프론트엔드 역할:
        - 영상 완료 후 다시 재생 시, last_position=0으로 초기화하여 전송
        - 또는 영상 재생 시 is_completed=true이면 처음부터 재생
        """
        service = EnrollmentService(async_db)

        # 강의 영상 조회
        result = await async_db.execute(
            select(Lecture)
            .join(Chapter, Lecture.chapter_id == Chapter.id)
            .where(Chapter.course_id == test_course.id)
            .order_by(Lecture.order_number)
            .limit(1)
        )
        lecture1 = result.scalar_one()

        print(f"\n[시나리오] 영상 완료 후 재생 위치 테스트")
        print(f"영상 길이: {lecture1.duration_seconds}초")

        # ==================== 1단계: 영상 완료 ====================
        print(f"\n[1단계] 영상을 끝까지 시청")
        await service.create_progress(
            user_id=test_user.id,
            data=ProgressCreate(
                lecture_id=lecture1.id,
                watched_seconds=600,
                last_position=600,  # 마지막 위치
                is_completed=True
            )
        )

        # Progress 조회
        progress_result = await async_db.execute(
            select(Progress).where(
                Progress.user_id == test_user.id,
                Progress.lecture_id == lecture1.id
            )
        )
        progress = progress_result.scalar_one()

        # 백엔드는 보낸 값 그대로 저장
        assert progress.last_position == 600, \
            f"[FAIL] 백엔드가 last_position을 잘못 저장: {progress.last_position}초"

        assert progress.is_completed is True, \
            f"[FAIL] 영상이 완료 처리되지 않음"

        print(f"   - last_position: {progress.last_position}초 (백엔드가 받은 값 그대로 저장)")
        print(f"   - is_completed: {progress.is_completed}")

        # ==================== 2단계: 다시 재생 (프론트가 last_position 그대로 사용) ====================
        print(f"\n[2단계] 다시 재생 - 프론트가 백엔드 값을 그대로 사용하는 경우")

        # 프론트엔드가 GET API로 받은 last_position을 그대로 사용
        # -> 영상이 마지막 위치에서 시작됨 (프론트 문제)

        # 백엔드 API 응답 시뮬레이션
        lecture_progress = await service.get_lecture_progress(
            user_id=test_user.id,
            lecture_id=lecture1.id
        )

        print(f"   - 백엔드 API 응답: last_position={lecture_progress.last_position}초")
        print(f"   - 프론트가 이 값으로 영상을 재생하면 마지막 위치에서 시작됨 (프론트 로직 문제)")

        # ==================== 3단계: 프론트가 처음부터 재생 (올바른 방법) ====================
        print(f"\n[3단계] 올바른 방법 - 프론트가 last_position=0으로 초기화")

        # 프론트엔드가 "처음부터 재생" 버튼을 누르거나
        # is_completed=true일 때 자동으로 last_position=0으로 설정
        await service.update_progress(
            user_id=test_user.id,
            lecture_id=lecture1.id,
            data=ProgressUpdate(
                watched_seconds=650,  # 누적 시청 시간은 증가
                last_position=0,      # 처음부터 재생!
                is_completed=True     # 여전히 완료 상태
            )
        )

        # Progress 재조회
        progress_result = await async_db.execute(
            select(Progress).where(
                Progress.user_id == test_user.id,
                Progress.lecture_id == lecture1.id
            )
        )
        progress = progress_result.scalar_one()

        # 백엔드는 프론트가 보낸 0을 그대로 저장
        assert progress.last_position == 0, \
            f"[FAIL] 백엔드가 last_position=0을 저장하지 않음: {progress.last_position}초"

        print(f"   - 프론트가 last_position=0 전송")
        print(f"   - 백엔드 저장: last_position={progress.last_position}초")
        print(f"   - 영상이 처음부터 재생됨!")

        # ==================== 4단계: 영상 중간 재생 ====================
        print(f"\n[4단계] 영상 중간부터 재생")

        await service.update_progress(
            user_id=test_user.id,
            lecture_id=lecture1.id,
            data=ProgressUpdate(
                watched_seconds=700,
                last_position=150,    # 2분 30초 위치
                is_completed=True
            )
        )

        progress_result = await async_db.execute(
            select(Progress).where(
                Progress.user_id == test_user.id,
                Progress.lecture_id == lecture1.id
            )
        )
        progress = progress_result.scalar_one()

        assert progress.last_position == 150, \
            f"[FAIL] 백엔드가 중간 위치를 저장하지 않음: {progress.last_position}초"

        print(f"   - 프론트가 last_position=150초 전송")
        print(f"   - 백엔드 저장: last_position={progress.last_position}초")
        print(f"   - 영상이 2분 30초부터 재생됨!")

        print(f"\n[PASS] 영상 완료 후 재생 위치 테스트 통과!")
        print(f"\n[결론]")
        print(f"  - 백엔드는 프론트가 보낸 last_position을 그대로 저장/반환")
        print(f"  - '영상 완료 후 처음부터 재생' 로직은 프론트엔드 책임")
        print(f"  - 프론트 해결 방법:")
        print(f"    1. is_completed=true인 영상 재생 시 자동으로 last_position=0 사용")
        print(f"    2. '처음부터 보기' 버튼 제공 (last_position=0 전송)")
        print(f"    3. 영상 재생 완료 시 자동으로 last_position=0 전송")

    async def test_백엔드는_last_position을_조작하지_않음(
        self,
        async_db: AsyncSession,
        test_user: User,
        test_course: Course,
        test_enrollment: Enrollment
    ):
        """
        백엔드가 last_position을 임의로 조작하지 않는다는 것을 증명
        - 프론트가 보낸 값을 그대로 저장
        - 영상 길이 초과 시에만 제한 (안전 장치)
        """
        service = EnrollmentService(async_db)

        # 강의 영상 조회
        result = await async_db.execute(
            select(Lecture)
            .join(Chapter, Lecture.chapter_id == Chapter.id)
            .where(Chapter.course_id == test_course.id)
            .order_by(Lecture.order_number)
            .limit(1)
        )
        lecture1 = result.scalar_one()

        test_cases = [
            (0, "처음"),
            (100, "1분 40초"),
            (300, "5분"),
            (450, "7분 30초"),
            (590, "9분 50초"),
            (600, "마지막"),
        ]

        print(f"\n[테스트] 백엔드는 프론트가 보낸 last_position을 그대로 저장")

        # 첫 번째는 create로 생성
        first_position, first_desc = test_cases[0]
        await service.create_progress(
            user_id=test_user.id,
            data=ProgressCreate(
                lecture_id=lecture1.id,
                watched_seconds=first_position,
                last_position=first_position,
                is_completed=False
            )
        )

        progress_result = await async_db.execute(
            select(Progress).where(
                Progress.user_id == test_user.id,
                Progress.lecture_id == lecture1.id
            )
        )
        progress = progress_result.scalar_one()

        assert progress.last_position == first_position, \
            f"[FAIL] 백엔드가 last_position을 조작함: 전송={first_position}, 저장={progress.last_position}"

        print(f"   - last_position={first_position}초 ({first_desc}) -> 저장={progress.last_position}초 [OK]")

        # 나머지는 update로 갱신
        for position, description in test_cases[1:]:
            await service.update_progress(
                user_id=test_user.id,
                lecture_id=lecture1.id,
                data=ProgressUpdate(
                    watched_seconds=position,
                    last_position=position,
                    is_completed=False
                )
            )

            progress_result = await async_db.execute(
                select(Progress).where(
                    Progress.user_id == test_user.id,
                    Progress.lecture_id == lecture1.id
                )
            )
            progress = progress_result.scalar_one()

            assert progress.last_position == position, \
                f"[FAIL] 백엔드가 last_position을 조작함: 전송={position}, 저장={progress.last_position}"

            print(f"   - last_position={position}초 ({description}) -> 저장={progress.last_position}초 [OK]")

        print(f"\n[PASS] 백엔드는 last_position을 조작하지 않음!")
        print(f"  - 모든 테스트 케이스에서 프론트가 보낸 값 그대로 저장됨")
        print(f"  - 백엔드는 단순히 상태를 저장하는 역할만 수행")

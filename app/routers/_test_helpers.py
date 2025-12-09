"""
⚠️ 개발/테스트 전용 엔드포인트 모음
프로덕션 배포 전에 이 파일과 관련 라우터 등록을 삭제해야 합니다.
"""

from fastapi import APIRouter, Depends, status, Path
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timedelta

from app.schemas.common import SuccessResponse, MessageResponse
from app.schemas.enrollment import MyCourseDetail
from app.core.dependencies import get_current_user, get_db
from app.models.user import User
from app.models.progress import Enrollment
from app.models.course import Course
from app.exceptions.base import CourseNotFoundError, AlreadyEnrolledError
from sqlalchemy import select, and_

router = APIRouter(prefix="/test", tags=["⚠️ 테스트 전용"])


@router.post(
    "/enrollments/{course_id}",
    response_model=SuccessResponse[dict],
    status_code=status.HTTP_201_CREATED,
    summary="[테스트] 수강 등록 직접 생성",
    description="⚠️ 테스트 전용: 결제 없이 수강 등록을 직접 생성합니다. 강의 진행률 테스트 목적."
)
async def test_create_enrollment(
    course_id: int = Path(..., gt=0, description="강의 ID"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    테스트 목적으로 결제 프로세스를 건너뛰고 수강 등록을 직접 생성합니다.

    - 강의 존재 여부 확인
    - 중복 등록 확인
    - Enrollment 레코드 생성 (is_active=True, 만료일 2년 후)
    """

    # 강의 존재 확인
    course = await db.execute(
        select(Course).where(Course.id == course_id)
    )
    course = course.scalar_one_or_none()

    if not course:
        raise CourseNotFoundError()

    # 중복 등록 확인
    existing = await db.execute(
        select(Enrollment).where(
            and_(
                Enrollment.user_id == current_user.id,
                Enrollment.course_id == course_id,
                Enrollment.is_active == True
            )
        )
    )
    existing_enrollment = existing.scalar_one_or_none()

    if existing_enrollment:
        raise AlreadyEnrolledError()

    # 수강 등록 생성
    enrollment = Enrollment(
        user_id=current_user.id,
        course_id=course_id,
        is_active=True,
        expires_at=datetime.utcnow() + timedelta(days=365*2),
    )
    db.add(enrollment)
    await db.commit()

    return SuccessResponse(
        data={
            "enrollment_id": enrollment.id,
            "user_id": enrollment.user_id,
            "course_id": enrollment.course_id,
            "course_title": course.title,
            "is_active": enrollment.is_active,
            "enrolled_at": enrollment.enrolled_at,
            "expires_at": enrollment.expires_at,
            "message": "테스트용 수강 등록이 생성되었습니다. 이제 내 수강목록에서 확인할 수 있습니다."
        }
    )


@router.delete(
    "/enrollments/{course_id}",
    response_model=MessageResponse,
    summary="[테스트] 수강 등록 삭제",
    description="⚠️ 테스트 전용: 수강 등록을 삭제합니다. 테스트 데이터 정리 목적."
)
async def test_delete_enrollment(
    course_id: int = Path(..., gt=0, description="강의 ID"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    테스트용으로 생성한 수강 등록을 삭제합니다.

    - 실제 결제가 있는 경우 결제 레코드는 유지되고 enrollment만 삭제됨
    - Progress 레코드도 CASCADE로 함께 삭제됨
    """

    enrollment = await db.execute(
        select(Enrollment).where(
            and_(
                Enrollment.user_id == current_user.id,
                Enrollment.course_id == course_id
            )
        )
    )
    enrollment = enrollment.scalar_one_or_none()

    if not enrollment:
        return MessageResponse(message="삭제할 수강 등록이 없습니다.")

    await db.delete(enrollment)
    await db.commit()

    return MessageResponse(message=f"수강 등록이 삭제되었습니다. (enrollment_id: {enrollment.id})")


@router.get(
    "/info",
    response_model=dict,
    summary="[테스트] 테스트 엔드포인트 정보",
    description="이 테스트 API의 사용 가이드를 제공합니다."
)
async def test_info():
    """
    테스트 엔드포인트 사용 가이드
    """
    return {
        "warning": "⚠️ 이 엔드포인트들은 개발/테스트 전용입니다. 프로덕션 배포 전에 반드시 삭제하세요.",
        "purpose": "결제 프로세스를 거치지 않고 수강 등록을 생성하여 강의 진행률 기능을 테스트합니다.",
        "usage": {
            "1. 수강 등록 생성": "POST /api/test/enrollments/{course_id}",
            "2. 내 수강목록 확인": "GET /api/enrollments/my",
            "3. 강의 진행률 테스트": "PATCH /api/enrollments/progress/lectures/{lecture_id}",
            "4. 수강 등록 삭제": "DELETE /api/test/enrollments/{course_id}"
        },
        "example_flow": [
            "1. 강의 목록 조회하여 course_id 확인 (GET /api/courses)",
            "2. 테스트 수강 등록 생성 (POST /api/test/enrollments/1)",
            "3. 내 수강목록에 나타나는지 확인 (GET /api/enrollments/my)",
            "4. 강의 진행률 업데이트 테스트",
            "5. 테스트 완료 후 수강 등록 삭제 (DELETE /api/test/enrollments/1)"
        ],
        "cleanup": "테스트 완료 후 이 파일(app/routers/_test_helpers.py)과 app/main.py의 라우터 등록을 삭제하세요."
    }

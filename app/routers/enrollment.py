from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.common import SuccessResponse
from app.schemas.enrollment import (
    ProgressCreate, ProgressUpdate, ProgressResponse,
    CourseProgressDetail, StudentDashboard,
    MyCourseListParams,
    MyCoursePaginatedResponse,
    MyCourseDetail,
)
from app.exceptions.responses import (
    ENROLLMENT_ACCESS_RESPONSES,
    PROGRESS_UPDATE_RESPONSES,
    AUTH_RESPONSES,
    READ_RESPONSES,
)
from app.core.dependencies import get_current_user, get_db
from app.models.user import User
from app.services.enrollment_service import EnrollmentService

router = APIRouter(prefix="/enrollments", tags=["수강 등록 및 학습 진행"])


@router.get(
    "/my",
    response_model=SuccessResponse[MyCoursePaginatedResponse],
    summary="내 수강 목록 조회",
    description="현재 사용자가 수강 중인 강의 목록을 조회합니다. 상태, 학습 진행도, 유형별로 필터링할 수 있습니다.",
    responses={**AUTH_RESPONSES})

async def get_my_enrollments(
    params: MyCourseListParams = Depends(),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    service = EnrollmentService(db)
    result = await service.get_my_courses(current_user.id, params)
    return SuccessResponse(data=result)


@router.get(
    "/dashboard",
    response_model=SuccessResponse[StudentDashboard],
    summary="학습자 대시보드",
    description="학습자의 전체 학습 현황을 요약하여 보여줍니다.",
    responses={**AUTH_RESPONSES})

async def get_student_dashboard(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    service = EnrollmentService(db)
    result = await service.get_student_dashboard(current_user.id)
    return SuccessResponse(data=result)


@router.get(
    "/{course_id}",
    response_model=SuccessResponse[MyCourseDetail],
    summary="내 강의실 조회",
    description="수강 중인 강의의 상세 정보를 조회합니다. 챕터별 강의 영상 목록과 각 영상의 시청 진행 상태를 확인할 수 있습니다.",
    responses={**AUTH_RESPONSES,**READ_RESPONSES})

async def get_enrollment(
    course_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    service = EnrollmentService(db)
    result = await service.get_my_course_detail(current_user.id, course_id)
    return SuccessResponse(data=result)


@router.post(
    "/progress",
    response_model=SuccessResponse[ProgressResponse],
    status_code=status.HTTP_201_CREATED,
    summary="학습 진행 생성",
    description="강의 영상의 학습 진행을 생성하거나 업데이트합니다. 이미 진행 기록이 있으면 자동으로 업데이트됩니다.",
    responses={**PROGRESS_UPDATE_RESPONSES})

async def create_progress(
    data: ProgressCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    service = EnrollmentService(db)
    result = await service.create_progress(current_user.id, data)
    return SuccessResponse(data=result)


@router.patch(
    "/progress/lectures/{lecture_id}",
    response_model=SuccessResponse[ProgressResponse],
    summary="학습 진행 업데이트",
    description="강의 영상의 학습 진행 상태를 업데이트합니다.",
    responses={**PROGRESS_UPDATE_RESPONSES})

async def update_progress(
    lecture_id: int,
    data: ProgressUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    service = EnrollmentService(db)
    result = await service.update_progress(current_user.id, lecture_id, data)
    return SuccessResponse(data=result)


@router.get(
    "/progress/course/{course_id}",
    response_model=SuccessResponse[CourseProgressDetail],
    summary="강의별 학습 진행 조회",
    description="특정 강의의 전체 학습 진행 상황을 조회합니다.",
    responses={**ENROLLMENT_ACCESS_RESPONSES})

async def get_course_progress(
    course_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    service = EnrollmentService(db)
    result = await service.get_course_progress(current_user.id, course_id)
    return SuccessResponse(data=result)


@router.get(
    "/progress/lecture/{lecture_id}",
    response_model=SuccessResponse[ProgressResponse],
    summary="강의 영상별 진행 조회",
    description="특정 강의 영상의 학습 진행 상태를 조회합니다.",
    responses={**ENROLLMENT_ACCESS_RESPONSES})

async def get_lecture_progress(
    lecture_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    service = EnrollmentService(db)
    result = await service.get_lecture_progress(current_user.id, lecture_id)
    return SuccessResponse(data=result)
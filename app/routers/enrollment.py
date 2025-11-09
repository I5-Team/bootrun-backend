from fastapi import APIRouter, Depends, status
from app.schemas.common import MessageResponse
from app.schemas.enrollment import (
    EnrollmentCreate, EnrollmentResponse, EnrollmentDetailResponse,
    EnrollmentPaginatedResponse, MyEnrollmentListParams,
    ProgressCreate, ProgressUpdate, ProgressResponse, 
    CourseProgressDetail, StudentDashboard, LearningStats
)
from app.exceptions.responses import (
    ENROLLMENT_CREATE_RESPONSES,
    ENROLLMENT_ACCESS_RESPONSES,
    ENROLLMENT_CANCEL_RESPONSES,
    PROGRESS_UPDATE_RESPONSES,
    AUTH_RESPONSES,
    READ_RESPONSES,
    MODIFY_RESPONSES,
)
from app.core.dependencies import get_current_user
from app.models.user import User

router = APIRouter(prefix="/enrollments", tags=["수강 등록 및 학습 진행"])

@router.post(
    "",
    response_model=EnrollmentResponse,
    status_code=status.HTTP_201_CREATED,
    summary="수강 등록",
    description="강의를 수강 등록합니다. 결제가 완료된 후 자동으로 등록됩니다.",
    responses={
        201: {"description": "수강 등록 성공"},
        **ENROLLMENT_CREATE_RESPONSES
    }
)
async def create_enrollment(
    data: EnrollmentCreate,
    current_user: User = Depends(get_current_user)
):
    pass

@router.get(
    "/my",
    response_model=EnrollmentPaginatedResponse,
    summary="내 수강 목록 조회",
    description="현재 사용자가 수강 중인 강의 목록을 조회합니다.",
    responses={
        200: {"description": "수강 목록 조회 성공"},
        **AUTH_RESPONSES
    }
)
async def get_my_enrollments(
    params: MyEnrollmentListParams = Depends(),
    current_user: User = Depends(get_current_user)
):
    pass

@router.get(
    "/{enrollment_id}",
    response_model=EnrollmentDetailResponse,
    summary="수강 상세 조회",
    description="특정 수강 등록의 상세 정보를 조회합니다.",
    responses={
        200: {"description": "수강 상세 조회 성공"},
        **AUTH_RESPONSES,
        **READ_RESPONSES
    }
)
async def get_enrollment(
    enrollment_id: int,
    current_user: User = Depends(get_current_user)
):
    pass

@router.delete(
    "/{enrollment_id}",
    response_model=MessageResponse,
    summary="수강 취소",
    description="수강 등록을 취소합니다. 환불 가능 기간 내에만 취소할 수 있습니다.",
    responses={
        200: {"description": "수강 취소 성공"},
        **ENROLLMENT_CANCEL_RESPONSES,
        400: {
            "description": "수강 취소 불가",
            "content": {
                "application/json": {
                    "example": {
                        "error": "CANCELLATION_NOT_ALLOWED",
                        "detail": "환불 가능 기간이 지났습니다"
                    }
                }
            }
        },
        **READ_RESPONSES
    }
)
async def cancel_enrollment(
    enrollment_id: int,
    current_user: User = Depends(get_current_user)
):
    pass

@router.post(
    "/progress",
    response_model=ProgressResponse,
    status_code=status.HTTP_201_CREATED,
    summary="학습 진행 생성",
    description="새로운 강의 영상의 학습 진행을 시작합니다.",
    responses={
        201: {"description": "학습 진행 생성 성공"},
        **PROGRESS_UPDATE_RESPONSES
    }
)
async def create_progress(
    data: ProgressCreate,
    current_user: User = Depends(get_current_user)
):
    pass

@router.patch(
    "/progress/lectures/{lecture_id}",
    response_model=ProgressResponse,
    summary="학습 진행 업데이트",
    description="강의 영상의 학습 진행 상태를 업데이트합니다.",
    responses={
        200: {"description": "학습 진행 업데이트 성공"},
        **PROGRESS_UPDATE_RESPONSES
    }
)
async def update_progress(
    lecture_id: int,
    data: ProgressUpdate,
    current_user: User = Depends(get_current_user)
):
    pass

@router.get(
    "/progress/course/{course_id}",
    response_model=CourseProgressDetail,
    summary="강의별 학습 진행 조회",
    description="특정 강의의 전체 학습 진행 상황을 조회합니다.",
    responses={
        200: {"description": "학습 진행 조회 성공"},
        **ENROLLMENT_ACCESS_RESPONSES
    }
)
async def get_course_progress(
    course_id: int,
    current_user: User = Depends(get_current_user)
):
    pass

@router.get(
    "/progress/lecture/{lecture_id}",
    response_model=ProgressResponse,
    summary="강의 영상별 진행 조회",
    description="특정 강의 영상의 학습 진행 상태를 조회합니다.",
    responses={
        200: {"description": "진행 정보 조회 성공"},
        **ENROLLMENT_ACCESS_RESPONSES
    }
)
async def get_lecture_progress(
    lecture_id: int,
    current_user: User = Depends(get_current_user)
):
    pass

@router.get(
    "/dashboard",
    response_model=StudentDashboard,
    summary="학습자 대시보드",
    description="학습자의 전체 학습 현황을 요약하여 보여줍니다.",
    responses={
        200: {"description": "대시보드 조회 성공"},
        **AUTH_RESPONSES
    }
)
async def get_student_dashboard(current_user: User = Depends(get_current_user)):
    pass

@router.get(
    "/stats",
    response_model=LearningStats,
    summary="학습 통계",
    description="학습 시간, 출석 등의 통계 정보를 조회합니다.",
    responses={
        200: {"description": "통계 조회 성공"},
        **AUTH_RESPONSES
    }
)
async def get_learning_stats(current_user: User = Depends(get_current_user)):
    pass
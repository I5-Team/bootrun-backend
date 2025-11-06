"""
수강 등록 및 학습 진행 API 라우터
수강 등록, 학습 진행 기록, 진행률 조회 등을 처리합니다.
"""

from fastapi import APIRouter, Depends, status
from schemas.common import MessageResponse
from schemas.enrollment import (
    EnrollmentCreate, EnrollmentResponse, EnrollmentDetailResponse,
    EnrollmentPaginatedResponse, MyEnrollmentListParams,
    ProgressCreate, ProgressUpdate, ProgressResponse, 
    CourseProgressDetail, StudentDashboard, LearningStats
)
from exceptions import (
    ENROLLMENT_CREATE_RESPONSES,
    ENROLLMENT_ACCESS_RESPONSES,
    PROGRESS_UPDATE_RESPONSES,
    AUTH_RESPONSES,
    READ_RESPONSES,
    MODIFY_RESPONSES,
)

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
async def create_enrollment(data: EnrollmentCreate):
    """
    # 수강 등록 API
    
    결제 완료 후 강의를 수강 등록합니다.
    
    ## 요청 본문
    - **course_id**: 등록할 강의 ID
    
    ## 응답
    - 201: 수강 등록 성공
    - 400: 이미 등록한 강의
    - 401: 인증되지 않은 사용자
    - 404: 강의를 찾을 수 없음
    
    ## 참고
    - 수강 기간은 등록일로부터 2년입니다
    - 같은 강의를 중복 등록할 수 없습니다
    """
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
async def get_my_enrollments(params: MyEnrollmentListParams = Depends()):
    """
    # 내 수강 목록 조회 API
    
    수강 중인 강의 목록을 조회합니다.
    
    ## 쿼리 파라미터
    - **category_id**: 카테고리 필터 (선택)
    - **difficulty**: 난이도 필터 (선택)
    - **is_active**: 활성 상태 필터 (기본값: true)
        - true: 수강 기간 내 강의만
        - false: 만료된 강의만
        - 미입력: 모든 강의
    - **page**: 페이지 번호 (기본값: 1)
    - **page_size**: 페이지 크기 (기본값: 20, 최대: 100)
    
    ## 응답
    - 200: 수강 목록 조회 성공
    - 401: 인증되지 않은 사용자
    
    ## 반환 정보
    - 강의 기본 정보
    - 진행률
    - 수강 기간 (등록일, 만료일, 남은 일수)
    - 완료/전체 강의 수
    """
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
async def get_enrollment(enrollment_id: int):
    """
    # 수강 상세 조회 API
    
    수강 등록의 상세 정보를 조회합니다.
    
    ## 경로 파라미터
    - **enrollment_id**: 수강 등록 ID
    
    ## 응답
    - 200: 수강 정보 조회 성공
    - 401: 인증되지 않은 사용자
    - 403: 다른 사용자의 수강 정보는 조회 불가
    - 404: 수강 정보를 찾을 수 없음
    
    ## 반환 정보
    - 강의 상세 정보
    - 진행률 및 학습 시간
    - 미션 진행 현황
    - 수강 기간 정보
    """
    pass


@router.delete(
    "/{enrollment_id}",
    response_model=MessageResponse,
    summary="수강 취소",
    description="수강 등록을 취소합니다. 환불 가능 기간 내에만 취소할 수 있습니다.",
    responses={
        200: {"description": "수강 취소 성공"},
        **AUTH_RESPONSES,
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
async def cancel_enrollment(enrollment_id: int):
    """
    # 수강 취소 API
    
    수강 등록을 취소하고 환불을 신청합니다.
    
    ## 경로 파라미터
    - **enrollment_id**: 수강 등록 ID
    
    ## 응답
    - 200: 수강 취소 성공
    - 400: 환불 가능 기간 초과 또는 진도율 10% 이상
    - 401: 인증되지 않은 사용자
    - 404: 수강 정보를 찾을 수 없음
    
    ## 참고
    - 환불 가능 조건: 구매일 7일 이내 + 진도율 10% 미만
    - 취소 시 자동으로 환불이 신청됩니다
    """
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
async def create_progress(data: ProgressCreate):
    """
    # 학습 진행 생성 API
    
    강의 영상 시청을 시작할 때 호출합니다.
    
    ## 요청 본문
    - **lecture_id**: 강의 영상 ID
    - **watched_seconds**: 시청 시간 (초)
    - **last_position**: 마지막 시청 위치 (초)
    - **is_completed**: 완료 여부 (기본값: false)
    
    ## 응답
    - 201: 학습 진행 생성 성공
    - 401: 인증되지 않은 사용자
    - 403: 수강 등록되지 않은 강의
    - 404: 강의 영상을 찾을 수 없음
    """
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
async def update_progress(lecture_id: int, data: ProgressUpdate):
    """
    # 학습 진행 업데이트 API
    
    강의 영상 시청 중 주기적으로 호출하여 진행 상태를 저장합니다.
    
    ## 경로 파라미터
    - **lecture_id**: 강의 영상 ID
    
    ## 요청 본문
    - **watched_seconds**: 총 시청 시간 (초)
    - **last_position**: 마지막 시청 위치 (초)
    - **is_completed**: 완료 여부
    
    ## 응답
    - 200: 학습 진행 업데이트 성공
    - 401: 인증되지 않은 사용자
    - 403: 수강 등록되지 않은 강의
    - 404: 강의 영상 또는 진행 기록을 찾을 수 없음
    
    ## 참고
    - 10초마다 호출을 권장합니다
    - 영상의 90% 이상 시청 시 자동으로 완료 처리됩니다
    """
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
async def get_course_progress(course_id: int):
    """
    # 강의별 학습 진행 조회 API
    
    강의의 전체 학습 진행 상황을 챕터별로 조회합니다.
    
    ## 경로 파라미터
    - **course_id**: 강의 ID
    
    ## 응답
    - 200: 학습 진행 조회 성공
    - 401: 인증되지 않은 사용자
    - 403: 수강 등록되지 않은 강의
    - 404: 강의를 찾을 수 없음
    
    ## 반환 정보
    - 전체 진행률
    - 챕터별 진행 상황
    - 각 강의 영상의 시청 정보
    - 총 학습 시간
    """
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
async def get_lecture_progress(lecture_id: int):
    """
    # 강의 영상별 진행 조회 API
    
    강의 영상의 시청 기록을 조회합니다.
    
    ## 경로 파라미터
    - **lecture_id**: 강의 영상 ID
    
    ## 응답
    - 200: 진행 정보 조회 성공
    - 401: 인증되지 않은 사용자
    - 403: 수강 등록되지 않은 강의
    - 404: 강의 영상을 찾을 수 없음
    
    ## 반환 정보
    - 시청 시간
    - 마지막 시청 위치 (이어보기용)
    - 완료 여부
    - 완료율
    
    ## 사용 사례
    - 영상 플레이어 로드 시 마지막 위치로 이동
    - 진행률 표시
    """
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
async def get_student_dashboard():
    """
    # 학습자 대시보드 API
    
    학습자의 전체 학습 현황을 한눈에 볼 수 있습니다.
    
    ## 응답
    - 200: 대시보드 조회 성공
    - 401: 인증되지 않은 사용자
    
    ## 반환 정보
    - 전체 수강 통계: 총 수강 수, 활성 수강 수, 완료 수
    - 총 학습 시간
    - 평균 진행률
    - 최근 활동 내역
    - 만료 임박 강의 목록
    
    ## 사용 사례
    - 마이페이지 메인 화면
    - 학습 현황 요약 표시
    """
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
async def get_learning_stats():
    """
    # 학습 통계 API
    
    시간별 학습 통계를 조회합니다.
    
    ## 응답
    - 200: 통계 조회 성공
    - 401: 인증되지 않은 사용자
    
    ## 반환 정보
    - **today_study_time**: 오늘 학습 시간 (분)
    - **week_study_time**: 이번 주 학습 시간 (분)
    - **month_study_time**: 이번 달 학습 시간 (분)
    - **total_study_time**: 총 학습 시간 (분)
    - **study_streak**: 연속 학습 일수
    - **last_study_date**: 마지막 학습일
    
    ## 사용 사례
    - 학습 동기 부여
    - 학습 패턴 분석
    """
    pass
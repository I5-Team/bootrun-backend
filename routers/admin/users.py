"""
관리자 사용자 관리 API 라우터
사용자 목록 조회, 상세 조회, 활성화/비활성화, 학습 리포트 등을 처리합니다.
"""

from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from schemas.admin import (
    UserManagementListParams, UserManagementPaginatedResponse,
    UserDetailForAdmin, UserLearningReport
)
from schemas.common import MessageResponse
from exceptions import (
    ADMIN_USER_MANAGEMENT_RESPONSES,
    ADMIN_RESPONSES,
)

router = APIRouter(prefix="/admin/users", tags=["관리자 - 사용자 관리"])


@router.get(
    "",
    response_model=UserManagementPaginatedResponse,
    summary="사용자 목록 조회",
    description="전체 사용자 목록을 조회합니다.",
    responses=ADMIN_RESPONSES
)
async def get_users(params: UserManagementListParams = Depends()):
    """
    # 사용자 목록 조회 API
    
    전체 사용자 목록을 조회합니다.
    
    ## 쿼리 파라미터
    - role: 역할 필터 (student/admin)
    - is_active: 활성화 여부
    - keyword: 검색 키워드 (이름, 이메일)
    - start_date: 가입일 시작
    - end_date: 가입일 종료
    - page: 페이지 번호
    - page_size: 페이지 크기
    
    ## 응답
    - 200: 사용자 목록 조회 성공
    - 401: 인증되지 않은 사용자
    - 403: 관리자 권한 필요
    """
    pass


@router.get(
    "/{user_id}",
    response_model=UserDetailForAdmin,
    summary="사용자 상세 조회",
    description="특정 사용자의 상세 정보를 조회합니다.",
    responses=ADMIN_USER_MANAGEMENT_RESPONSES
)
async def get_user(user_id: int):
    """
    # 사용자 상세 조회 API
    
    사용자의 상세 정보를 조회합니다.
    
    ## 경로 파라미터
    - user_id: 사용자 ID
    
    ## 응답
    - 200: 사용자 정보 조회 성공
    - 401: 인증되지 않은 사용자
    - 403: 관리자 권한 필요
    - 404: 사용자를 찾을 수 없음
    
    ## 반환 정보
    - 기본 정보
    - 학습 정보
    - 결제 정보
    - 활동 정보
    - 수강 목록
    """
    pass


@router.patch(
    "/{user_id}/activate",
    response_model=MessageResponse,
    summary="사용자 활성화",
    description="비활성화된 사용자를 활성화합니다.",
    responses=ADMIN_USER_MANAGEMENT_RESPONSES
)
async def activate_user(user_id: int):
    """
    # 사용자 활성화 API
    
    비활성화된 사용자를 활성화합니다.
    
    ## 경로 파라미터
    - user_id: 사용자 ID
    
    ## 응답
    - 200: 활성화 성공
    - 401: 인증되지 않은 사용자
    - 403: 관리자 권한 필요
    - 404: 사용자를 찾을 수 없음
    """
    pass


@router.patch(
    "/{user_id}/deactivate",
    response_model=MessageResponse,
    summary="사용자 비활성화",
    description="사용자를 비활성화합니다.",
    responses=ADMIN_USER_MANAGEMENT_RESPONSES
)
async def deactivate_user(user_id: int):
    """
    # 사용자 비활성화 API
    
    사용자를 비활성화합니다.
    
    ## 경로 파라미터
    - user_id: 사용자 ID
    
    ## 응답
    - 200: 비활성화 성공
    - 401: 인증되지 않은 사용자
    - 403: 관리자 권한 필요
    - 404: 사용자를 찾을 수 없음
    
    ## 참고
    - 비활성화된 사용자는 로그인할 수 없습니다
    """
    pass


@router.delete(
    "/{user_id}",
    response_model=MessageResponse,
    summary="사용자 삭제",
    description="사용자를 완전히 삭제합니다.",
    responses=ADMIN_USER_MANAGEMENT_RESPONSES
)
async def delete_user(user_id: int):
    """
    # 사용자 삭제 API
    
    사용자를 삭제합니다.
    
    ## 경로 파라미터
    - user_id: 사용자 ID
    
    ## 응답
    - 200: 삭제 성공
    - 401: 인증되지 않은 사용자
    - 403: 관리자 권한 필요
    - 404: 사용자를 찾을 수 없음
    
    ## 주의
    - 이 작업은 되돌릴 수 없습니다
    - 모든 학습 기록이 삭제됩니다
    """
    pass


@router.get(
    "/{user_id}/learning-report",
    response_model=UserLearningReport,
    summary="사용자 학습 리포트",
    description="사용자의 학습 리포트를 조회합니다.",
    responses=ADMIN_USER_MANAGEMENT_RESPONSES
)
async def get_user_learning_report(user_id: int, report_period: str):
    """
    # 학습 리포트 API
    
    사용자의 학습 리포트를 조회합니다.
    
    ## 경로 파라미터
    - user_id: 사용자 ID
    
    ## 쿼리 파라미터
    - report_period: 리포트 기간 (예: "2025-01")
    
    ## 응답
    - 200: 리포트 조회 성공
    - 401: 인증되지 않은 사용자
    - 403: 관리자 권한 필요
    - 404: 사용자를 찾을 수 없음
    
    ## 반환 정보
    - 총 학습 시간
    - 출석률
    - 평균 진행률
    - 강의별 진행 상황
    - 출석 현황
    """
    pass


@router.get(
    "/export",
    summary="사용자 목록 내보내기",
    description="사용자 목록을 엑셀 파일로 내보냅니다.",
    responses=ADMIN_RESPONSES
)
async def export_users(params: UserManagementListParams = Depends()):
    """
    # 사용자 목록 내보내기 API
    
    사용자 목록을 엑셀 파일로 내보냅니다.
    
    ## 쿼리 파라미터
    - UserManagementListParams와 동일
    
    ## 응답
    - 200: 엑셀 파일 스트리밍
    - 401: 인증되지 않은 사용자
    - 403: 관리자 권한 필요
    
    ## Content-Type
    - application/vnd.openxmlformats-officedocument.spreadsheetml.sheet
    """
    pass
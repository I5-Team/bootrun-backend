"""
미션 API 라우터
강의별 미션 조회, 미션 제출, 제출 내역 조회 등을 처리합니다.
"""

from fastapi import APIRouter, status
from typing import List
from schemas.mission import (
    MissionWithUserStatus, MissionSubmissionCreate,
    MissionSubmissionResponse, MissionSubmissionHistory,
    UserMissionProgress, MissionStats
)
from exceptions import (
    MISSION_SUBMIT_RESPONSES,
    AUTH_RESPONSES,
    READ_RESPONSES,
    ENROLLMENT_ACCESS_RESPONSES,
)

router = APIRouter(prefix="/missions", tags=["미션"])


@router.get(
    "/courses/{course_id}",
    response_model=List[MissionWithUserStatus],
    summary="강의별 미션 목록",
    description="특정 강의의 모든 미션(중간/기말)을 조회합니다.",
    responses=ENROLLMENT_ACCESS_RESPONSES
)
async def get_course_missions(course_id: int):
    """
    # 강의별 미션 목록 API
    
    강의에 포함된 모든 미션을 조회합니다.
    
    ## 경로 파라미터
    - **course_id**: 강의 ID
    
    ## 응답
    - 200: 미션 목록 조회 성공
    - 401: 인증되지 않은 사용자
    - 403: 수강 등록되지 않은 강의
    - 404: 강의를 찾을 수 없음
    
    ## 반환 정보
    - 미션 기본 정보 (제목, 설명, 유형)
    - 문제 정보 (문제 수, 배점)
    - 사용자 진행 상태
        - 제출 횟수 / 남은 횟수
        - 최고 점수
        - 통과 여부
    """
    pass


@router.get(
    "/{mission_id}",
    response_model=MissionWithUserStatus,
    summary="미션 상세 조회",
    description="특정 미션의 상세 정보와 문제를 조회합니다.",
    responses=ENROLLMENT_ACCESS_RESPONSES
)
async def get_mission(mission_id: int):
    """
    # 미션 상세 조회 API
    
    미션의 상세 정보와 문제를 조회합니다.
    
    ## 경로 파라미터
    - **mission_id**: 미션 ID
    
    ## 응답
    - 200: 미션 정보 조회 성공
    - 401: 인증되지 않은 사용자
    - 403: 수강 등록되지 않은 강의의 미션
    - 404: 미션을 찾을 수 없음
    
    ## 반환 정보
    - 미션 설명 및 제출 조건
    - 문제 데이터 (question_data)
        - 5지선다형: 질문, 보기
        - 코드 제출형: 문제 설명, 입출력 예제
    - 최대 점수 / 통과 기준 점수
    - 사용자 제출 이력
    
    ## 참고
    - 정답 데이터(answer_data)는 포함되지 않습니다
    """
    pass


@router.post(
    "/submissions",
    response_model=MissionSubmissionResponse,
    status_code=status.HTTP_201_CREATED,
    summary="미션 제출",
    description="미션 답안을 제출하고 자동 채점 결과를 받습니다.",
    responses=MISSION_SUBMIT_RESPONSES
)
async def submit_mission(data: MissionSubmissionCreate):
    """
    # 미션 제출 API
    
    미션 답안을 제출하고 채점 결과를 받습니다.
    
    ## 요청 본문
    - **mission_id**: 미션 ID
    - **answer**: 답안 데이터 (JSON)
        - 5지선다형: {"answers": [1, 3, 2, ...]}  (선택한 번호 배열)
        - 코드 제출형: {"code": "function solution() {...}"}
    
    ## 응답
    - 201: 제출 성공, 채점 결과 반환
    - 400: 최대 제출 횟수 초과
    - 401: 인증되지 않은 사용자
    - 403: 수강 등록되지 않은 강의
    - 404: 미션을 찾을 수 없음
    
    ## 반환 정보
    - 획득 점수
    - 통과 여부
    - 피드백 (틀린 문제 등)
    - 남은 제출 횟수
    - 실행 결과 (코드 제출형)
    
    ## 채점 방식
    - **5지선다형**: 정답과 비교하여 자동 채점
    - **코드 제출형**: 테스트 케이스 실행 후 채점
    
    ## 참고
    - 최대 제출 횟수 제한이 있습니다 (기본 3회)
    - 최고 점수가 기록됩니다
    """
    pass


@router.get(
    "/{mission_id}/submissions",
    response_model=List[MissionSubmissionHistory],
    summary="미션 제출 내역",
    description="특정 미션의 제출 내역을 조회합니다.",
    responses=ENROLLMENT_ACCESS_RESPONSES
)
async def get_mission_submissions(mission_id: int):
    """
    # 미션 제출 내역 API
    
    사용자의 미션 제출 이력을 조회합니다.
    
    ## 경로 파라미터
    - **mission_id**: 미션 ID
    
    ## 응답
    - 200: 제출 내역 조회 성공
    - 401: 인증되지 않은 사용자
    - 403: 수강 등록되지 않은 강의
    - 404: 미션을 찾을 수 없음
    
    ## 반환 정보
    - 각 제출의 점수 및 통과 여부
    - 제출 일시
    - 시도 번호
    
    ## 사용 사례
    - 제출 이력 확인
    - 점수 변화 추이 확인
    """
    pass


@router.get(
    "/{mission_id}/progress",
    response_model=UserMissionProgress,
    summary="미션 진행 현황",
    description="사용자의 미션 진행 현황을 상세하게 조회합니다.",
    responses=ENROLLMENT_ACCESS_RESPONSES
)
async def get_mission_progress(mission_id: int):
    """
    # 미션 진행 현황 API
    
    미션의 진행 상황을 상세하게 조회합니다.
    
    ## 경로 파라미터
    - **mission_id**: 미션 ID
    
    ## 응답
    - 200: 진행 현황 조회 성공
    - 401: 인증되지 않은 사용자
    - 403: 수강 등록되지 않은 강의
    - 404: 미션을 찾을 수 없음
    
    ## 반환 정보
    - 미션 기본 정보
    - 제출 횟수 및 남은 횟수
    - 최고 점수
    - 통과 여부
    - 전체 제출 내역
    """
    pass


@router.get(
    "/{mission_id}/stats",
    response_model=MissionStats,
    summary="미션 통계",
    description="미션의 전체 통계 정보를 조회합니다. (수강생 전체 대상)",
    responses=ENROLLMENT_ACCESS_RESPONSES
)
async def get_mission_stats(mission_id: int):
    """
    # 미션 통계 API
    
    미션의 전체 통계를 조회합니다.
    
    ## 경로 파라미터
    - **mission_id**: 미션 ID
    
    ## 응답
    - 200: 통계 조회 성공
    - 401: 인증되지 않은 사용자
    - 403: 수강 등록되지 않은 강의
    - 404: 미션을 찾을 수 없음
    
    ## 반환 정보
    - 총 제출 횟수
    - 통과/실패 인원 수
    - 통과율
    - 평균 점수
    - 평균 시도 횟수
    
    ## 사용 사례
    - 난이도 파악
    - 학습 동기 부여
    """
    pass
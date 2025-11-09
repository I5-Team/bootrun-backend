from fastapi import APIRouter, status, Depends
from typing import List
from app.schemas.mission import (
    MissionWithUserStatus, MissionSubmissionCreate,
    MissionSubmissionResponse, MissionSubmissionHistory,
    UserMissionProgress, MissionStats
)
from app.exceptions.responses import (
    MISSION_SUBMIT_RESPONSES,
    AUTH_RESPONSES,
    READ_RESPONSES,
    ENROLLMENT_ACCESS_RESPONSES,
)
from app.core.dependencies import get_current_user
from app.models.user import User

router = APIRouter(prefix="/missions", tags=["미션"])

@router.get(
    "/courses/{course_id}",
    response_model=List[MissionWithUserStatus],
    summary="강의별 미션 목록",
    description="특정 강의의 모든 미션(중간/기말)을 조회합니다.",
    responses={
        200: {"description": "미션 목록 조회 성공"},
        **ENROLLMENT_ACCESS_RESPONSES
    }
)
async def get_course_missions(
    course_id: int,
    current_user: User = Depends(get_current_user)
):
    pass

@router.get(
    "/{mission_id}",
    response_model=MissionWithUserStatus,
    summary="미션 상세 조회",
    description="특정 미션의 상세 정보와 문제를 조회합니다.",
    responses={
        200: {"description": "미션 상세 조회 성공"},
        **ENROLLMENT_ACCESS_RESPONSES
    }
)
async def get_mission(
    mission_id: int,
    current_user: User = Depends(get_current_user)
):
    pass

@router.post(
    "/submissions",
    response_model=MissionSubmissionResponse,
    status_code=status.HTTP_201_CREATED,
    summary="미션 제출",
    description="미션 답안을 제출하고 자동 채점 결과를 받습니다.",
    responses={
        201: {"description": "미션 제출 성공"},
        **MISSION_SUBMIT_RESPONSES
    }
)
async def submit_mission(
    data: MissionSubmissionCreate,
    current_user: User = Depends(get_current_user)
):
    pass

@router.get(
    "/{mission_id}/submissions",
    response_model=List[MissionSubmissionHistory],
    summary="미션 제출 내역",
    description="특정 미션의 제출 내역을 조회합니다.",
    responses={
        200: {"description": "제출 내역 조회 성공"},
        **ENROLLMENT_ACCESS_RESPONSES
    }
)
async def get_mission_submissions(
    mission_id: int,
    current_user: User = Depends(get_current_user)
):
    pass

@router.get(
    "/{mission_id}/progress",
    response_model=UserMissionProgress,
    summary="미션 진행 현황",
    description="사용자의 미션 진행 현황을 상세하게 조회합니다.",
    responses={
        200: {"description": "진행 현황 조회 성공"},
        **ENROLLMENT_ACCESS_RESPONSES
    }
)
async def get_mission_progress(
    mission_id: int,
    current_user: User = Depends(get_current_user)
):
    pass

@router.get(
    "/{mission_id}/stats",
    response_model=MissionStats,
    summary="미션 통계",
    description="미션의 전체 통계 정보를 조회합니다. (수강생 전체 대상)",
    responses={
        200: {"description": "통계 조회 성공"},
        **ENROLLMENT_ACCESS_RESPONSES
    }
)
async def get_mission_stats(
    mission_id: int,
    current_user: User = Depends(get_current_user)
):
    pass
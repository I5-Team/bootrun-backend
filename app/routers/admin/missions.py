from fastapi import APIRouter, status
from app.schemas.common import MessageResponse, SuccessResponse
from app.schemas.mission import MissionCreate, MissionUpdate, MissionResponse
from app.exceptions.responses import (
    MISSION_CREATE_RESPONSES,
    MODIFY_RESPONSES,
)

router = APIRouter(prefix="/admin/missions", tags=["관리자 - 미션 관리"])

@router.post(
    "/courses/{course_id}/missions",
    response_model=SuccessResponse[MissionResponse],
    status_code=status.HTTP_201_CREATED,
    summary="미션 생성",
    description="강의에 새로운 미션을 추가합니다.",
    responses={
        201: {"description": "미션 생성 성공"},
        **MISSION_CREATE_RESPONSES
    }
)
async def create_mission(course_id: int, data: MissionCreate):
    pass

@router.patch(
    "/{mission_id}",
    response_model=SuccessResponse[MissionResponse],
    summary="미션 수정",
    description="미션 정보를 수정합니다.",
    responses={
        200: {"description": "미션 수정 성공"},
        **MODIFY_RESPONSES
    }
)
async def update_mission(mission_id: int, data: MissionUpdate):
    pass

@router.delete(
    "/{mission_id}",
    response_model=MessageResponse,
    summary="미션 삭제",
    description="미션을 삭제합니다.",
    responses={
        200: {"description": "미션 삭제 완료"},
        **MODIFY_RESPONSES
    }
)
async def delete_mission(mission_id: int):
    pass
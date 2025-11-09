from fastapi import APIRouter, Depends, status
from app.schemas.admin import (
    CourseManagementListParams, CourseAnalyticsResponse, CourseManagementPaginatedResponse,
)
from app.schemas.common import MessageResponse, SuccessResponse
from app.schemas.course import (
    CourseCreate, CourseUpdate, CourseResponse,
    ChapterCreate, ChapterUpdate, ChapterResponse,
    LectureCreate, LectureUpdate, LectureResponse
)
from app.exceptions.responses import (
    ADMIN_COURSE_MANAGEMENT_RESPONSES,
    COURSE_CREATE_RESPONSES,
    COURSE_UPDATE_RESPONSES,
    CHAPTER_CREATE_RESPONSES,
    LECTURE_CREATE_RESPONSES,
    ADMIN_RESPONSES,
)

router = APIRouter(prefix="/admin/courses", tags=["관리자 - 강의 관리"])

@router.get(
    "",
    response_model=CourseManagementPaginatedResponse,
    summary="강의 목록 조회",
    description="관리자용 강의 목록을 조회합니다.",
    responses={
        200: {"description": "강의 목록 조회 성공"},
        **ADMIN_RESPONSES
    }
)
async def get_courses(params: CourseManagementListParams = Depends()):
    pass

@router.post(
    "",
    response_model=SuccessResponse[CourseResponse],
    status_code=status.HTTP_201_CREATED,
    summary="강의 생성",
    description="새로운 강의를 생성합니다.",
    responses={
        201: {"description": "강의 생성 성공"},
        **COURSE_CREATE_RESPONSES
    }
)
async def create_course(data: CourseCreate):
    pass

@router.patch(
    "/{course_id}",
    response_model=SuccessResponse[CourseResponse],
    summary="강의 수정",
    description="강의 정보를 수정합니다.",
    responses={
        200: {"description": "강의 수정 성공"},
        **COURSE_UPDATE_RESPONSES
    }
)
async def update_course(course_id: int, data: CourseUpdate):
    pass

@router.delete(
    "/{course_id}",
    response_model=MessageResponse,
    summary="강의 삭제",
    description="강의를 삭제합니다.",
    responses={
        200: {"description": "강의 삭제 완료"},
        **ADMIN_COURSE_MANAGEMENT_RESPONSES
    }
)
async def delete_course(course_id: int):
    pass

@router.post(
    "/{course_id}/publish",
    response_model=MessageResponse,
    summary="강의 공개",
    description="강의를 공개 상태로 변경합니다.",
    responses={
        200: {"description": "강의 공개 완료"},
        **ADMIN_COURSE_MANAGEMENT_RESPONSES
    }
)
async def publish_course(course_id: int):
    pass

@router.post(
    "/{course_id}/unpublish",
    response_model=MessageResponse,
    summary="강의 비공개",
    description="강의를 비공개 상태로 변경합니다.",
    responses={
        200: {"description": "강의 비공개 완료"},
        **ADMIN_COURSE_MANAGEMENT_RESPONSES
    }
)
async def unpublish_course(course_id: int):
    pass

@router.get(
    "/{course_id}/analytics",
    response_model=SuccessResponse[CourseAnalyticsResponse],
    summary="강의 분석",
    description="강의의 상세 분석 데이터를 조회합니다.",
    responses={
        200: {"description": "강의 분석 조회 성공"},
        **ADMIN_COURSE_MANAGEMENT_RESPONSES
    }
)
async def get_course_analytics(course_id: int):
    pass

@router.post(
    "/{course_id}/duplicate",
    response_model=SuccessResponse[CourseResponse],
    summary="강의 복제",
    description="기존 강의를 복제하여 새 강의를 생성합니다.",
    responses={
        200: {"description": "강의 복제 성공"},
        **ADMIN_COURSE_MANAGEMENT_RESPONSES
    }
)
async def duplicate_course(course_id: int):
    pass

@router.get(
    "/export",
    summary="강의 목록 내보내기",
    description="강의 목록을 엑셀 파일로 내보냅니다.",
    responses={
        200: {"description": "강의 목록 내보내기 완료"},
        **ADMIN_RESPONSES
    }
)
async def export_courses(params: CourseManagementListParams = Depends()):
    pass

@router.post(
    "/{course_id}/chapters",
    response_model=SuccessResponse[ChapterResponse],
    status_code=status.HTTP_201_CREATED,
    summary="챕터 생성",
    description="강의에 새로운 챕터를 추가합니다.",
    responses={
        201: {"description": "챕터 생성 성공"},
        **CHAPTER_CREATE_RESPONSES
    }
)
async def create_chapter(course_id: int, data: ChapterCreate):
    pass

@router.patch(
    "/{course_id}/chapters/{chapter_id}",
    response_model=SuccessResponse[ChapterResponse],
    summary="챕터 수정",
    description="챕터 정보를 수정합니다.",
    responses={
        200: {"description": "챕터 수정 성공"},
        **ADMIN_COURSE_MANAGEMENT_RESPONSES
    }
)
async def update_chapter(course_id: int, chapter_id: int, data: ChapterUpdate):
    pass

@router.delete(
    "/{course_id}/chapters/{chapter_id}",
    response_model=MessageResponse,
    summary="챕터 삭제",
    description="챕터를 삭제합니다.",
    responses={
        200: {"description": "챕터 삭제 완료"},
        **ADMIN_COURSE_MANAGEMENT_RESPONSES
    }
)
async def delete_chapter(course_id: int, chapter_id: int):
    pass

@router.post(
    "/{course_id}/chapters/{chapter_id}/lectures",
    response_model=SuccessResponse[LectureResponse],
    status_code=status.HTTP_201_CREATED,
    summary="강의 영상 생성",
    description="챕터에 새로운 강의 영상을 추가합니다.",
    responses={
        201: {"description": "강의 영상 생성 성공"},
        **LECTURE_CREATE_RESPONSES
    }
)
async def create_lecture(course_id: int, chapter_id: int, data: LectureCreate):
    pass

@router.patch(
    "/{course_id}/chapters/{chapter_id}/lectures/{lecture_id}",
    response_model=SuccessResponse[LectureResponse],
    summary="강의 영상 수정",
    description="강의 영상 정보를 수정합니다.",
    responses={
        200: {"description": "강의 영상 수정 성공"},
        **ADMIN_COURSE_MANAGEMENT_RESPONSES
    }
)
async def update_lecture(course_id: int, chapter_id: int, lecture_id: int, data: LectureUpdate):
    pass

@router.delete(
    "/{course_id}/chapters/{chapter_id}/lectures/{lecture_id}",
    response_model=MessageResponse,
    summary="강의 영상 삭제",
    description="강의 영상을 삭제합니다.",
    responses={
        200: {"description": "강의 영상 삭제 완료"},
        **ADMIN_COURSE_MANAGEMENT_RESPONSES
    }
)
async def delete_lecture(course_id: int, chapter_id: int, lecture_id: int):
    pass
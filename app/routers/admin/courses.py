from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import ValidationError

from typing import List, Optional

from app.schemas.admin import (
    CourseManagementListParams, CourseManagementPaginatedResponse,
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
from app.core.dependencies import get_current_admin, get_db
from app.models.user import User
from app.services.admin_course_service import AdminCourseService

router = APIRouter(prefix="/admin/courses", tags=["관리자 - 강의 관리"])

# ==================== 파일 업로드 API 제거됨 ====================
# 파일 업로드는 /storage 엔드포인트를 사용하세요:
# - POST /storage/upload/image - 이미지 업로드 (썸네일, 강사 이미지)
# - POST /storage/upload/video - 동영상 업로드
# - POST /storage/upload - 일반 파일 업로드 (강의 자료)
# - DELETE /storage/delete/{file_path} - 파일 삭제
# - GET /storage/list - 파일 목록 조회
# =============================================================

@router.get(
    "",
    response_model=SuccessResponse[CourseManagementPaginatedResponse],
    summary="강의 목록 조회",
    description="관리자용 강의 목록을 조회합니다. 수강생 수, 매출, 평균 진행률, 완료율 등의 정보를 포함합니다.",
    operation_id="admin_get_courses",
    responses=ADMIN_RESPONSES
)
async def get_courses(
    params: CourseManagementListParams = Depends(),
    current_admin: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db)
):
    service = AdminCourseService(db)
    result = await service.get_courses_for_admin(params)

    return SuccessResponse(
        success=True,
        message="강의 목록 조회 성공",
        data=result
    )

@router.get(
    "/{course_id}",
    response_model=SuccessResponse[CourseResponse],
    summary="강의 상세 조회",
    description="관리자용 강의 상세 정보를 조회합니다. 비공개 강의도 조회할 수 있습니다.",
    operation_id="admin_get_course_detail",
    responses=ADMIN_COURSE_MANAGEMENT_RESPONSES
)
async def get_course(
    course_id: int,
    current_admin: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db)
):
    service = AdminCourseService(db)
    course = await service.get_course_by_id(course_id)

    return SuccessResponse(
        success=True,
        message="강의 상세 조회 성공",
        data=course
    )

@router.post(
    "",
    response_model=SuccessResponse[CourseResponse],
    status_code=status.HTTP_201_CREATED,
    summary="강의 생성",
    description="새로운 강의를 생성합니다. 기본적으로 비공개 상태로 생성됩니다.",
    operation_id="admin_create_course",
    responses=COURSE_CREATE_RESPONSES
)
async def create_course(
    data: CourseCreate,
    current_admin: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db)
):
    service = AdminCourseService(db)
    course = await service.create_course(data)

    return SuccessResponse(
        success=True,
        message="강의가 성공적으로 생성되었습니다",
        data=course
    )

@router.post(
    "/{course_id}/publish",
    response_model=MessageResponse,
    summary="강의 공개",
    description="강의를 공개 상태로 변경합니다. 사용자들이 강의를 확인할 수 있게 됩니다.",
    responses=ADMIN_COURSE_MANAGEMENT_RESPONSES
)
async def publish_course(
    course_id: int,
    current_admin: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db)
):
    service = AdminCourseService(db)
    await service.publish_course(course_id)

    return MessageResponse(
        success=True,
        message="강의가 공개되었습니다"
    )

@router.post(
    "/{course_id}/unpublish",
    response_model=MessageResponse,
    summary="강의 비공개",
    description="강의를 비공개 상태로 변경합니다. 사용자들이 강의를 확인할 수 없게 됩니다.",
    responses=ADMIN_COURSE_MANAGEMENT_RESPONSES
)
async def unpublish_course(
    course_id: int,
    current_admin: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db)
):
    service = AdminCourseService(db)
    await service.unpublish_course(course_id)

    return MessageResponse(
        success=True,
        message="강의가 비공개되었습니다"
    )

@router.patch(
    "/{course_id}",
    response_model=SuccessResponse[CourseResponse],
    summary="강의 수정",
    description="강의 정보를 수정합니다. 제공된 필드만 수정됩니다.",
    operation_id="admin_update_course",
    responses=COURSE_UPDATE_RESPONSES
)
async def update_course(
    course_id: int,
    data: CourseUpdate,
    current_admin: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db)
):
    service = AdminCourseService(db)
    course = await service.update_course(course_id, data)

    return SuccessResponse(
        success=True,
        message="강의가 성공적으로 수정되었습니다",
        data=course
    )

@router.delete(
    "/{course_id}",
    response_model=MessageResponse,
    summary="강의 삭제",
    description="강의를 삭제합니다. CASCADE로 연결된 챕터, 강의 영상, 수강 등록 등 모든 데이터가 함께 삭제됩니다.",
    operation_id="admin_delete_course",
    responses=ADMIN_COURSE_MANAGEMENT_RESPONSES
)
async def delete_course(
    course_id: int,
    current_admin: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db)
):
    service = AdminCourseService(db)
    await service.delete_course(course_id)

    return MessageResponse(
        success=True,
        message="강의가 성공적으로 삭제되었습니다"
    )

@router.get(
    "/{course_id}/chapters",
    response_model=SuccessResponse[List[ChapterResponse]],
    summary="챕터 목록 조회",
    description="특정 강의의 모든 챕터를 조회합니다. order_number 순서로 정렬됩니다.",
    responses=ADMIN_COURSE_MANAGEMENT_RESPONSES
)
async def get_chapters(
    course_id: int,
    current_admin: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db)
):
    service = AdminCourseService(db)
    chapters = await service.get_chapters(course_id)

    return SuccessResponse(
        success=True,
        message="챕터 목록 조회 성공",
        data=chapters
    )

@router.post(
    "/{course_id}/chapters",
    response_model=SuccessResponse[ChapterResponse],
    status_code=status.HTTP_201_CREATED,
    summary="챕터 생성",
    description="강의에 새로운 챕터를 추가합니다.",
    responses=CHAPTER_CREATE_RESPONSES
)
async def create_chapter(
    course_id: int,
    data: ChapterCreate,
    current_admin: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db)
):
    service = AdminCourseService(db)
    chapter = await service.create_chapter(course_id, data)

    return SuccessResponse(
        success=True,
        message="챕터가 성공적으로 생성되었습니다",
        data=chapter
    )

@router.patch(
    "/{course_id}/chapters/{chapter_id}",
    response_model=SuccessResponse[ChapterResponse],
    summary="챕터 수정",
    description="챕터 정보를 수정합니다. 제공된 필드만 수정됩니다.",
    responses=ADMIN_COURSE_MANAGEMENT_RESPONSES
)
async def update_chapter(
    course_id: int,
    chapter_id: int,
    data: ChapterUpdate,
    current_admin: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db)
):
    service = AdminCourseService(db)
    chapter = await service.update_chapter(course_id, chapter_id, data)

    return SuccessResponse(
        success=True,
        message="챕터가 성공적으로 수정되었습니다",
        data=chapter
    )

@router.delete(
    "/{course_id}/chapters/{chapter_id}",
    response_model=MessageResponse,
    summary="챕터 삭제",
    description="챕터를 삭제합니다. CASCADE로 챕터에 포함된 모든 강의 영상이 함께 삭제됩니다.",
    responses=ADMIN_COURSE_MANAGEMENT_RESPONSES
)
async def delete_chapter(
    course_id: int,
    chapter_id: int,
    current_admin: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db)
):
    service = AdminCourseService(db)
    await service.delete_chapter(course_id, chapter_id)

    return MessageResponse(
        success=True,
        message="챕터가 성공적으로 삭제되었습니다"
    )

@router.get(
    "/{course_id}/chapters/{chapter_id}/lectures",
    response_model=SuccessResponse[List[LectureResponse]],
    summary="강의 영상 목록 조회",
    description="특정 챕터의 모든 강의 영상을 조회합니다. order_number 순서로 정렬됩니다.",
    responses=ADMIN_COURSE_MANAGEMENT_RESPONSES
)
async def get_lectures(
    course_id: int,
    chapter_id: int,
    current_admin: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db)
):
    service = AdminCourseService(db)
    lectures = await service.get_lectures(course_id, chapter_id)

    return SuccessResponse(
        success=True,
        message="강의 영상 목록 조회 성공",
        data=lectures
    )

@router.post(
    "/{course_id}/chapters/{chapter_id}/lectures",
    response_model=SuccessResponse[LectureResponse],
    status_code=status.HTTP_201_CREATED,
    summary="강의 영상 생성",
    description="챕터에 새로운 강의 영상을 추가합니다. VOD 또는 유튜브 영상을 지원합니다.",
    responses=LECTURE_CREATE_RESPONSES
)
async def create_lecture(
    course_id: int,
    chapter_id: int,
    data: LectureCreate,
    current_admin: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db)
):
    service = AdminCourseService(db)
    lecture = await service.create_lecture(course_id, chapter_id, data)

    return SuccessResponse(
        success=True,
        message="강의 영상이 성공적으로 생성되었습니다",
        data=lecture
    )

@router.patch(
    "/{course_id}/chapters/{chapter_id}/lectures/{lecture_id}",
    response_model=SuccessResponse[LectureResponse],
    summary="강의 영상 수정",
    description="강의 영상 정보를 수정합니다. 제공된 필드만 수정됩니다.",
    responses=ADMIN_COURSE_MANAGEMENT_RESPONSES
)
async def update_lecture(
    course_id: int,
    chapter_id: int,
    lecture_id: int,
    data: LectureUpdate,
    current_admin: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db)
):
    service = AdminCourseService(db)
    lecture = await service.update_lecture(course_id, chapter_id, lecture_id, data)

    return SuccessResponse(
        success=True,
        message="강의 영상이 성공적으로 수정되었습니다",
        data=lecture
    )

@router.delete(
    "/{course_id}/chapters/{chapter_id}/lectures/{lecture_id}",
    response_model=MessageResponse,
    summary="강의 영상 삭제",
    description="강의 영상을 삭제합니다. 학습 진행 기록이 함께 삭제되고 강의 전체 시간이 업데이트됩니다.",
    responses=ADMIN_COURSE_MANAGEMENT_RESPONSES
)
async def delete_lecture(
    course_id: int,
    chapter_id: int,
    lecture_id: int,
    current_admin: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db)
):
    service = AdminCourseService(db)
    await service.delete_lecture(course_id, chapter_id, lecture_id)

    return MessageResponse(
        success=True,
        message="강의 영상이 성공적으로 삭제되었습니다"
    )

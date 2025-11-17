from fastapi import APIRouter, Depends, status, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession

from typing import List, Optional

from app.schemas.admin import (
    CourseManagementListParams, CourseManagementPaginatedResponse,
)
from app.schemas.common import MessageResponse, SuccessResponse, ImageUploadResponse, FileUploadResponse, FileDeleteRequest, FileListResponse
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

# ==================== 파일 업로드 ====================

@router.post(
    "/upload-thumbnail",
    response_model=SuccessResponse[ImageUploadResponse],
    status_code=status.HTTP_201_CREATED,
    summary="강의 썸네일 업로드",
    description="강의 썸네일 이미지를 업로드합니다. 업로드된 이미지 URL을 반환받아 강의 생성/수정 시 사용하세요.",
    responses=ADMIN_RESPONSES
)
async def upload_thumbnail(
    file: UploadFile = File(..., description="썸네일 이미지 파일 (JPEG, PNG, WebP)"),
    current_admin: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db)
):
    """강의 썸네일 업로드

    - 지원 형식: JPEG, PNG, WebP
    - 최대 크기: 10MB
    - 업로드된 파일은 /uploads/thumbnails/ 경로에 저장됩니다
    - 반환된 image_url을 CourseCreate의 thumbnail_url에 사용하세요
    """
    service = AdminCourseService(db)
    result = await service.upload_thumbnail(file)

    return SuccessResponse(
        success=True,
        message="썸네일이 성공적으로 업로드되었습니다",
        data=result
    )

@router.post(
    "/upload-instructor-image",
    response_model=SuccessResponse[ImageUploadResponse],
    status_code=status.HTTP_201_CREATED,
    summary="강사 이미지 업로드",
    description="강사 프로필 이미지를 업로드합니다. 업로드된 이미지 URL을 반환받아 강의 생성/수정 시 사용하세요.",
    responses=ADMIN_RESPONSES
)
async def upload_instructor_image(
    file: UploadFile = File(..., description="강사 이미지 파일 (JPEG, PNG, WebP)"),
    current_admin: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db)
):
    """강사 프로필 이미지 업로드

    - 지원 형식: JPEG, PNG, WebP
    - 최대 크기: 10MB
    - 업로드된 파일은 /uploads/instructors/ 경로에 저장됩니다
    - 반환된 image_url을 CourseCreate의 instructor_image에 사용하세요
    """
    service = AdminCourseService(db)
    result = await service.upload_instructor_image(file)

    return SuccessResponse(
        success=True,
        message="강사 이미지가 성공적으로 업로드되었습니다",
        data=result
    )

@router.post(
    "/upload-material",
    response_model=SuccessResponse[FileUploadResponse],
    status_code=status.HTTP_201_CREATED,
    summary="강의 자료 업로드",
    description="강의 자료 파일을 업로드합니다. 업로드된 파일 URL을 반환받아 강의 영상 생성/수정 시 사용하세요.",
    responses=ADMIN_RESPONSES
)
async def upload_material(
    file: UploadFile = File(..., description="강의 자료 파일 (PDF, ZIP, DOCX 등)"),
    current_admin: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db)
):
    """강의 자료 업로드

    - 지원 형식: PDF, ZIP, DOCX, PPTX, TXT 등
    - 최대 크기: 50MB
    - 업로드된 파일은 /uploads/materials/ 경로에 저장됩니다
    - 반환된 file_url을 LectureCreate의 material_url에 사용하세요
    """
    service = AdminCourseService(db)
    result = await service.upload_material(file)

    return SuccessResponse(
        success=True,
        message="강의 자료가 성공적으로 업로드되었습니다",
        data=result
    )

@router.get(
    "/files",
    response_model=SuccessResponse[FileListResponse],
    status_code=status.HTTP_200_OK,
    summary="업로드된 파일 목록 조회",
    description="관리자가 업로드한 강의 관련 파일(썸네일, 강사 이미지, 강의 자료) 목록을 조회합니다.",
    responses=ADMIN_RESPONSES
)
async def list_uploaded_files(
    file_type: Optional[str] = None,
    current_admin: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db)
):
    """업로드된 파일 목록 조회

    - file_type: 조회할 파일 타입 (thumbnails, instructors, materials)
    - file_type을 지정하지 않으면 모든 타입의 파일을 조회합니다
    - 최신 업로드 순으로 정렬됩니다
    - 파일명, URL, 크기, 생성일시 등의 정보를 포함합니다
    """
    service = AdminCourseService(db)
    result = await service.list_uploaded_files(file_type)

    return SuccessResponse(
        success=True,
        message="파일 목록 조회 성공",
        data=result
    )

@router.delete(
    "/files",
    response_model=MessageResponse,
    status_code=status.HTTP_200_OK,
    summary="업로드된 파일 삭제",
    description="업로드된 파일(썸네일, 강사 이미지, 강의 자료)을 삭제합니다.",
    responses=ADMIN_RESPONSES
)
async def delete_file(
    request: FileDeleteRequest,
    current_admin: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db)
):
    """업로드된 파일 삭제

    - 잘못 업로드한 파일이나 사용하지 않는 파일을 삭제합니다
    - 파일 URL을 제공하면 해당 파일이 서버에서 삭제됩니다
    - 이미 강의/챕터/강의에 연결된 파일을 삭제하면 연결이 끊어지므로 주의하세요
    """
    service = AdminCourseService(db)
    await service.delete_file(request.file_url)

    return MessageResponse(
        success=True,
        message="파일이 성공적으로 삭제되었습니다"
    )

# ==================== 강의 관리 ====================

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
    """관리자용 강의 목록 조회

    - 수강생 수, 매출, 평균 진행률, 완료율 등의 통계 정보 포함
    - 카테고리, 난이도, 공개 여부, 키워드로 필터링 가능
    """
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
    """관리자용 강의 상세 조회

    - 강의의 모든 상세 정보를 조회합니다
    - 비공개 강의도 조회 가능합니다
    - 수강 인원 수가 포함됩니다
    """
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
    """새로운 강의 생성

    - 강의는 기본적으로 비공개(is_published=False) 상태로 생성됩니다
    - 챕터와 강의 영상을 추가한 후 공개 API를 사용하여 공개할 수 있습니다
    """
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
    """강의 공개

    - is_published를 True로 변경합니다
    - 공개된 강의는 일반 사용자가 강의 목록에서 확인할 수 있습니다
    """
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
    """강의 비공개

    - is_published를 False로 변경합니다
    - 비공개된 강의는 일반 사용자 강의 목록에서 숨겨집니다
    - 이미 수강 중인 사용자는 계속 수강할 수 있습니다
    """
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
    """강의 정보 수정

    - 제공된 필드만 수정됩니다 (PATCH 방식)
    - is_published 필드를 직접 수정하는 것보다 공개/비공개 API 사용을 권장합니다
    """
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
    """강의 삭제

    **주의**: 강의 삭제 시 다음 데이터가 함께 삭제됩니다:
    - 모든 챕터 및 강의 영상
    - 수강 등록 정보
    - 학습 진행 기록
    - 결제 정보 (외래 키 제약에 따라)
    """
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
    """챕터 목록 조회

    - 특정 강의의 모든 챕터를 조회합니다
    - order_number 순서로 정렬되어 반환됩니다
    - 각 챕터의 총 재생 시간도 함께 반환됩니다
    """
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
    """챕터 생성

    - order_number를 사용하여 챕터 순서를 지정합니다
    - 동일한 order_number를 가진 챕터가 있어도 생성됩니다 (순서 조정은 수정 API 사용)
    """
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
    """챕터 수정

    - 제공된 필드만 수정됩니다 (PATCH 방식)
    - order_number를 변경하여 챕터 순서를 조정할 수 있습니다
    """
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
    """챕터 삭제

    **주의**: 챕터 삭제 시 다음 데이터가 함께 삭제됩니다:
    - 챕터에 포함된 모든 강의 영상
    - 학습 진행 기록
    - 강의 전체 재생 시간이 자동으로 업데이트됩니다
    """
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
    """강의 영상 목록 조회

    - 특정 챕터의 모든 강의 영상을 조회합니다
    - order_number 순서로 정렬되어 반환됩니다
    - 각 영상의 제목, 설명, URL, 재생 시간 등의 정보가 포함됩니다
    """
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
    """강의 영상 생성

    - video_type: 'vod' 또는 'youtube'
    - duration_seconds: 재생 시간(초)을 입력하면 강의 전체 시간이 자동으로 업데이트됩니다
    - order_number: 챕터 내 강의 순서
    - material_url: 강의 자료 다운로드 링크 (선택)
    """
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
    """강의 영상 수정

    - 제공된 필드만 수정됩니다 (PATCH 방식)
    - duration_seconds를 변경하면 강의 전체 시간이 자동으로 업데이트됩니다
    - order_number를 변경하여 강의 순서를 조정할 수 있습니다
    """
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
    """강의 영상 삭제

    **주의**: 강의 영상 삭제 시 다음 작업이 수행됩니다:
    - 해당 영상의 학습 진행 기록이 삭제됩니다 (CASCADE)
    - 강의 전체 재생 시간이 자동으로 업데이트됩니다
    """
    service = AdminCourseService(db)
    await service.delete_lecture(course_id, chapter_id, lecture_id)

    return MessageResponse(
        success=True,
        message="강의 영상이 성공적으로 삭제되었습니다"
    )

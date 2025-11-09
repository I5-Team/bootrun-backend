from fastapi import APIRouter, Depends
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.common import PaginatedResponse
from app.schemas.course import (
    CourseResponse, CourseDetailResponse,
    CourseListParams, 
    ChapterWithLectures,
    LectureResponse, CourseMetadataResponse
)
from app.exceptions.responses import (
    COURSE_LIST_RESPONSES,
    COURSE_DETAIL_RESPONSES,
    CHAPTER_DETAIL_RESPONSES,      
    LECTURE_LIST_RESPONSES,          
    LECTURE_DETAIL_RESPONSES,        
)
from app.core.dependencies import get_current_user_optional, get_current_user, get_db
from app.models.user import User
from app.services.course_service import CourseService

router = APIRouter(prefix="/courses", tags=["강의"])

@router.get(
    "/metadata",
    response_model=CourseMetadataResponse,
    summary="강의 필터링 메타데이터 조회",
    responses={200: {"description": "성공"}, **COURSE_LIST_RESPONSES}
)
async def get_course_metadata():
    return CourseService.get_course_metadata()

@router.get(
    "",
    response_model=PaginatedResponse[CourseResponse],
    summary="강의 목록 조회",
    responses={200: {"description": "성공"}, **COURSE_LIST_RESPONSES}
)
async def get_courses(
    params: CourseListParams = Depends(),
    db: AsyncSession = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional)
):
    service = CourseService(db)
    user_id = current_user.id if current_user else None
    result = await service.get_courses(params, user_id)
    return PaginatedResponse[CourseResponse](
        total=result.total,
        page=result.page,
        page_size=result.page_size,
        total_pages=result.total_pages,
        items=result.items
    )

@router.get(
    "/{course_id}",
    response_model=CourseDetailResponse,
    summary="강의 상세 조회",
    responses={200: {"description": "성공"}, **COURSE_DETAIL_RESPONSES}
)
async def get_course(
    course_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional)
):
    service = CourseService(db)
    user_id = current_user.id if current_user else None
    return await service.get_course_by_id(course_id, user_id)

@router.get(
    "/{course_id}/chapters",
    response_model=List[ChapterWithLectures],
    summary="챕터 목록 조회",
    responses={200: {"description": "성공"}, **CHAPTER_DETAIL_RESPONSES}
)
async def get_chapters(
    course_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional)
):
    service = CourseService(db)
    course_detail = await service.get_course_by_id(course_id, None)
    return course_detail.chapters

@router.get(
    "/{course_id}/chapters/{chapter_id}",
    response_model=ChapterWithLectures,
    summary="챕터 상세 조회",
    responses={200: {"description": "성공"}, **COURSE_DETAIL_RESPONSES}
)
async def get_chapter(
    course_id: int,
    chapter_id: int,
    db: AsyncSession = Depends(get_db)
):
    service = CourseService(db)
    return await service.get_chapter_by_id(course_id, chapter_id)

@router.get(
    "/{course_id}/chapters/{chapter_id}/lectures",
    response_model=List[LectureResponse],
    summary="강의 영상 목록 조회",
    responses={200: {"description": "성공"}, **LECTURE_LIST_RESPONSES}
)
async def get_lectures(
    course_id: int,
    chapter_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional)
):
    service = CourseService(db)
    return await service.get_lectures_by_chapter(course_id, chapter_id)

@router.get(
    "/{course_id}/chapters/{chapter_id}/lectures/{lecture_id}",
    response_model=LectureResponse,
    summary="강의 영상 상세 조회",
    responses={200: {"description": "성공"}, **LECTURE_DETAIL_RESPONSES}
)
async def get_lecture(
    course_id: int,
    chapter_id: int,
    lecture_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    service = CourseService(db)
    return await service.get_lecture_by_id(
        course_id, 
        chapter_id, 
        lecture_id, 
        current_user.id
    )
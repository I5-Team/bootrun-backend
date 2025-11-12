from fastapi import APIRouter, Depends
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.common import PaginatedResponse, SuccessResponse
from app.schemas.course import (
    CourseResponse, CourseDetailResponse,
    CourseListParams, 
    ChapterWithLectures,
    LectureResponse
)
from app.exceptions.responses import (
    COURSE_LIST_RESPONSES,
    COURSE_DETAIL_RESPONSES,
    CHAPTER_DETAIL_RESPONSES,      
    LECTURE_LIST_RESPONSES,                 
)
from app.core.dependencies import get_current_user_optional, get_current_user, get_db
from app.models.user import User
from app.services.course_service import CourseService

router = APIRouter(prefix="/courses", tags=["강의"])

@router.get(
    "",
    response_model=PaginatedResponse[CourseResponse],
    summary="강의 목록 조회",
    operation_id="user_get_courses",
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
    response_model=SuccessResponse[CourseDetailResponse],
    summary="강의 상세 조회",
    operation_id="user_get_course",
    responses={200: {"description": "성공"}, **COURSE_DETAIL_RESPONSES}
)
async def get_course(
    course_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional)
):
    service = CourseService(db)
    user_id = current_user.id if current_user else None
    course = await service.get_course_by_id(course_id, user_id)
    return SuccessResponse(
        success=True,
        message="강의 상세 조회 성공",
        data=course
    )

@router.get(
    "/{course_id}/chapters",
    response_model=SuccessResponse[List[ChapterWithLectures]],
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
    return SuccessResponse(
        success=True,
        message="챕터 목록 조회 성공",
        data=course_detail.chapters
    )

@router.get(
    "/{course_id}/chapters/{chapter_id}",
    response_model=SuccessResponse[ChapterWithLectures],
    summary="챕터 상세 조회",
    responses={200: {"description": "성공"}, **COURSE_DETAIL_RESPONSES}
)
async def get_chapter(
    course_id: int,
    chapter_id: int,
    db: AsyncSession = Depends(get_db)
):
    service = CourseService(db)
    chapter = await service.get_chapter_by_id(course_id, chapter_id)
    return SuccessResponse(
        success=True,
        message="챕터 상세 조회 성공",
        data=chapter
    )

@router.get(
    "/{course_id}/chapters/{chapter_id}/lectures",
    response_model=SuccessResponse[List[LectureResponse]],
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
    lectures = await service.get_lectures_by_chapter(course_id, chapter_id)
    return SuccessResponse(
        success=True,
        message="강의 영상 목록 조회 성공",
        data=lectures
    )

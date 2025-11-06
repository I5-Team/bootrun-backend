"""
강의 API 라우터
강의 목록 조회, 상세 조회, 챕터/강의 영상 조회 등을 처리합니다.
"""

from fastapi import APIRouter, Depends, status
from typing import List
from schemas.common import MessageResponse, PaginatedResponse
from schemas.course import (
    CourseResponse, CourseDetailResponse,
    CourseListParams, 
    ChapterWithLectures,
    LectureResponse, CourseMetadataResponse
)
from exceptions import (
    READ_RESPONSES,
    COURSE_LIST_RESPONSES,
    COURSE_DETAIL_RESPONSES,
)

router = APIRouter(prefix="/courses", tags=["강의"])


# ============= 강의 검색 API =============

@router.get(
    "/metadata",
    response_model=CourseMetadataResponse,
    summary="강의 필터링 메타데이터 조회",
    description="강의 검색 및 필터링에 사용할 수 있는 카테고리, 난이도, 가격 유형 등의 메타데이터를 조회합니다.",
    responses={
        200: {"description": "메타데이터 조회 성공"},
        **COURSE_LIST_RESPONSES
    }
)
async def get_course_metadata():
    """
    # 강의 메타데이터 조회 API
    
    강의 목록 필터링에 사용할 메타데이터를 반환합니다.
    
    ## 응답
    - 200: 메타데이터 조회 성공
    
    ## 반환 정보
    - **categories**: 카테고리 목록 (프론트엔드, 백엔드, 데이터분석, AI, 디자인, 기타)
    - **course_types**: 강의 유형 (VOD, 부스트캠프, KDC)
    - **difficulties**: 난이도 (beginner, intermediate, advanced)
    - **price_types**: 가격 유형 (free, paid, national_support)
    
    ## 사용 사례
    - 강의 목록 페이지의 필터 UI 구성
    - 검색 필터 옵션 제공
    """
    pass


# ============= 강의 API =============

@router.get(
    "",
    response_model=PaginatedResponse[CourseResponse],
    summary="강의 목록 조회",
    description="전체 강의 목록을 조회합니다. 카테고리, 난이도, 가격 유형 등으로 필터링할 수 있습니다.",
    responses={
        200: {"description": "강의 목록 조회 성공"},
        **COURSE_LIST_RESPONSES
    }
)
async def get_courses(params: CourseListParams = Depends()):
    """
    # 강의 목록 조회 API
    
    조건에 따라 강의 목록을 조회합니다.
    
    ## 쿼리 파라미터
    - **category_type**: 카테고리 필터 (frontend/backend/data_analysis/ai/design/other)
    - **difficulty**: 난이도 필터 (beginner/intermediate/advanced)
    - **price_type**: 가격 유형 필터 (free/paid/national_support)
    - **keyword**: 검색 키워드 (강의명, 설명에서 검색)
    - **is_published**: 공개 여부 (기본값: true, 관리자는 false 가능)
    - **page**: 페이지 번호 (기본값: 1)
    - **page_size**: 페이지 크기 (기본값: 20, 최대: 100)
    
    ## 응답
    - 200: 강의 목록 조회 성공
    - 422: 입력값 유효성 검사 실패
    
    ## 정렬
    - 기본: 최신 생성순
    
    ## 예시
    - 프론트엔드 초급 강의: `?category_type=frontend&difficulty=beginner`
    - 무료 강의: `?price_type=free`
    - 키워드 검색: `?keyword=React`
    """
    pass


@router.get(
    "/{course_id}",
    response_model=CourseDetailResponse,
    summary="강의 상세 조회",
    description="특정 강의의 상세 정보를 조회합니다. 챕터와 강의 영상 목록이 포함됩니다.",
    responses={
        200: {"description": "강의 상세 조회 성공"},
        **COURSE_DETAIL_RESPONSES
    }
)
async def get_course(course_id: int):
    """
    # 강의 상세 조회 API
    
    강의의 상세 정보와 커리큘럼을 조회합니다.
    
    ## 경로 파라미터
    - **course_id**: 강의 ID
    
    ## 응답
    - 200: 강의 정보 조회 성공
    - 404: 강의를 찾을 수 없음
    
    ## 반환 정보
    - 기본 정보: 제목, 설명, 강사, 난이도, 가격 등
    - 커리큘럼: 전체 챕터 및 강의 영상 목록
    - 수강 정보: 수강 여부, 진행률 (로그인 시)
    - FAQ: 자주 묻는 질문
    
    ## 참고
    - 로그인한 사용자의 경우 수강 여부와 진행률 정보가 포함됩니다
    - 비공개 강의는 관리자만 조회 가능합니다
    """
    pass


@router.get(
    "/{course_id}/chapters",
    response_model=List[ChapterWithLectures],
    summary="챕터 목록 조회",
    description="특정 강의의 전체 챕터 목록을 조회합니다.",
    responses={
        200: {"description": "챕터 목록 조회 성공"},
        **COURSE_DETAIL_RESPONSES
    }
)
async def get_chapters(course_id: int):
    """
    # 챕터 목록 조회 API
    
    강의의 전체 챕터와 각 챕터의 강의 영상을 조회합니다.
    
    ## 경로 파라미터
    - **course_id**: 강의 ID
    
    ## 응답
    - 200: 챕터 목록 조회 성공
    - 404: 강의를 찾을 수 없음
    
    ## 반환 정보
    - 챕터 정보: 제목, 설명, 순서, 총 시간
    - 강의 영상 목록: 각 챕터에 포함된 강의 영상 정보
    - 학습 진행 상태 (로그인 시): 완료 여부, 마지막 시청 위치 등
    """
    pass


@router.get(
    "/{course_id}/chapters/{chapter_id}",
    response_model=ChapterWithLectures,
    summary="챕터 상세 조회",
    description="특정 챕터의 상세 정보와 강의 영상 목록을 조회합니다.",
    responses={
        200: {"description": "챕터 상세 조회 성공"},
        **COURSE_DETAIL_RESPONSES,
        404: {
            "description": "강의 또는 챕터를 찾을 수 없음",
            "content": {
                "application/json": {
                    "examples": {
                        "course_not_found": {
                            "value": {
                                "error": "COURSE_NOT_FOUND",
                                "detail": "강의를 찾을 수 없습니다"
                            }
                        },
                        "chapter_not_found": {
                            "value": {
                                "error": "CHAPTER_NOT_FOUND",
                                "detail": "챕터를 찾을 수 없습니다"
                            }
                        }
                    }
                }
            }
        }
    }
)
async def get_chapter(course_id: int, chapter_id: int):
    """
    # 챕터 상세 조회 API
    
    특정 챕터의 상세 정보를 조회합니다.
    
    ## 경로 파라미터
    - **course_id**: 강의 ID
    - **chapter_id**: 챕터 ID
    
    ## 응답
    - 200: 챕터 정보 조회 성공
    - 404: 강의 또는 챕터를 찾을 수 없음
    
    ## 반환 정보
    - 챕터 기본 정보
    - 챕터에 포함된 모든 강의 영상
    - 각 강의의 학습 진행 상태 (로그인 시)
    """
    pass


@router.get(
    "/{course_id}/chapters/{chapter_id}/lectures",
    response_model=List[LectureResponse],
    summary="강의 영상 목록 조회",
    description="특정 챕터의 강의 영상 목록을 조회합니다.",
    responses={
        200: {"description": "강의 영상 목록 조회 성공"},
        **COURSE_DETAIL_RESPONSES,
        404: {
            "description": "강의 또는 챕터를 찾을 수 없음",
            "content": {
                "application/json": {
                    "examples": {
                        "course_not_found": {
                            "value": {
                                "error": "COURSE_NOT_FOUND",
                                "detail": "강의를 찾을 수 없습니다"
                            }
                        },
                        "chapter_not_found": {
                            "value": {
                                "error": "CHAPTER_NOT_FOUND",
                                "detail": "챕터를 찾을 수 없습니다"
                            }
                        }
                    }
                }
            }
        }
    }
)
async def get_lectures(course_id: int, chapter_id: int):
    """
    # 강의 영상 목록 조회 API
    
    챕터에 속한 강의 영상들을 조회합니다.
    
    ## 경로 파라미터
    - **course_id**: 강의 ID
    - **chapter_id**: 챕터 ID
    
    ## 응답
    - 200: 강의 영상 목록 조회 성공
    - 404: 강의 또는 챕터를 찾을 수 없음
    
    ## 반환 정보
    - 강의 영상 기본 정보: 제목, 설명, 재생 시간 등
    - 동영상 정보: URL, 타입 (VOD/유튜브)
    - 학습 진행 정보 (로그인 시): 완료 여부, 시청 시간, 마지막 위치
    """
    pass


@router.get(
    "/{course_id}/chapters/{chapter_id}/lectures/{lecture_id}",
    response_model=LectureResponse,
    summary="강의 영상 상세 조회",
    description="특정 강의 영상의 상세 정보를 조회합니다.",
    responses={
        200: {"description": "강의 영상 상세 조회 성공"},
        **COURSE_DETAIL_RESPONSES,
        403: {
            "description": "수강 권한 없음",
            "content": {
                "application/json": {
                    "example": {
                        "error": "ENROLLMENT_REQUIRED",
                        "detail": "수강 등록이 필요합니다"
                    }
                }
            }
        },
        404: {
            "description": "강의, 챕터 또는 강의 영상을 찾을 수 없음",
            "content": {
                "application/json": {
                    "examples": {
                        "course_not_found": {
                            "value": {
                                "error": "COURSE_NOT_FOUND",
                                "detail": "강의를 찾을 수 없습니다"
                            }
                        },
                        "chapter_not_found": {
                            "value": {
                                "error": "CHAPTER_NOT_FOUND",
                                "detail": "챕터를 찾을 수 없습니다"
                            }
                        },
                        "lecture_not_found": {
                            "value": {
                                "error": "LECTURE_NOT_FOUND",
                                "detail": "강의 영상을 찾을 수 없습니다"
                            }
                        }
                    }
                }
            }
        },
        410: {
            "description": "수강 기간 만료",
            "content": {
                "application/json": {
                    "example": {
                        "error": "ENROLLMENT_EXPIRED",
                        "detail": "수강 기간이 만료되었습니다"
                    }
                }
            }
        }
    }
)
async def get_lecture(course_id: int, chapter_id: int, lecture_id: int):
    """
    # 강의 영상 상세 조회 API
    
    특정 강의 영상의 상세 정보를 조회합니다.
    
    ## 경로 파라미터
    - **course_id**: 강의 ID
    - **chapter_id**: 챕터 ID
    - **lecture_id**: 강의 영상 ID
    
    ## 응답
    - 200: 강의 영상 정보 조회 성공
    - 403: 수강 권한 없음
    - 404: 강의, 챕터 또는 강의 영상을 찾을 수 없음
    - 410: 수강 기간 만료
    
    ## 반환 정보
    - 강의 영상 상세 정보
    - 동영상 스트리밍 URL
    - 학습 진행 정보: 완료 여부, 시청 시간, 마지막 시청 위치
    
    ## 참고
    - 수강 등록된 사용자만 접근 가능합니다
    - 수강 기간이 만료된 경우 접근이 제한됩니다
    """
    pass
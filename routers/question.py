"""
학습 Q&A API 라우터
질문 작성, 답변 작성, 질문/답변 수정 및 삭제 등을 처리합니다.
"""

from fastapi import APIRouter, Depends, status
from typing import List
from schemas.course import (
    QuestionCreate, QuestionUpdate, QuestionResponse,
    QuestionDetailResponse, QuestionListParams,
    CommentCreate, CommentUpdate, CommentResponse
)
from schemas.common import MessageResponse, PaginatedResponse
from exceptions import (
    QNA_CREATE_RESPONSES,
    QNA_UPDATE_RESPONSES,
    COMMENT_CREATE_RESPONSES,
    AUTH_RESPONSES,
    READ_RESPONSES,
    MODIFY_RESPONSES,
)

router = APIRouter(prefix="/questions", tags=["학습 Q&A"])


@router.get(
    "",
    response_model=PaginatedResponse[QuestionResponse],
    summary="질문 목록 조회",
    description="학습 Q&A 게시판의 질문 목록을 조회합니다.",
    responses={
        200: {"description": "질문 목록 조회 성공"},
        **READ_RESPONSES
    }
)
async def get_questions(params: QuestionListParams = Depends()):
    """
    # 질문 목록 조회 API
    
    학습 Q&A 게시판의 질문 목록을 조회합니다.
    
    ## 쿼리 파라미터
    - **course_id**: 강의 ID 필터 (선택)
    - **is_answered**: 답변 여부 필터 (선택)
        - true: 답변 완료된 질문만
        - false: 답변 대기 중인 질문만
        - 미입력: 모든 질문
    - **keyword**: 검색 키워드 (제목, 내용에서 검색)
    - **page**: 페이지 번호 (기본값: 1)
    - **page_size**: 페이지 크기 (기본값: 20, 최대: 100)
    
    ## 응답
    - 200: 질문 목록 조회 성공
    - 422: 입력값 유효성 검사 실패
    
    ## 반환 정보
    - 질문 기본 정보
    - 작성자 정보
    - 조회수
    - 답변 완료 여부
    - 답변 개수
    """
    pass


@router.get(
    "/{question_id}",
    response_model=QuestionDetailResponse,
    summary="질문 상세 조회",
    description="특정 질문의 상세 정보와 답변을 조회합니다.",
    responses={
        200: {"description": "질문 상세 조회 성공"},
        **READ_RESPONSES
    }
)
async def get_question(question_id: int):
    """
    # 질문 상세 조회 API
    
    질문의 상세 정보와 모든 답변을 조회합니다.
    
    ## 경로 파라미터
    - **question_id**: 질문 ID
    
    ## 응답
    - 200: 질문 정보 조회 성공, 조회수 +1
    - 404: 질문을 찾을 수 없음
    
    ## 반환 정보
    - 질문 상세 정보
    - 모든 답변 및 대댓글
    - 강사 답변 여부 표시
    """
    pass


@router.post(
    "",
    response_model=QuestionResponse,
    status_code=status.HTTP_201_CREATED,
    summary="질문 작성",
    description="학습 Q&A 게시판에 질문을 작성합니다.",
    responses={
        201: {"description": "질문 작성 성공"},
        **QNA_CREATE_RESPONSES
    }
)
async def create_question(data: QuestionCreate):
    """
    # 질문 작성 API
    
    학습 Q&A 게시판에 질문을 작성합니다.
    
    ## 요청 본문
    - **course_id**: 강의 ID
    - **title**: 질문 제목 (1~200자)
    - **content**: 질문 내용 (1자 이상)
    
    ## 응답
    - 201: 질문 작성 성공
    - 401: 인증되지 않은 사용자
    - 403: 수강 중인 강의에만 질문 가능
    - 404: 강의를 찾을 수 없음
    
    ## 참고
    - 수강 등록된 강의에만 질문을 작성할 수 있습니다
    """
    pass


@router.patch(
    "/{question_id}",
    response_model=QuestionResponse,
    summary="질문 수정",
    description="작성한 질문을 수정합니다.",
    responses={
        200: {"description": "질문 수정 성공"},
        **QNA_UPDATE_RESPONSES
    }
)
async def update_question(question_id: int, data: QuestionUpdate):
    """
    # 질문 수정 API
    
    본인이 작성한 질문을 수정합니다.
    
    ## 경로 파라미터
    - **question_id**: 질문 ID
    
    ## 요청 본문
    - **title**: 질문 제목 (선택)
    - **content**: 질문 내용 (선택)
    
    ## 응답
    - 200: 질문 수정 성공
    - 401: 인증되지 않은 사용자
    - 403: 본인이 작성한 질문만 수정 가능
    - 404: 질문을 찾을 수 없음
    
    ## 참고
    - 제공된 필드만 업데이트됩니다
    """
    pass


@router.delete(
    "/{question_id}",
    response_model=MessageResponse,
    summary="질문 삭제",
    description="작성한 질문을 삭제합니다. (소프트 삭제)",
    responses={
        200: {"description": "질문 삭제 성공"},
        **QNA_UPDATE_RESPONSES
    }
)
async def delete_question(question_id: int):
    """
    # 질문 삭제 API
    
    본인이 작성한 질문을 삭제합니다.
    
    ## 경로 파라미터
    - **question_id**: 질문 ID
    
    ## 응답
    - 200: 질문 삭제 성공
    - 401: 인증되지 않은 사용자
    - 403: 본인이 작성한 질문 또는 관리자만 삭제 가능
    - 404: 질문을 찾을 수 없음
    
    ## 참고
    - 소프트 삭제로 처리됩니다 (실제로는 DB에 남음)
    - 삭제된 질문은 목록 및 상세에서 보이지 않습니다
    - 관리자는 모든 질문을 삭제할 수 있습니다
    """
    pass


@router.post(
    "/{question_id}/comments",
    response_model=CommentResponse,
    status_code=status.HTTP_201_CREATED,
    summary="답변 작성",
    description="질문에 답변(댓글)을 작성합니다. 관리자 또는 강사만 가능합니다.",
    responses={
        201: {"description": "답변 작성 성공"},
        **COMMENT_CREATE_RESPONSES
    }
)
async def create_comment(question_id: int, data: CommentCreate):
    """
    # 답변 작성 API
    
    질문에 답변을 작성합니다.
    
    ## 경로 파라미터
    - **question_id**: 질문 ID
    
    ## 요청 본문
    - **question_id**: 질문 ID (본문에도 포함)
    - **content**: 답변 내용 (1자 이상)
    - **parent_id**: 부모 댓글 ID (대댓글인 경우, 선택)
    
    ## 응답
    - 201: 답변 작성 성공
    - 401: 인증되지 않은 사용자
    - 403: 관리자 또는 강사만 답변 가능
    - 404: 질문을 찾을 수 없음
    
    ## 참고
    - 관리자 및 강사만 답변을 작성할 수 있습니다
    - parent_id를 지정하면 대댓글로 작성됩니다
    - 강사/관리자 답변은 is_instructor_answer로 표시됩니다
    """
    pass


@router.patch(
    "/{question_id}/comments/{comment_id}",
    response_model=CommentResponse,
    summary="답변 수정",
    description="작성한 답변을 수정합니다.",
    responses={
        200: {"description": "답변 수정 성공"},
        **MODIFY_RESPONSES
    }
)
async def update_comment(question_id: int, comment_id: int, data: CommentUpdate):
    """
    # 답변 수정 API
    
    본인이 작성한 답변을 수정합니다.
    
    ## 경로 파라미터
    - **question_id**: 질문 ID
    - **comment_id**: 답변 ID
    
    ## 요청 본문
    - **content**: 답변 내용
    
    ## 응답
    - 200: 답변 수정 성공
    - 401: 인증되지 않은 사용자
    - 403: 본인이 작성한 답변만 수정 가능
    - 404: 질문 또는 답변을 찾을 수 없음
    """
    pass


@router.delete(
    "/{question_id}/comments/{comment_id}",
    response_model=MessageResponse,
    summary="답변 삭제",
    description="작성한 답변을 삭제합니다. (소프트 삭제)",
    responses={
        200: {"description": "답변 삭제 성공"},
        **MODIFY_RESPONSES
    }
)
async def delete_comment(question_id: int, comment_id: int):
    """
    # 답변 삭제 API
    
    본인이 작성한 답변을 삭제합니다.
    
    ## 경로 파라미터
    - **question_id**: 질문 ID
    - **comment_id**: 답변 ID
    
    ## 응답
    - 200: 답변 삭제 성공
    - 401: 인증되지 않은 사용자
    - 403: 본인이 작성한 답변 또는 관리자만 삭제 가능
    - 404: 질문 또는 답변을 찾을 수 없음
    
    ## 참고
    - 소프트 삭제로 처리됩니다
    - 삭제된 답변은 보이지 않습니다
    - 답변 삭제 시 해당 답변의 대댓글도 함께 숨겨집니다
    """
    pass


@router.get(
    "/my/questions",
    response_model=PaginatedResponse[QuestionResponse],
    summary="내가 작성한 질문",
    description="현재 사용자가 작성한 질문 목록을 조회합니다.",
    responses={
        200: {"description": "내 질문 목록 조회 성공"},
        **AUTH_RESPONSES
    }
)
async def get_my_questions(page: int = 1, page_size: int = 20):
    """
    # 내가 작성한 질문 조회 API
    
    본인이 작성한 질문 목록을 조회합니다.
    
    ## 쿼리 파라미터
    - **page**: 페이지 번호 (기본값: 1)
    - **page_size**: 페이지 크기 (기본값: 20)
    
    ## 응답
    - 200: 질문 목록 조회 성공
    - 401: 인증되지 않은 사용자
    """
    pass


@router.get(
    "/my/comments",
    response_model=List[CommentResponse],
    summary="내가 작성한 답변",
    description="현재 사용자가 작성한 답변 목록을 조회합니다.",
    responses={
        200: {"description": "내 답변 목록 조회 성공"},
        **AUTH_RESPONSES
    }
)
async def get_my_comments(page: int = 1, page_size: int = 20):
    """
    # 내가 작성한 답변 조회 API
    
    본인이 작성한 답변 목록을 조회합니다.
    
    ## 쿼리 파라미터
    - **page**: 페이지 번호 (기본값: 1)
    - **page_size**: 페이지 크기 (기본값: 20)
    
    ## 응답
    - 200: 답변 목록 조회 성공
    - 401: 인증되지 않은 사용자
    
    ## 참고
    - 관리자 또는 강사만 답변을 작성할 수 있으므로, 
      일반 사용자는 빈 목록이 반환됩니다
    """
    pass
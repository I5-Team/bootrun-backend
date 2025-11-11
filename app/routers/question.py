from fastapi import APIRouter, Depends, status, Path, Query
from sqlalchemy.orm import Session

from app.schemas.course import (
    QuestionCreate, QuestionUpdate, QuestionResponse,
    QuestionDetailResponse, QuestionListParams,
    CommentCreate, CommentUpdate, CommentResponse
)
from app.schemas.common import MessageResponse, PaginatedResponse, SuccessResponse
from app.exceptions.responses import (
    QNA_CREATE_RESPONSES,
    QNA_UPDATE_RESPONSES,
    COMMENT_CREATE_RESPONSES,
    AUTH_PERMISSION_RESPONSES,
    READ_RESPONSES,
)
from app.core.dependencies import (
    get_current_user,
    get_current_admin,
    get_current_instructor,
    verify_resource_owner
)
from app.core.database import get_db
from app.models.user import User

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
async def get_questions(
    params: QuestionListParams = Depends(),
    db: Session = Depends(get_db)
):
    # TODO: 서비스 로직 구현
    pass

@router.get(
    "/{question_id}",
    response_model=SuccessResponse[QuestionDetailResponse],
    summary="질문 상세 조회",
    description="특정 질문의 상세 정보와 답변을 조회합니다.",
    responses={
        200: {"description": "질문 상세 조회 성공"},
        **READ_RESPONSES
    }
)
async def get_question(
    question_id: int = Path(..., gt=0, description="질문 ID"),
    db: Session = Depends(get_db)
):
    # TODO: 서비스 로직 구현
    # 조회수 증가 로직 포함
    pass

@router.post(
    "",
    response_model=SuccessResponse[QuestionResponse],
    status_code=status.HTTP_201_CREATED,
    summary="질문 작성",
    description="학습 Q&A 게시판에 질문을 작성합니다.",
    responses={
        201: {"description": "질문 작성 성공"},
        **QNA_CREATE_RESPONSES
    }
)
async def create_question(
    data: QuestionCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # TODO: 서비스 로직 구현
    # 수강 등록 확인 로직 포함
    pass

@router.patch(
    "/{question_id}",
    response_model=SuccessResponse[QuestionResponse],
    summary="질문 수정",
    description="작성한 질문을 수정합니다.",
    responses={
        200: {"description": "질문 수정 성공"},
        **QNA_UPDATE_RESPONSES
    }
)
async def update_question(
    question_id: int = Path(..., gt=0, description="질문 ID"),
    data: QuestionUpdate = ...,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # TODO: 서비스 로직 구현
    # verify_resource_owner 사용하여 소유권 확인
    pass

@router.delete(
    "/{question_id}",
    response_model=MessageResponse,
    summary="질문 삭제",
    description="작성한 질문을 삭제합니다. (소프트 삭제)",
    responses={
        200: {"description": "질문 삭제 성공"},
        **AUTH_PERMISSION_RESPONSES
    }
)
async def delete_question(
    question_id: int = Path(..., gt=0, description="질문 ID"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # TODO: 서비스 로직 구현
    # verify_resource_owner 사용하여 소유권 확인 (관리자는 예외)
    pass

@router.post(
    "/{question_id}/comments",
    response_model=SuccessResponse[CommentResponse],
    status_code=status.HTTP_201_CREATED,
    summary="답변 작성",
    description="질문에 답변(댓글)을 작성합니다. 관리자 또는 강사만 가능합니다.",
    responses={
        201: {"description": "답변 작성 성공"},
        **COMMENT_CREATE_RESPONSES
    }
)
async def create_comment(
    question_id: int = Path(..., gt=0, description="질문 ID"),
    data: CommentCreate = ...,
    instructor: User = Depends(get_current_instructor),
    db: Session = Depends(get_db)
):
    # TODO: 서비스 로직 구현
    pass

@router.patch(
    "/{question_id}/comments/{comment_id}",
    response_model=SuccessResponse[CommentResponse],
    summary="답변 수정",
    description="작성한 답변을 수정합니다.",
    responses={
        200: {"description": "답변 수정 성공"},
        **AUTH_PERMISSION_RESPONSES
    }
)
async def update_comment(
    question_id: int = Path(..., gt=0, description="질문 ID"),
    comment_id: int = Path(..., gt=0, description="답변 ID"),
    data: CommentUpdate = ...,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # TODO: 서비스 로직 구현
    # verify_resource_owner 사용하여 소유권 확인
    pass

@router.delete(
    "/{question_id}/comments/{comment_id}",
    response_model=MessageResponse,
    summary="답변 삭제",
    description="작성한 답변을 삭제합니다. (소프트 삭제)",
    responses={
        200: {"description": "답변 삭제 성공"},
        **AUTH_PERMISSION_RESPONSES
    }
)
async def delete_comment(
    question_id: int = Path(..., gt=0, description="질문 ID"),
    comment_id: int = Path(..., gt=0, description="답변 ID"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # TODO: 서비스 로직 구현
    # verify_resource_owner 사용하여 소유권 확인 (관리자는 예외)
    pass

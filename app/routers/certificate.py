from fastapi import APIRouter, status, Depends
from typing import List
from app.schemas.certificate import (
    CertificateCreate, CertificateResponse, CertificateListResponse,
    CertificateGenerationResponse, CertificateVerifyRequest,
    CertificateVerifyResponse, CompletionCheckRequest, CompletionCheckResponse
)
from app.schemas.common import SuccessResponse
from app.exceptions.responses import (
    CERTIFICATE_ISSUE_RESPONSES,
    CERTIFICATE_VERIFY_RESPONSES,
    CERTIFICATE_GENERATE_RESPONSES,
    AUTH_RESPONSES,
    READ_RESPONSES,
)
from app.core.dependencies import get_current_user, get_current_admin
from app.models.user import User

router = APIRouter(prefix="/certificates", tags=["수료증"])

@router.post(
    "",
    response_model=SuccessResponse[CertificateResponse],
    status_code=status.HTTP_201_CREATED,
    summary="수료증 발급",
    description="수료 조건을 만족한 강의의 수료증을 발급합니다.",
    responses={
        201: {"description": "수료증 발급 성공"},
        **CERTIFICATE_ISSUE_RESPONSES
    }
)
async def issue_certificate(
    data: CertificateCreate,
    current_user: User = Depends(get_current_user)
):
    pass

@router.get(
    "/my",
    response_model=SuccessResponse[List[CertificateListResponse]],
    summary="내 수료증 목록",
    description="사용자가 발급받은 수료증 목록을 조회합니다.",
    responses={
        200: {"description": "수료증 목록 조회 성공"},
        **AUTH_RESPONSES
    }
)
async def get_my_certificates(current_user: User = Depends(get_current_user)):
    pass

@router.get(
    "/{certificate_id}",
    response_model=SuccessResponse[CertificateResponse],
    summary="수료증 상세 조회",
    description="특정 수료증의 상세 정보를 조회합니다.",
    responses={
        200: {"description": "수료증 조회 성공"},
        **AUTH_RESPONSES,
        **READ_RESPONSES
    }
)
async def get_certificate(
    certificate_id: int,
    current_user: User = Depends(get_current_user)
):
    pass

@router.post(
    "/{certificate_id}/pdf",
    response_model=SuccessResponse[CertificateGenerationResponse],
    summary="수료증 PDF 생성",
    description="수료증 PDF 파일을 생성하고 다운로드 URL을 반환합니다.",
    responses={
        200: {"description": "PDF 생성 성공"},
        **CERTIFICATE_GENERATE_RESPONSES
    }
)
async def generate_certificate_pdf(
    certificate_id: int,
    current_user: User = Depends(get_current_user)
):
    pass

@router.delete(
    "/{certificate_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="수료증 삭제",
    description="수료증을 삭제합니다. 관리자만 가능합니다.",
    responses={
        204: {"description": "수료증 삭제 완료"},
        **AUTH_RESPONSES,
        **READ_RESPONSES
    }
)
async def delete_certificate(
    certificate_id: int,
    admin: User = Depends(get_current_admin)
):
    pass

@router.post(
    "/check-eligibility",
    response_model=SuccessResponse[CompletionCheckResponse],
    summary="수료 조건 확인",
    description="수강 중인 강의의 수료 가능 여부를 확인합니다.",
    responses={
        200: {"description": "수료 조건 확인 완료"},
        **AUTH_RESPONSES
    }
)
async def check_completion_eligibility(
    data: CompletionCheckRequest,
    current_user: User = Depends(get_current_user)
):
    pass

@router.post(
    "/verify",
    response_model=SuccessResponse[CertificateVerifyResponse],
    summary="수료증 진위 확인",
    description="수료증 번호로 수료증의 진위를 확인합니다. 인증 불필요(공개 API).",
    responses={
        200: {"description": "진위 확인 완료"},
        **CERTIFICATE_VERIFY_RESPONSES
    }
)
async def verify_certificate(data: CertificateVerifyRequest):
    pass
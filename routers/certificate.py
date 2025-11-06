"""
수료증 API 라우터  
수료증 발급, 조회, PDF 생성, 진위 확인 등을 처리합니다.
"""

from fastapi import APIRouter, status
from typing import List
from schemas.certificate import (
    CertificateCreate, CertificateResponse, CertificateListResponse,
    CertificateGenerationResponse, CertificateVerifyRequest,
    CertificateVerifyResponse, CompletionCheckRequest, CompletionCheckResponse
)
from exceptions import (
    CERTIFICATE_ISSUE_RESPONSES,
    CERTIFICATE_VERIFY_RESPONSES,
    CERTIFICATE_GENERATE_RESPONSES,
    AUTH_RESPONSES,
    READ_RESPONSES,
)

router = APIRouter(prefix="/certificates", tags=["수료증"])


@router.post(
    "",
    response_model=CertificateResponse,
    status_code=status.HTTP_201_CREATED,
    summary="수료증 발급",
    description="수료 조건을 만족한 강의의 수료증을 발급합니다.",
    responses={
        201: {"description": "수료증 발급 성공"},
        **CERTIFICATE_ISSUE_RESPONSES
    }
)
async def issue_certificate(data: CertificateCreate):
    """
    # 수료증 발급 API
    
    강의 수료 시 수료증을 발급합니다.
    
    ## 요청 본문
    - **enrollment_id**: 수강 등록 ID
    
    ## 응답
    - 201: 수료증 발급 성공
    - 400: 수료 조건 미충족
    - 401: 인증되지 않은 사용자
    - 404: 수강 정보를 찾을 수 없음
    
    ## 수료 조건
    - 진도율 100% 완료
    - 모든 미션 통과 (중간/기말)
    - 수강 기간 내
    
    ## 참고
    - 수료증 번호는 자동 생성됩니다 (WNIV-YYYY-NNNNNN)
    - PDF는 별도 API로 생성합니다
    """
    pass


@router.get(
    "/my",
    response_model=List[CertificateListResponse],
    summary="내 수료증 목록",
    description="사용자가 발급받은 수료증 목록을 조회합니다.",
    responses={
        200: {"description": "수료증 목록 조회 성공"},
        **AUTH_RESPONSES
    }
)
async def get_my_certificates():
    """
    # 내 수료증 목록 API
    
    발급받은 수료증 목록을 조회합니다.
    
    ## 응답
    - 200: 수료증 목록 조회 성공
    - 401: 인증되지 않은 사용자
    
    ## 반환 정보
    - 수료증 기본 정보
    - 강의 정보
    - 발급일
    - PDF 다운로드 URL
    """
    pass


@router.get(
    "/{certificate_id}",
    response_model=CertificateResponse,
    summary="수료증 상세 조회",
    description="특정 수료증의 상세 정보를 조회합니다.",
    responses={
        200: {"description": "수료증 조회 성공"},
        **AUTH_RESPONSES,
        **READ_RESPONSES
    }
)
async def get_certificate(certificate_id: int):
    """
    # 수료증 상세 조회 API
    
    수료증의 상세 정보를 조회합니다.
    
    ## 경로 파라미터
    - **certificate_id**: 수료증 ID
    
    ## 응답
    - 200: 수료증 정보 조회 성공
    - 401: 인증되지 않은 사용자
    - 403: 다른 사용자의 수료증은 조회 불가
    - 404: 수료증을 찾을 수 없음
    """
    pass


@router.post(
    "/{certificate_id}/pdf",
    response_model=CertificateGenerationResponse,
    summary="수료증 PDF 생성",
    description="수료증 PDF 파일을 생성하고 다운로드 URL을 반환합니다.",
    responses={
        200: {"description": "PDF 생성 성공"},
        **CERTIFICATE_GENERATE_RESPONSES
    }
)
async def generate_certificate_pdf(certificate_id: int):
    """
    # 수료증 PDF 생성 API
    
    수료증을 PDF 형식으로 생성합니다.
    
    ## 경로 파라미터
    - **certificate_id**: 수료증 ID
    
    ## 응답
    - 200: PDF 생성 성공, 다운로드 URL 반환
    - 400: PDF 생성 실패
    - 401: 인증되지 않은 사용자
    - 404: 수료증을 찾을 수 없음
    
    ## PDF 내용
    - 사용자 이름
    - 강의명
    - 수료일
    - 수료증 번호
    - 서명 및 직인
    """
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
async def delete_certificate(certificate_id: int):
    """
    # 수료증 삭제 API
    
    수료증을 삭제합니다.
    
    ## 경로 파라미터
    - **certificate_id**: 수료증 ID
    
    ## 응답
    - 204: 수료증 삭제 성공
    - 401: 인증되지 않은 사용자
    - 403: 관리자만 삭제 가능
    - 404: 수료증을 찾을 수 없음
    """
    pass


@router.post(
    "/check-eligibility",
    response_model=CompletionCheckResponse,
    summary="수료 조건 확인",
    description="수강 중인 강의의 수료 가능 여부를 확인합니다.",
    responses={
        200: {"description": "수료 조건 확인 완료"},
        **AUTH_RESPONSES
    }
)
async def check_completion_eligibility(data: CompletionCheckRequest):
    """
    # 수료 조건 확인 API
    
    수료 가능 여부를 확인합니다.
    
    ## 요청 본문
    - **enrollment_id**: 수강 등록 ID
    
    ## 응답
    - 200: 수료 조건 확인 완료
    - 401: 인증되지 않은 사용자
    - 404: 수강 정보를 찾을 수 없음
    
    ## 반환 정보
    - **is_eligible**: 수료 가능 여부
    - **message**: 수료 가능/불가 사유
    - **requirements**: 수료 조건 상세
        - progress_rate: 현재 진도율
        - lectures_completed: 완료한 강의 수
        - missions_completed: 미션 완료 여부
        - midterm_passed: 중간 미션 통과 여부
        - final_passed: 기말 미션 통과 여부
    """
    pass


@router.post(
    "/verify",
    response_model=CertificateVerifyResponse,
    summary="수료증 진위 확인",
    description="수료증 번호로 수료증의 진위를 확인합니다. 인증 불필요(공개 API).",
    responses={
        200: {"description": "진위 확인 완료"},
        **CERTIFICATE_VERIFY_RESPONSES
    }
)
async def verify_certificate(data: CertificateVerifyRequest):
    """
    # 수료증 진위 확인 API
    
    수료증 번호로 진위를 확인합니다.
    
    ## 요청 본문
    - **certificate_number**: 수료증 번호 (형식: WNIV-YYYY-NNNNNN)
    
    ## 응답
    - 200: 진위 확인 완료
    - 404: 유효하지 않은 수료증 번호
    
    ## 반환 정보
    - **is_valid**: 유효 여부
    - **message**: 결과 메시지
    - **certificate**: 수료증 정보 (유효한 경우)
        - 수료자 이름
        - 강의명
        - 카테고리
        - 발급일
    
    ## 참고
    - 이 API는 인증이 필요하지 않습니다 (공개 API)
    - 기업 등에서 수료증 진위 확인에 사용됩니다
    """
    pass
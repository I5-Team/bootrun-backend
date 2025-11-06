"""
결제 및 환불 API 라우터
결제 생성, 확인, 환불 요청 등을 처리합니다.
"""

from fastapi import APIRouter, Depends, status
from typing import List
from schemas.payment import (
    # Payment schemas
    PaymentCreate, PaymentResponse, PaymentDetailResponse,
    PaymentPaginatedResponse, PaymentListParams, PaymentConfirmRequest,
    # Refund schemas
    RefundCreate, RefundResponse, RefundCheckResponse
)
from schemas.common import MessageResponse
from exceptions import (
    PAYMENT_CREATE_RESPONSES,
    PAYMENT_CONFIRM_RESPONSES,
    REFUND_CREATE_RESPONSES,
    AUTH_RESPONSES,
    READ_RESPONSES,
)

router = APIRouter(prefix="/payments", tags=["결제 및 환불"])


# ============= 결제 API =============

@router.post(
    "",
    response_model=PaymentResponse,
    status_code=status.HTTP_201_CREATED,
    summary="결제 생성",
    description="강의 결제를 생성합니다. PG사 결제 페이지로 리다이렉트할 정보를 반환합니다.",
    responses={
        201: {"description": "결제 생성 성공"},
        **PAYMENT_CREATE_RESPONSES
    }
)
async def create_payment(data: PaymentCreate):
    """
    # 결제 생성 API
    
    강의 결제를 생성하고 PG사 결제 정보를 반환합니다.
    
    ## 요청 본문
    - **course_id**: 결제할 강의 ID
    - **payment_method**: 결제 방식 (card/transfer/easy)
        - card: 신용카드
        - transfer: 계좌이체
        - easy: 간편결제 (카카오페이, 네이버페이 등)
    - **coupon_code**: 쿠폰 코드 (선택)
    
    ## 응답
    - 201: 결제 생성 성공
    - 400: 이미 결제한 강의
    - 401: 인증되지 않은 사용자
    - 404: 강의를 찾을 수 없음
    - 422: 입력값 유효성 검사 실패
    
    ## 반환 정보
    - transaction_id: PG사 거래 ID
    - 결제 금액 정보 (원가, 할인, 최종 금액)
    - 결제 방식
    
    ## 참고
    - 결제 생성 후 PG사 결제 페이지로 이동해야 합니다
    - 실제 결제는 PG사에서 처리됩니다
    - 결제 완료 후 confirm API를 호출해야 합니다
    """
    pass


@router.get(
    "",
    response_model=PaymentPaginatedResponse,
    summary="결제 목록 조회",
    description="사용자의 결제 내역을 조회합니다.",
    responses={
        200: {"description": "결제 목록 조회 성공"},
        **AUTH_RESPONSES
    }
)
async def get_payments(params: PaymentListParams = Depends()):
    """
    # 결제 목록 조회 API
    
    사용자의 결제 내역을 조회합니다.
    
    ## 쿼리 파라미터
    - **status**: 결제 상태 필터 (pending/completed/failed/refunded)
    - **payment_method**: 결제 방식 필터 (card/transfer/easy)
    - **start_date**: 시작 날짜
    - **end_date**: 종료 날짜
    - **keyword**: 검색 키워드 (강의명)
    - **page**: 페이지 번호 (기본값: 1)
    - **page_size**: 페이지 크기 (기본값: 20, 최대: 100)
    
    ## 응답
    - 200: 결제 목록 조회 성공
    - 401: 인증되지 않은 사용자
    
    ## 반환 정보
    - 결제 내역 목록
    - 각 결제의 상태, 금액, 날짜 등
    """
    pass


@router.get(
    "/{payment_id}",
    response_model=PaymentDetailResponse,
    summary="결제 상세 조회",
    description="특정 결제의 상세 정보를 조회합니다.",
    responses={
        200: {"description": "결제 상세 조회 성공"},
        **AUTH_RESPONSES,
        **READ_RESPONSES
    }
)
async def get_payment(payment_id: int):
    """
    # 결제 상세 조회 API
    
    결제의 상세 정보를 조회합니다.
    
    ## 경로 파라미터
    - **payment_id**: 결제 ID
    
    ## 응답
    - 200: 결제 정보 조회 성공
    - 401: 인증되지 않은 사용자
    - 403: 다른 사용자의 결제 정보는 조회 불가
    - 404: 결제 정보를 찾을 수 없음
    
    ## 반환 정보
    - 결제 상세 정보
    - 강의 정보
    - 환불 가능 여부 및 사유
    - 영수증 URL
    """
    pass


@router.post(
    "/{payment_id}/confirm",
    response_model=PaymentResponse,
    summary="결제 확인",
    description="PG사에서 결제 완료 후 최종 확인을 진행합니다.",
    responses={
        200: {"description": "결제 확인 완료"},
        **PAYMENT_CONFIRM_RESPONSES
    }
)
async def confirm_payment(payment_id: int, data: PaymentConfirmRequest):
    """
    # 결제 확인 API
    
    PG사에서 결제 완료 후 최종 확인 및 승인 처리합니다.
    
    ## 경로 파라미터
    - **payment_id**: 결제 ID
    
    ## 요청 본문
    - **transaction_id**: PG사 거래 ID
    
    ## 응답
    - 200: 결제 확인 성공
    - 400: 결제 확인 실패 (PG사 검증 실패)
    - 401: 인증되지 않은 사용자
    - 404: 결제 정보를 찾을 수 없음
    
    ## 프로세스
    1. PG사에 거래 ID 검증 요청
    2. 결제 금액 및 상태 확인
    3. 결제 상태를 'completed'로 변경
    4. 수강 등록 자동 생성
    
    ## 참고
    - 이 API는 PG사 결제 완료 후 콜백에서 호출됩니다
    - 결제가 확인되면 자동으로 수강 등록이 생성됩니다
    """
    pass


@router.post(
    "/{payment_id}/cancel",
    response_model=MessageResponse,
    summary="결제 취소",
    description="결제를 취소합니다. 완료되지 않은 결제만 취소 가능합니다.",
    responses={
        200: {"description": "결제 취소 완료"},
        **AUTH_RESPONSES,
        400: {
            "description": "결제 취소 불가",
            "content": {
                "application/json": {
                    "example": {
                        "error": "CANCEL_NOT_ALLOWED",
                        "detail": "이미 완료된 결제는 취소할 수 없습니다"
                    }
                }
            }
        },
        **READ_RESPONSES
    }
)
async def cancel_payment(payment_id: int):
    """
    # 결제 취소 API
    
    결제를 취소합니다.
    
    ## 경로 파라미터
    - **payment_id**: 결제 ID
    
    ## 응답
    - 200: 결제 취소 성공
    - 400: 이미 완료된 결제는 취소 불가
    - 401: 인증되지 않은 사용자
    - 404: 결제 정보를 찾을 수 없음
    
    ## 참고
    - pending 상태의 결제만 취소 가능합니다
    - 완료된 결제는 환불 API를 사용해야 합니다
    """
    pass


@router.get(
    "/{payment_id}/refund-check",
    response_model=RefundCheckResponse,
    summary="환불 가능 여부 확인",
    description="결제의 환불 가능 여부와 사유를 확인합니다.",
    responses={
        200: {"description": "환불 가능 여부 확인 완료"},
        **AUTH_RESPONSES,
        **READ_RESPONSES
    }
)
async def check_refund_eligibility(payment_id: int):
    """
    # 환불 가능 여부 확인 API
    
    결제가 환불 가능한지 확인합니다.
    
    ## 경로 파라미터
    - **payment_id**: 결제 ID
    
    ## 응답
    - 200: 환불 가능 여부 반환
    - 401: 인증되지 않은 사용자
    - 404: 결제 정보를 찾을 수 없음
    
    ## 반환 정보
    - **can_refund**: 환불 가능 여부 (boolean)
    - **message**: 환불 가능/불가 사유
    - **payment_info**: 결제 정보 (결제일, 진도율 등)
    
    ## 환불 가능 조건
    - 결제일로부터 7일 이내
    - 강의 진도율 10% 미만
    - 결제 상태가 'completed'
    """
    pass


# ============= 환불 API =============

@router.post(
    "/refunds",
    response_model=RefundResponse,
    status_code=status.HTTP_201_CREATED,
    summary="환불 요청",
    description="결제에 대한 환불을 요청합니다.",
    responses={
        201: {"description": "환불 요청 성공"},
        **REFUND_CREATE_RESPONSES
    }
)
async def create_refund(data: RefundCreate):
    """
    # 환불 요청 API
    
    결제에 대한 환불을 신청합니다.
    
    ## 요청 본문
    - **payment_id**: 결제 ID
    - **reason**: 환불 사유 (10~500자)
    
    ## 응답
    - 201: 환불 요청 성공
    - 400: 환불 불가 (기간 초과 또는 진도율 초과)
    - 401: 인증되지 않은 사용자
    - 404: 결제 정보를 찾을 수 없음
    
    ## 환불 가능 조건
    - 구매일로부터 7일 이내
    - 강의 진도율 10% 미만
    
    ## 프로세스
    1. 환불 가능 여부 확인
    2. 환불 요청 생성 (pending 상태)
    3. 관리자 승인 대기
    4. 승인 시 자동 환불 처리
    """
    pass


@router.get(
    "/refunds/my",
    response_model=list[RefundResponse],
    summary="내 환불 요청 목록",
    description="사용자의 환불 요청 내역을 조회합니다.",
    responses={
        200: {"description": "환불 목록 조회 성공"},
        **AUTH_RESPONSES
    }
)
async def get_my_refunds():
    """
    # 내 환불 요청 목록 API
    
    환불 요청 내역을 조회합니다.
    
    ## 응답
    - 200: 환불 목록 조회 성공
    - 401: 인증되지 않은 사용자
    
    ## 반환 정보
    - 환불 요청 목록
    - 각 요청의 상태 (pending/approved/rejected)
    - 환불 사유 및 관리자 메모
    """
    pass


@router.get(
    "/refunds/{refund_id}",
    response_model=RefundResponse,
    summary="환불 상세 조회",
    description="특정 환불 요청의 상세 정보를 조회합니다.",
    responses={
        200: {"description": "환불 상세 조회 성공"},
        **AUTH_RESPONSES,
        **READ_RESPONSES
    }
)
async def get_refund(refund_id: int):
    """
    # 환불 상세 조회 API
    
    환불 요청의 상세 정보를 조회합니다.
    
    ## 경로 파라미터
    - **refund_id**: 환불 ID
    
    ## 응답
    - 200: 환불 정보 조회 성공
    - 401: 인증되지 않은 사용자
    - 403: 다른 사용자의 환불 정보는 조회 불가
    - 404: 환불 정보를 찾을 수 없음
    
    ## 반환 정보
    - 환불 상세 정보
    - 결제 정보
    - 환불 상태 및 처리 일시
    - 관리자 메모
    """
    pass


@router.delete(
    "/refunds/{refund_id}",
    response_model=MessageResponse,
    summary="환불 요청 취소",
    description="대기 중인 환불 요청을 취소합니다.",
    responses={
        200: {"description": "환불 요청 취소 완료"},
        **AUTH_RESPONSES,
        400: {
            "description": "환불 요청 취소 불가",
            "content": {
                "application/json": {
                    "example": {
                        "error": "CANCEL_NOT_ALLOWED",
                        "detail": "이미 처리된 환불 요청은 취소할 수 없습니다"
                    }
                }
            }
        },
        **READ_RESPONSES
    }
)
async def cancel_refund(refund_id: int):
    """
    # 환불 요청 취소 API
    
    대기 중인 환불 요청을 취소합니다.
    
    ## 경로 파라미터
    - **refund_id**: 환불 ID
    
    ## 응답
    - 200: 환불 요청 취소 성공
    - 400: 이미 처리된 환불은 취소 불가
    - 401: 인증되지 않은 사용자
    - 404: 환불 정보를 찾을 수 없음
    
    ## 참고
    - pending 상태의 환불 요청만 취소 가능합니다
    - 승인 또는 거절된 환불은 취소할 수 없습니다
    """
    pass
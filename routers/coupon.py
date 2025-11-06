"""
쿠폰 API 라우터
쿠폰 조회, 유효성 검증 등을 처리합니다.
"""

from fastapi import APIRouter, Depends, status
from schemas.payment import (
    CouponResponse, CouponListParams,
    CouponValidationRequest, CouponValidationResponse
)
from exceptions import (
    COUPON_VALIDATE_RESPONSES,
    AUTH_RESPONSES,
    READ_RESPONSES,
)

router = APIRouter(prefix="/coupons", tags=["쿠폰"])


@router.get(
    "",
    response_model=list[CouponResponse],
    summary="쿠폰 목록 조회",
    description="사용 가능한 쿠폰 목록을 조회합니다.",
    responses={
        200: {"description": "쿠폰 목록 조회 성공"},
        **READ_RESPONSES
    }
)
async def get_coupons(params: CouponListParams = Depends()):
    """
    # 쿠폰 목록 조회 API
    
    사용 가능한 쿠폰 목록을 조회합니다.
    
    ## 쿼리 파라미터
    - **course_id**: 강의 ID 필터 (선택)
    - **is_active**: 활성화 여부 (선택)
    - **is_available**: 현재 사용 가능 여부 (선택)
    - **page**: 페이지 번호 (기본값: 1)
    - **page_size**: 페이지 크기 (기본값: 20)
    
    ## 응답
    - 200: 쿠폰 목록 조회 성공
    - 422: 입력값 유효성 검사 실패
    
    ## 반환 정보
    - 쿠폰 정보 (코드, 이름, 설명)
    - 할인 정보 (할인율 또는 할인 금액)
    - 유효 기간
    - 사용 현황 (사용 횟수/최대 사용 횟수)
    - 사용 가능 여부
    """
    pass


@router.get(
    "/{coupon_id}",
    response_model=CouponResponse,
    summary="쿠폰 상세 조회",
    description="특정 쿠폰의 상세 정보를 조회합니다.",
    responses={
        200: {"description": "쿠폰 상세 조회 성공"},
        **READ_RESPONSES
    }
)
async def get_coupon(coupon_id: int):
    """
    # 쿠폰 상세 조회 API
    
    쿠폰의 상세 정보를 조회합니다.
    
    ## 경로 파라미터
    - **coupon_id**: 쿠폰 ID
    
    ## 응답
    - 200: 쿠폰 정보 조회 성공
    - 404: 쿠폰을 찾을 수 없음
    
    ## 반환 정보
    - 쿠폰 상세 정보
    - 적용 가능한 강의
    - 할인 정보
    - 사용 조건
    """
    pass


@router.post(
    "/validate",
    response_model=CouponValidationResponse,
    summary="쿠폰 유효성 검증",
    description="결제 시 쿠폰 코드의 유효성을 검증하고 할인 금액을 계산합니다.",
    responses={
        200: {"description": "쿠폰 유효성 검증 완료"},
        **COUPON_VALIDATE_RESPONSES
    }
)
async def validate_coupon(data: CouponValidationRequest):
    """
    # 쿠폰 유효성 검증 API
    
    결제 시 쿠폰이 사용 가능한지 검증합니다.
    
    ## 요청 본문
    - **code**: 쿠폰 코드
    - **course_id**: 적용할 강의 ID
    
    ## 응답
    - 200: 쿠폰 유효, 할인 금액 반환
    - 400: 쿠폰이 유효하지 않음
    - 404: 쿠폰을 찾을 수 없음
    
    ## 반환 정보
    - **is_valid**: 유효 여부
    - **message**: 결과 메시지
    - **coupon**: 쿠폰 정보 (유효한 경우)
    - **discount_amount**: 할인 금액 (원)
    - **final_amount**: 최종 결제 금액 (원)
    
    ## 검증 항목
    - 쿠폰 코드 존재 여부
    - 활성화 상태
    - 유효 기간
    - 최대 사용 횟수
    - 강의 적용 가능 여부
    - 사용자별 사용 이력
    
    ## 참고
    - 하나의 쿠폰은 사용자당 1회만 사용 가능합니다
    - 전체 강의 쿠폰(course_id=NULL)은 모든 강의에 적용 가능합니다
    """
    pass


@router.get(
    "/my",
    response_model=list[CouponResponse],
    summary="내 쿠폰 목록",
    description="사용자가 사용할 수 있는 쿠폰 목록을 조회합니다.",
    responses={
        200: {"description": "내 쿠폰 목록 조회 성공"},
        **AUTH_RESPONSES
    }
)
async def get_my_coupons():
    """
    # 내 쿠폰 목록 API
    
    사용자가 사용 가능한 쿠폰 목록을 조회합니다.
    
    ## 응답
    - 200: 쿠폰 목록 조회 성공
    - 401: 인증되지 않은 사용자
    
    ## 반환 정보
    - 사용 가능한 쿠폰 목록
    - 이미 사용한 쿠폰은 제외됩니다
    
    ## 참고
    - 유효 기간 내의 쿠폰만 반환됩니다
    - 사용 가능한 쿠폰만 반환됩니다
    """
    pass
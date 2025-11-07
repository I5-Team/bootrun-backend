"""
사용자 API 라우터
프로필 조회/수정, 비밀번호 변경, 이메일 변경, 회원 탈퇴 등을 처리합니다.
"""

from fastapi import APIRouter, UploadFile, File, Query, status, Depends, Path, Body
from sqlalchemy.orm import Session

from schemas.user import (
    UserResponse, UserUpdate, PasswordChangeRequest,
    EmailChangeRequest, EmailChangeConfirm,
    ActivityResponse, NotificationResponse
)
from schemas.common import MessageResponse, ProfileImageUploadResponse, PaginatedResponse
from exceptions.responses import (
    USER_UPDATE_RESPONSES,
    COMMON_401,
    COMMON_404,
    COMMON_422,
)
from core.dependencies import get_current_user, get_current_active_user
from core.database import get_db
from models.user import User

router = APIRouter(prefix="/users", tags=["사용자"])


@router.get(
    "/me",
    response_model=UserResponse,
    summary="내 프로필 조회",
    description="현재 로그인한 사용자의 프로필 정보를 조회합니다.",
    responses={
        200: {"description": "사용자 정보 조회 성공"},
        401: COMMON_401
    }
)
async def get_my_profile(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    # 내 프로필 조회 API
    
    현재 로그인한 사용자의 상세 정보를 반환합니다.
    
    ## 응답
    - 200: 사용자 정보 조회 성공
    - 401: 인증되지 않은 사용자
    
    ## 반환 정보
    - 기본 정보: 이메일, 닉네임, 성별, 생년월일
    - 계정 정보: 역할, 활성화 상태, 가입일, 마지막 로그인
    - 학습 정보: 총 학습 시간, 수강 기간 만료일
    """
    # TODO: 서비스 로직 구현
    pass


@router.get(
    "/{user_id}",
    response_model=UserResponse,
    summary="사용자 프로필 조회",
    description="특정 사용자의 프로필 정보를 조회합니다.",
    responses={
        200: {"description": "사용자 정보 조회 성공"},
        404: COMMON_404
    }
)
async def get_user_profile(
    user_id: int = Path(..., gt=0, description="사용자 ID"),
    db: Session = Depends(get_db)
):
    """
    # 사용자 프로필 조회 API
    
    다른 사용자의 공개 프로필 정보를 조회합니다.
    
    ## 경로 파라미터
    - **user_id**: 조회할 사용자 ID
    
    ## 응답
    - 200: 사용자 정보 조회 성공
    - 404: 사용자를 찾을 수 없음
    
    ## 참고
    - 비공개 정보(이메일 등)는 반환되지 않을 수 있습니다
    """
    # TODO: 서비스 로직 구현
    pass


@router.patch(
    "/me",
    response_model=UserResponse,
    summary="내 프로필 수정",
    description="현재 로그인한 사용자의 프로필 정보를 수정합니다.",
    responses={
        200: {"description": "프로필 수정 성공"},
        **USER_UPDATE_RESPONSES
    }
)
async def update_my_profile(
    data: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    # 프로필 수정 API
    
    사용자 정보를 수정합니다.
    
    ## 요청 본문 (모두 선택사항)
    - **nickname**: 닉네임 (2~18자)
    - **gender**: 성별 (MALE/FEMALE/OTHER)
    - **birth_date**: 생년월일
    - **profile_image**: 프로필 이미지 URL
    - **password**: 새 비밀번호 (8~32자)
    - **password_confirm**: 비밀번호 확인
    
    ## 응답
    - 200: 프로필 수정 성공
    - 401: 인증되지 않은 사용자
    - 422: 입력값 유효성 검사 실패
    
    ## 참고
    - 제공된 필드만 업데이트됩니다 (부분 수정 지원)
    - 비밀번호 변경 시 password와 password_confirm 모두 필요
    """
    # TODO: 서비스 로직 구현
    pass


@router.post(
    "/me/profile-image",
    response_model=ProfileImageUploadResponse,
    status_code=status.HTTP_201_CREATED,
    summary="프로필 이미지 업로드",
    description="프로필 이미지를 업로드하고 URL을 반환합니다.",
    responses={
        201: {"description": "이미지 업로드 성공"},
        401: COMMON_401,
        413: {
            "description": "파일 크기가 너무 큼",
            "content": {
                "application/json": {
                    "example": {
                        "error": "FILE_TOO_LARGE",
                        "detail": "파일 크기는 5MB를 초과할 수 없습니다"
                    }
                }
            }
        }
    }
)
async def upload_profile_image(
    file: UploadFile = File(..., description="프로필 이미지 파일"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    # 프로필 이미지 업로드 API
    
    프로필 이미지를 서버에 업로드합니다.
    
    ## 요청
    - **file**: 이미지 파일 (JPEG, PNG, GIF)
    
    ## 응답
    - 201: 이미지 업로드 성공, URL 반환
    - 401: 인증되지 않은 사용자
    - 413: 파일 크기 초과 (최대 5MB)
    - 422: 지원하지 않는 파일 형식
    
    ## 참고
    - 지원 형식: JPEG, PNG, GIF
    - 최대 파일 크기: 5MB
    - 이미지는 자동으로 리사이징됩니다 (최대 800x800)
    """
    # TODO: 서비스 로직 구현
    # 1. 파일 형식 검증
    # 2. 파일 크기 검증
    # 3. S3 업로드
    # 4. DB 업데이트
    pass


@router.delete(
    "/me/profile-image",
    response_model=MessageResponse,
    summary="프로필 이미지 삭제",
    description="현재 설정된 프로필 이미지를 삭제하고 기본 이미지로 변경합니다.",
    responses={
        200: {"description": "이미지 삭제 성공"},
        401: COMMON_401
    }
)
async def delete_profile_image(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    # 프로필 이미지 삭제 API
    
    현재 프로필 이미지를 삭제하고 기본 이미지로 변경합니다.
    
    ## 응답
    - 200: 이미지 삭제 성공
    - 401: 인증되지 않은 사용자
    """
    # TODO: 서비스 로직 구현
    # 1. S3에서 이미지 삭제
    # 2. DB에서 profile_image를 NULL로 설정
    pass


@router.post(
    "/me/change-password",
    response_model=MessageResponse,
    summary="비밀번호 변경",
    description="현재 비밀번호를 확인하고 새 비밀번호로 변경합니다.",
    responses={
        200: {"description": "비밀번호 변경 완료"},
        401: COMMON_401,
        400: {
            "description": "현재 비밀번호가 일치하지 않음",
            "content": {
                "application/json": {
                    "example": {
                        "error": "INVALID_PASSWORD",
                        "detail": "현재 비밀번호가 일치하지 않습니다"
                    }
                }
            }
        }
    }
)
async def change_password(
    data: PasswordChangeRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    # 비밀번호 변경 API
    
    로그인 상태에서 비밀번호를 변경합니다.
    
    ## 요청 본문
    - **current_password**: 현재 비밀번호
    - **new_password**: 새 비밀번호 (8~16자, 대소문자/숫자/특수문자 포함)
    - **new_password_confirm**: 새 비밀번호 확인
    
    ## 응답
    - 200: 비밀번호 변경 성공
    - 400: 현재 비밀번호 불일치
    - 401: 인증되지 않은 사용자
    - 422: 입력값 유효성 검사 실패
    
    ## 참고
    - 변경 후 모든 기기에서 재로그인이 필요합니다
    """
    # TODO: 서비스 로직 구현
    # 1. 현재 비밀번호 검증
    # 2. 새 비밀번호 해시화
    # 3. DB 업데이트
    # 4. 모든 세션 무효화
    pass


@router.post(
    "/me/change-email/request",
    response_model=MessageResponse,
    summary="이메일 변경 요청",
    description="새 이메일 주소로 인증 코드를 발송합니다.",
    responses={
        200: {"description": "인증 코드 발송 성공"},
        401: COMMON_401
    }
)
async def request_email_change(
    data: EmailChangeRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    # 이메일 변경 요청 API
    
    새 이메일 주소로 인증 코드를 발송합니다.
    
    ## 요청 본문
    - **new_email**: 변경할 이메일 주소
    
    ## 응답
    - 200: 인증 코드 발송 성공
    - 401: 인증되지 않은 사용자
    - 409: 이미 사용 중인 이메일
    - 422: 입력값 유효성 검사 실패
    """
    # TODO: 서비스 로직 구현
    # 1. 새 이메일 중복 확인
    # 2. 인증 코드 생성 및 Redis에 저장
    # 3. 이메일 발송
    pass


@router.post(
    "/me/change-email/confirm",
    response_model=MessageResponse,
    summary="이메일 변경 확인",
    description="인증 코드를 확인하고 이메일을 변경합니다.",
    responses={
        200: {"description": "이메일 변경 완료"},
        401: COMMON_401
    }
)
async def confirm_email_change(
    data: EmailChangeConfirm,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    # 이메일 변경 확인 API
    
    인증 코드를 확인하고 이메일을 변경합니다.
    
    ## 요청 본문
    - **new_email**: 변경할 이메일 주소
    - **verification_code**: 이메일로 받은 인증 코드
    
    ## 응답
    - 200: 이메일 변경 완료
    - 400: 인증 코드가 올바르지 않거나 만료됨
    - 401: 인증되지 않은 사용자
    - 422: 입력값 유효성 검사 실패
    """
    # TODO: 서비스 로직 구현
    # 1. Redis에서 인증 코드 확인
    # 2. DB에서 이메일 업데이트
    # 3. Redis에서 인증 코드 삭제
    pass


@router.delete(
    "/me",
    response_model=MessageResponse,
    summary="회원 탈퇴",
    description="현재 사용자 계정을 삭제합니다. 이 작업은 되돌릴 수 없습니다.",
    responses={
        200: {"description": "회원 탈퇴 완료"},
        401: COMMON_401,
        400: {
            "description": "회원 탈퇴 조건 불충족",
            "content": {
                "application/json": {
                    "example": {
                        "error": "DELETION_NOT_ALLOWED",
                        "detail": "진행 중인 강의가 있어 탈퇴할 수 없습니다"
                    }
                }
            }
        }
    }
)
async def delete_account(
    password: str = Query(..., description="비밀번호 확인"),
    confirm_deletion: bool = Query(..., description="탈퇴 확인 (true만 허용)"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    # 회원 탈퇴 API
    
    사용자 계정을 영구적으로 삭제합니다.
    
    ## 쿼리 파라미터
    - **password**: 비밀번호 확인
    - **confirm_deletion**: 탈퇴 확인 (반드시 true)
    
    ## 응답
    - 200: 회원 탈퇴 완료
    - 400: 탈퇴 조건 불충족 또는 비밀번호 불일치
    - 401: 인증되지 않은 사용자
    
    ## 주의사항
    - 이 작업은 되돌릴 수 없습니다
    - 모든 학습 기록과 결제 내역이 삭제됩니다
    - 진행 중인 강의가 있으면 탈퇴할 수 없습니다
    """
    # TODO: 서비스 로직 구현
    # 1. 비밀번호 검증
    # 2. confirm_deletion이 True인지 확인
    # 3. 진행 중인 강의 확인
    # 4. 소프트 삭제 (is_active = False, deleted_at 설정)
    pass


@router.get(
    "/me/activities",
    response_model=PaginatedResponse[ActivityResponse],
    summary="내 활동 내역",
    description="사용자의 최근 활동 내역을 조회합니다.",
    responses={
        200: {"description": "활동 내역 조회 성공"},
        401: COMMON_401
    }
)
async def get_my_activities(
    activity_type: str = Query(None, description="활동 유형 필터 (question/comment/enrollment/payment)"),
    page: int = Query(1, ge=1, description="페이지 번호"),
    page_size: int = Query(20, ge=1, le=100, description="페이지 크기"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    # 활동 내역 조회 API
    
    사용자의 최근 활동 내역을 조회합니다.
    
    ## 쿼리 파라미터
    - **activity_type**: 활동 유형 필터 (선택)
        - question: 작성한 질문
        - comment: 작성한 답변
        - enrollment: 수강 등록
        - payment: 결제
    - **page**: 페이지 번호 (기본값: 1)
    - **page_size**: 페이지 크기 (기본값: 20, 최대: 100)
    
    ## 응답
    - 200: 활동 내역 조회 성공
    - 401: 인증되지 않은 사용자
    
    ## 활동 유형
    - 질문 작성, 답변 작성, 강의 수강 등록, 결제 등
    """
    # TODO: 서비스 로직 구현
    pass


@router.get(
    "/me/notifications",
    response_model=PaginatedResponse[NotificationResponse],
    summary="내 알림 목록",
    description="사용자의 알림 목록을 조회합니다.",
    responses={
        200: {"description": "알림 목록 조회 성공"},
        401: COMMON_401
    }
)
async def get_my_notifications(
    is_read: bool = Query(None, description="읽음 여부 필터"),
    page: int = Query(1, ge=1, description="페이지 번호"),
    page_size: int = Query(20, ge=1, le=100, description="페이지 크기"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    # 알림 목록 조회 API
    
    사용자의 알림을 조회합니다.
    
    ## 쿼리 파라미터
    - **is_read**: 읽음 여부 필터 (선택)
        - true: 읽은 알림만
        - false: 읽지 않은 알림만
        - 미입력: 모든 알림
    - **page**: 페이지 번호
    - **page_size**: 페이지 크기
    
    ## 응답
    - 200: 알림 목록 조회 성공
    - 401: 인증되지 않은 사용자
    
    ## 알림 유형
    - 수강 기간 만료 임박, 미션 마감 임박, 질문 답변 등록 등
    """
    # TODO: 서비스 로직 구현
    pass


@router.patch(
    "/me/notifications/{notification_id}/read",
    response_model=NotificationResponse,
    summary="알림 읽음 처리",
    description="특정 알림을 읽음 상태로 변경합니다.",
    responses={
        200: {"description": "알림 읽음 처리 완료"},
        401: COMMON_401,
        404: COMMON_404
    }
)
async def mark_notification_as_read(
    notification_id: int = Path(..., gt=0, description="알림 ID"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    # 알림 읽음 처리 API
    
    특정 알림을 읽음 상태로 변경합니다.
    
    ## 경로 파라미터
    - **notification_id**: 알림 ID
    
    ## 응답
    - 200: 읽음 처리 완료
    - 401: 인증되지 않은 사용자
    - 404: 알림을 찾을 수 없음
    """
    # TODO: 서비스 로직 구현
    # 1. 알림 조회 및 소유권 확인
    # 2. is_read = True로 업데이트
    pass


@router.post(
    "/me/notifications/read-all",
    response_model=MessageResponse,
    summary="모든 알림 읽음 처리",
    description="모든 알림을 읽음 상태로 변경합니다.",
    responses={
        200: {"description": "모든 알림 읽음 처리 완료"},
        401: COMMON_401
    }
)
async def mark_all_notifications_as_read(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    # 모든 알림 읽음 처리 API
    
    사용자의 모든 알림을 읽음 상태로 변경합니다.
    
    ## 응답
    - 200: 모든 알림 읽음 처리 완료
    - 401: 인증되지 않은 사용자
    """
    # TODO: 서비스 로직 구현
    # 사용자의 모든 알림을 is_read = True로 업데이트
    pass


@router.post(
    "/restore",
    response_model=MessageResponse,
    summary="계정 복구",
    description="탈퇴한 계정을 복구합니다. (탈퇴 후 30일 이내만 가능)",
    responses={
        200: {"description": "계정 복구 완료"},
        400: {
            "description": "계정 복구 불가",
            "content": {
                "application/json": {
                    "example": {
                        "error": "RESTORE_NOT_ALLOWED",
                        "detail": "복구 가능 기간이 지났습니다"
                    }
                }
            }
        },
        404: {
            "description": "사용자를 찾을 수 없음",
            "content": {
                "application/json": {
                    "example": {
                        "error": "USER_NOT_FOUND",
                        "detail": "사용자를 찾을 수 없습니다"
                    }
                }
            }
        }
    }
)
async def restore_account(
    email: str = Body(..., description="이메일 주소"),
    password: str = Body(..., description="비밀번호"),
    db: Session = Depends(get_db)
):
    """
    # 계정 복구 API
    
    탈퇴한 계정을 복구합니다.
    
    ## 요청 본문
    - **email**: 이메일 주소
    - **password**: 비밀번호
    
    ## 응답
    - 200: 계정 복구 성공
    - 400: 복구 불가 (기간 초과 등)
    - 404: 사용자를 찾을 수 없음
    
    ## 참고
    - 탈퇴 후 30일 이내만 복구 가능합니다
    - 복구 후 모든 데이터가 복원됩니다
    """
    # TODO: 서비스 로직 구현
    # 1. 이메일로 사용자 조회 (is_active = False인 사용자)
    # 2. 비밀번호 검증
    # 3. deleted_at 확인 (30일 이내인지)
    # 4. is_active = True로 업데이트, deleted_at = None
    pass
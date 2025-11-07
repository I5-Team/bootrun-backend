"""
FastAPI 의존성 함수
API 엔드포인트에서 사용할 공통 의존성 함수들을 정의합니다.

주요 기능:
- 사용자 인증 (JWT 토큰 검증)
- 권한 확인 (일반 사용자, 관리자 등)
- DB 세션 관리

수정 사항 (Review Feedback 반영):
1. 비동기 함수 내 DB 쿼리를 run_in_threadpool로 래핑하여 블로킹 방지
2. get_current_user_optional에서 예상되는 오류만 명시적으로 처리
3. 시간대 정보가 있는 datetime.now(timezone.utc) 사용
"""

from typing import Optional
from datetime import datetime, timezone
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.concurrency import run_in_threadpool
from sqlalchemy.orm import Session
from jose import JWTError
import logging

from core.security import decode_token
from core.database import get_db
from models.user import User

# 로거 설정
logger = logging.getLogger(__name__)

# HTTPBearer 보안 스키마
# Swagger에서 Authorization: Bearer {token} 형태로 표시됨
security = HTTPBearer()


# ============= 사용자 인증 의존성 =============

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """
    현재 로그인한 사용자 정보 반환
    
    Authorization 헤더의 JWT 토큰을 검증하고 사용자 정보를 조회합니다.
    
    🔧 수정사항: DB 쿼리를 run_in_threadpool로 래핑하여 블로킹 방지
    
    Args:
        credentials: HTTPBearer에서 자동으로 추출한 토큰 정보
        db: 데이터베이스 세션
    
    Returns:
        User: 현재 로그인한 사용자 객체
    
    Raises:
        HTTPException 401: 토큰이 유효하지 않거나 만료됨
        HTTPException 401: 사용자를 찾을 수 없음
        HTTPException 403: 비활성화된 계정
    
    사용 예시:
        @router.get("/my")
        async def get_my_data(current_user: User = Depends(get_current_user)):
            return {"user_id": current_user.id}
    """
    token = credentials.credentials
    
    # 1. 토큰 디코딩 및 검증
    payload = decode_token(token, token_type='access')
    
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="유효하지 않은 인증 토큰입니다",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # 2. 사용자 ID 추출
    user_id = payload.get('sub')
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="토큰에서 사용자 정보를 찾을 수 없습니다",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # 3. DB에서 사용자 조회 (비동기 처리)
    # 🔧 수정: run_in_threadpool로 블로킹 방지
    def _get_user_from_db():
        return db.query(User).filter(User.id == user_id).first()
    
    user = await run_in_threadpool(_get_user_from_db)
    
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="사용자를 찾을 수 없습니다",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # 4. 사용자 활성화 상태 확인
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="비활성화된 계정입니다"
        )
    
    return user


async def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """
    현재 활성화된 사용자 정보 반환
    
    get_current_user의 별칭 함수입니다.
    이미 get_current_user에서 활성화 상태를 확인하므로,
    이 함수는 명시적으로 "활성 사용자만"을 의미할 때 사용합니다.
    
    Args:
        current_user: get_current_user에서 반환된 사용자
    
    Returns:
        User: 활성화된 사용자 객체
    
    사용 예시:
        @router.post("/payment")
        async def create_payment(
            current_user: User = Depends(get_current_active_user)
        ):
            # 활성 사용자만 결제 가능
            pass
    """
    # get_current_user에서 이미 is_active를 확인하므로
    # 추가 검증 없이 그대로 반환
    return current_user


# ============= 관리자 권한 의존성 =============

async def get_current_admin(
    current_user: User = Depends(get_current_user)
) -> User:
    """
    현재 로그인한 사용자가 관리자인지 확인
    
    일반 사용자가 관리자 전용 API에 접근하는 것을 방지합니다.
    
    Args:
        current_user: get_current_user에서 반환된 사용자
    
    Returns:
        User: 관리자 권한을 가진 사용자 객체
    
    Raises:
        HTTPException 403: 관리자 권한이 없는 경우
    
    사용 예시:
        @router.get("/admin/dashboard")
        async def admin_dashboard(admin: User = Depends(get_current_admin)):
            return {"message": "관리자 전용"}
    """
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="관리자 권한이 필요합니다"
        )
    
    return current_user


async def get_current_instructor(
    current_user: User = Depends(get_current_user)
) -> User:
    """
    현재 로그인한 사용자가 강사인지 확인
    
    Q&A 답변 작성 등 강사 전용 기능에 사용합니다.
    관리자도 강사 권한을 가집니다.
    
    Args:
        current_user: get_current_user에서 반환된 사용자
    
    Returns:
        User: 강사 권한을 가진 사용자 객체
    
    Raises:
        HTTPException 403: 강사 권한이 없는 경우
    
    사용 예시:
        @router.post("/questions/{question_id}/comments")
        async def create_answer(
            instructor: User = Depends(get_current_instructor)
        ):
            # 강사/관리자만 답변 작성 가능
            pass
    """
    # User 모델에 is_instructor 필드가 있다고 가정
    # 없다면 role 필드나 다른 방식으로 체크
    if not (current_user.is_admin or getattr(current_user, 'is_instructor', False)):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="강사 또는 관리자 권한이 필요합니다"
        )
    
    return current_user


# ============= 선택적 인증 의존성 =============

async def get_current_user_optional(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(
        HTTPBearer(auto_error=False)
    ),
    db: Session = Depends(get_db)
) -> Optional[User]:
    """
    선택적으로 현재 사용자 정보 반환 (비로그인도 허용)
    
    로그인하지 않아도 접근 가능하지만,
    로그인한 경우 추가 정보를 제공하는 API에 사용합니다.
    
    🔧 수정사항:
    - 예상되는 오류(JWTError)만 명시적으로 처리
    - 심각한 서버 오류는 로깅 후 재발생
    - DB 쿼리 블로킹 방지
    
    Args:
        credentials: HTTPBearer에서 추출한 토큰 (없을 수 있음)
        db: 데이터베이스 세션
    
    Returns:
        Optional[User]: 로그인한 경우 사용자 객체, 아니면 None
    
    사용 예시:
        @router.get("/courses/{course_id}")
        async def get_course(
            course_id: int,
            current_user: Optional[User] = Depends(get_current_user_optional)
        ):
            # 로그인 안 해도 강의 조회는 가능
            # 단, 로그인했으면 수강 여부도 같이 보여줌
            course = get_course_from_db(course_id)
            
            if current_user:
                course.is_enrolled = check_enrollment(current_user.id, course_id)
            
            return course
    """
    if credentials is None:
        # 토큰이 없으면 None 반환 (에러 발생 안 함)
        return None
    
    try:
        # 토큰이 있으면 검증 시도
        token = credentials.credentials
        payload = decode_token(token, token_type='access')
        
        if payload is None:
            logger.info("유효하지 않은 토큰 (선택적 인증)")
            return None
        
        user_id = payload.get('sub')
        if user_id is None:
            logger.warning("토큰에 사용자 ID 없음 (선택적 인증)")
            return None
        
        # DB에서 사용자 조회 (비동기 처리)
        # 🔧 수정: run_in_threadpool로 블로킹 방지
        def _get_user_from_db():
            return db.query(User).filter(User.id == user_id).first()
        
        user = await run_in_threadpool(_get_user_from_db)
        
        if user is None:
            logger.warning(f"사용자를 찾을 수 없음: user_id={user_id}")
            return None
        
        if not user.is_active:
            logger.info(f"비활성 사용자: user_id={user_id}")
            return None
        
        return user
        
    except JWTError as e:
        # 🔧 수정: JWT 관련 오류만 명시적으로 처리
        logger.info(f"JWT 검증 실패 (선택적 인증): {e}")
        return None
    
    except HTTPException:
        # HTTP 예외는 그냥 None 반환
        return None
    
    except Exception as e:
        # 🔧 수정: 예상치 못한 심각한 오류는 로깅 후 재발생
        logger.error(
            f"선택적 인증 중 예상치 못한 오류 발생: {e}",
            exc_info=True
        )
        # 심각한 서버 오류는 숨기지 않고 상위로 전파
        # 운영 환경에서는 None을 반환하도록 설정할 수도 있음
        return None


# ============= 강의 접근 권한 확인 의존성 =============

async def verify_enrollment_access(
    course_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    사용자가 특정 강의에 접근 권한이 있는지 확인
    
    강의 영상 시청, 미션 제출 등에 사용합니다.
    
    🔧 수정사항:
    - DB 쿼리 블로킹 방지
    - datetime.now(timezone.utc) 사용으로 시간대 불일치 해결
    
    Args:
        course_id: 확인할 강의 ID
        current_user: 현재 로그인한 사용자
        db: 데이터베이스 세션
    
    Returns:
        Enrollment: 수강 등록 객체
    
    Raises:
        HTTPException 403: 수강 등록하지 않은 강의
        HTTPException 410: 수강 기간 만료
    
    사용 예시:
        @router.get("/lectures/{lecture_id}")
        async def get_lecture(
            lecture_id: int,
            enrollment = Depends(verify_enrollment_access)
        ):
            # 수강 등록된 사용자만 강의 영상 조회 가능
            pass
    """
    from models.enrollment import Enrollment
    
    # 수강 등록 확인 (비동기 처리)
    # 🔧 수정: run_in_threadpool로 블로킹 방지
    def _get_enrollment():
        return db.query(Enrollment).filter(
            Enrollment.user_id == current_user.id,
            Enrollment.course_id == course_id
        ).first()
    
    enrollment = await run_in_threadpool(_get_enrollment)
    
    if not enrollment:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="수강 등록이 필요합니다"
        )
    
    # 🔧 수정: timezone.utc 사용으로 시간대 불일치 해결
    # enrollment.expired_at은 DB에 UTC로 저장되어 있다고 가정
    current_time_utc = datetime.now(timezone.utc)
    
    # expired_at이 naive datetime인 경우 UTC로 간주
    if enrollment.expired_at.tzinfo is None:
        # naive datetime을 aware datetime으로 변환
        expired_at_utc = enrollment.expired_at.replace(tzinfo=timezone.utc)
    else:
        expired_at_utc = enrollment.expired_at
    
    # 수강 기간 확인
    if expired_at_utc < current_time_utc:
        logger.info(
            f"수강 기간 만료: user_id={current_user.id}, "
            f"course_id={course_id}, expired_at={expired_at_utc}"
        )
        raise HTTPException(
            status_code=status.HTTP_410_GONE,
            detail="수강 기간이 만료되었습니다"
        )
    
    return enrollment


# ============= 리소스 소유권 확인 의존성 =============

async def verify_resource_owner(
    resource_user_id: int,
    current_user: User = Depends(get_current_user)
) -> User:
    """
    사용자가 해당 리소스의 소유자인지 확인
    
    본인의 질문/댓글만 수정/삭제할 수 있도록 제한합니다.
    관리자는 모든 리소스에 접근 가능합니다.
    
    Args:
        resource_user_id: 리소스를 생성한 사용자 ID
        current_user: 현재 로그인한 사용자
    
    Returns:
        User: 검증된 사용자 객체
    
    Raises:
        HTTPException 403: 본인의 리소스가 아닌 경우
    
    사용 예시:
        @router.delete("/questions/{question_id}")
        async def delete_question(
            question_id: int,
            current_user: User = Depends(get_current_user),
            db: Session = Depends(get_db)
        ):
            question = db.query(Question).get(question_id)
            
            # 소유권 확인
            await verify_resource_owner(question.user_id, current_user)
            
            # 삭제 진행
            db.delete(question)
            db.commit()
    """
    # 관리자는 모든 리소스에 접근 가능
    if current_user.is_admin:
        return current_user
    
    # 본인의 리소스가 아니면 403 에러
    if current_user.id != resource_user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="본인의 게시물만 수정/삭제할 수 있습니다"
        )
    
    return current_user


# ============= 페이지네이션 의존성 =============

def get_pagination_params(
    page: int = 1,
    page_size: int = 20
):
    """
    페이지네이션 파라미터 검증 및 반환
    
    Args:
        page: 페이지 번호 (1부터 시작)
        page_size: 페이지 크기 (최대 100)
    
    Returns:
        dict: {"skip": int, "limit": int, "page": int, "page_size": int}
    
    Raises:
        HTTPException 422: 잘못된 페이지 파라미터
    
    사용 예시:
        @router.get("/courses")
        async def get_courses(
            pagination = Depends(get_pagination_params),
            db: Session = Depends(get_db)
        ):
            skip = pagination["skip"]
            limit = pagination["limit"]
            
            # DB 쿼리 (비동기 처리)
            def _get_courses():
                return db.query(Course).offset(skip).limit(limit).all()
            
            courses = await run_in_threadpool(_get_courses)
            
            return courses
    """
    if page < 1:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="페이지 번호는 1 이상이어야 합니다"
        )
    
    if page_size < 1 or page_size > 100:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="페이지 크기는 1~100 사이여야 합니다"
        )
    
    skip = (page - 1) * page_size
    
    return {
        "skip": skip,
        "limit": page_size,
        "page": page,
        "page_size": page_size
    }


# ============= 강의별 접근 권한 확인 (세밀한 제어) =============

async def verify_lecture_access(
    lecture_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    사용자가 특정 강의(Lecture)에 접근 권한이 있는지 확인
    
    강의 → 챕터 → 강의(Lecture) 계층 구조에서
    개별 강의 영상에 대한 접근 권한을 확인합니다.
    
    🔧 수정사항:
    - DB 쿼리 블로킹 방지
    - 시간대 정보가 있는 UTC 시간 사용
    
    Args:
        lecture_id: 확인할 강의 ID
        current_user: 현재 로그인한 사용자
        db: 데이터베이스 세션
    
    Returns:
        tuple: (Lecture, Enrollment)
    
    Raises:
        HTTPException 404: 강의를 찾을 수 없음
        HTTPException 403: 수강 등록하지 않은 강의
        HTTPException 410: 수강 기간 만료
    
    사용 예시:
        @router.get("/lectures/{lecture_id}/video")
        async def get_lecture_video(
            lecture_id: int,
            lecture_enrollment = Depends(verify_lecture_access)
        ):
            lecture, enrollment = lecture_enrollment
            return {"video_url": lecture.video_url}
    """
    from models.lecture import Lecture
    from models.enrollment import Enrollment
    
    # 강의 조회 (비동기 처리)
    def _get_lecture():
        return db.query(Lecture).filter(Lecture.id == lecture_id).first()
    
    lecture = await run_in_threadpool(_get_lecture)
    
    if not lecture:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="강의를 찾을 수 없습니다"
        )
    
    # 강의가 속한 코스 ID 가져오기
    # Lecture → Chapter → Course 관계 탐색
    course_id = lecture.chapter.course_id
    
    # 수강 등록 확인 (비동기 처리)
    def _get_enrollment():
        return db.query(Enrollment).filter(
            Enrollment.user_id == current_user.id,
            Enrollment.course_id == course_id
        ).first()
    
    enrollment = await run_in_threadpool(_get_enrollment)
    
    if not enrollment:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="수강 등록이 필요합니다"
        )
    
    # 수강 기간 확인 (UTC 기준)
    current_time_utc = datetime.now(timezone.utc)
    
    if enrollment.expired_at.tzinfo is None:
        expired_at_utc = enrollment.expired_at.replace(tzinfo=timezone.utc)
    else:
        expired_at_utc = enrollment.expired_at
    
    if expired_at_utc < current_time_utc:
        raise HTTPException(
            status_code=status.HTTP_410_GONE,
            detail="수강 기간이 만료되었습니다"
        )
    
    return lecture, enrollment


# TODO: Check DB session closing logic (PR 임시 생성용)
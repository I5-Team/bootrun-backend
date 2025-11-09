from typing import Optional
from datetime import datetime, timezone
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from jose import JWTError
import logging

from app.core.security import decode_token
from app.core.database import get_db
from app.models.user import User

logger = logging.getLogger(__name__)

security = HTTPBearer()

# ============= 사용자 인증 =============

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db)
) -> User:
    token = credentials.credentials
    
    payload = decode_token(token, token_type='access')
    
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="유효하지 않은 인증 토큰입니다",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user_id = payload.get('sub')
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="토큰에서 사용자 정보를 찾을 수 없습니다",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # 비동기 쿼리
    result = await db.execute(
        select(User).where(User.id == user_id)
    )
    user = result.scalar_one_or_none()
    
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="사용자를 찾을 수 없습니다",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="비활성화된 계정입니다"
        )
    
    return user

async def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    return current_user

# ============= 권한 확인 =============

async def get_current_admin(
    current_user: User = Depends(get_current_user)
) -> User:
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="관리자 권한이 필요합니다"
        )
    return current_user

async def get_current_instructor(
    current_user: User = Depends(get_current_user)
) -> User:
    if not (current_user.is_admin or getattr(current_user, 'is_instructor', False)):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="강사 또는 관리자 권한이 필요합니다"
        )
    return current_user

# ============= 선택적 인증 =============

async def get_current_user_optional(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(
        HTTPBearer(auto_error=False)
    ),
    db: AsyncSession = Depends(get_db)
) -> Optional[User]:
    if credentials is None:
        return None
    
    try:
        token = credentials.credentials
        payload = decode_token(token, token_type='access')
        
        if payload is None:
            return None
        
        user_id = payload.get('sub')
        if user_id is None:
            return None
        
        result = await db.execute(
            select(User).where(User.id == user_id)
        )
        user = result.scalar_one_or_none()
        
        if user is None or not user.is_active:
            return None
        
        return user
        
    except (JWTError, HTTPException):
        return None
    except Exception as e:
        logger.error(f'선택적 인증 오류: {e}', exc_info=True)
        return None

# ============= 수강 권한 확인 =============

async def verify_enrollment_access(
    course_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    from app.models.progress import Enrollment
    
    result = await db.execute(
        select(Enrollment).where(
            Enrollment.user_id == current_user.id,
            Enrollment.course_id == course_id
        )
    )
    enrollment = result.scalar_one_or_none()
    
    if not enrollment:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="수강 등록이 필요합니다"
        )
    
    current_time_utc = datetime.now(timezone.utc)
    expired_at_utc = enrollment.expired_at.replace(tzinfo=timezone.utc) \
        if enrollment.expired_at.tzinfo is None else enrollment.expired_at
    
    if expired_at_utc < current_time_utc:
        raise HTTPException(
            status_code=status.HTTP_410_GONE,
            detail="수강 기간이 만료되었습니다"
        )
    
    return enrollment

# ============= 리소스 소유권 확인 =============

async def verify_resource_owner(
    resource_user_id: int,
    current_user: User = Depends(get_current_user)
) -> User:
    if current_user.is_admin:
        return current_user
    
    if current_user.id != resource_user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="본인의 게시물만 수정/삭제할 수 있습니다"
        )
    
    return current_user

# ============= 페이지네이션 =============

def get_pagination_params(
    page: int = 1,
    page_size: int = 20
):
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

# ============= 강의 접근 권한 확인 =============

async def verify_lecture_access(
    lecture_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    from app.models.course import Lecture
    from app.models.progress import Enrollment
    
    result = await db.execute(
        select(Lecture).where(Lecture.id == lecture_id)
    )
    lecture = result.scalar_one_or_none()
    
    if not lecture:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="강의를 찾을 수 없습니다"
        )
    
    course_id = lecture.chapter.course_id
    
    result = await db.execute(
        select(Enrollment).where(
            Enrollment.user_id == current_user.id,
            Enrollment.course_id == course_id
        )
    )
    enrollment = result.scalar_one_or_none()
    
    if not enrollment:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="수강 등록이 필요합니다"
        )
    
    current_time_utc = datetime.now(timezone.utc)
    expired_at_utc = enrollment.expired_at.replace(tzinfo=timezone.utc) \
        if enrollment.expired_at.tzinfo is None else enrollment.expired_at
    
    if expired_at_utc < current_time_utc:
        raise HTTPException(
            status_code=status.HTTP_410_GONE,
            detail="수강 기간이 만료되었습니다"
        )
    
    return lecture, enrollment
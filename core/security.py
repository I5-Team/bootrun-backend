from datetime import datetime, timedelta, timezone
from typing import Optional

from jose import JWTError, jwt
from passlib.context import CryptContext

from core.config import settings

# bcrypt를 사용하는 비밀번호 해싱 컨텍스트
pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')


def hash_password(password: str) -> str:
    """
    bcrypt를 사용하여 일반 텍스트 비밀번호 해시

    Args:
        password: 해시할 일반 텍스트 비밀번호

    Returns:
        해시된 비밀번호 문자열
    """
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    일반 텍스트 비밀번호를 해시된 비밀번호와 비교하여 확인

    Args:
        plain_password: 확인할 일반 텍스트 비밀번호
        hashed_password: 비교하기 이전의 해시된 비밀번호

    Returns:
        비밀번호가 일치하면 True, 그렇지 않으면 False
    """
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    JWT 엑세스 토큰(Access Token) 생성

    Args:
        data: 토큰 클레임(예: {'sub': user_id})이 포함된 딕셔너리
        expires_delta: 선택적(Optional) 사용자 지정 만료 시간. 제공되지 않을 시,
                      설정(settings)의 JWT_ACCESS_TOKEN_EXPIRE_MINUTES 를 사용

    Returns:
        인코딩된 JWT 토큰 문자열
    """
    to_encode = data.copy()

    # 만료 시간 설정
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(
            minutes=settings.jwt_access_token_expire_minutes
        )

    # type 및 iss 클레임
    to_encode.update({
        'type': 'access',           # 엑세스 토큰 명시
        'iss': 'bootrun-backend'    # 발급자 명시
    })

    # 토큰 인코딩
    encoded_jwt = jwt.encode(
        to_encode,
        settings.jwt_secret_key,
        algorithm=settings.jwt_algorithm,
    )

    return encoded_jwt


def create_refresh_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    JWT 갱신 토큰(Refresh Token) 생성

    Args:
        data: 토큰 클레임(예: {'sub': user_id})이 포함된 딕셔너리
        expires_delta: 선택적(Optional) 사용자 지정 만료 시간. 제공되지 않으면,
                       설정(settings)의 **JWT_REFRESH_TOKEN_EXPIRE_DAYS**를 사용

    Returns:
        인코딩된 JWT 토큰 문자열
    """
    to_encode = data.copy()

    # 만료 시간 설정
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(
            days=settings.jwt_refresh_token_expire_days
        )

    to_encode.update({'exp': expire})

    # type 및 iss 클레임
    to_encode.update({
        'type': 'refresh',           # refresh 토큰 명시
        'iss': 'bootrun-backend'    # 발급자 명시
    })

    # 토큰 인코딩
    encoded_jwt = jwt.encode(
        to_encode,
        settings.jwt_secret_key,
        algorithm=settings.jwt_algorithm,
    )

    return encoded_jwt


def decode_token(token: str, token_type: str) -> Optional[dict]:
    """
    JWT 토큰을 디코딩하고 확인(verify)하며, 토큰 타입을 검증

    Args:
        token: 디코딩할 JWT 토큰 문자열
        token_type: 예상되는 토큰 타입 ('access' 또는 'refresh')

    Returns:
        유효한 경우 토큰 클레임이 포함된 딕셔너리, 유효하지 않은 경우 None
    """
    try:
        payload = jwt.decode(
            token,
            settings.jwt_secret_key,
            algorithms=[settings.jwt_algorithm],
        )

        # 토큰 타입 클레임 검증
        if payload.get('type') != token_type:
            # 예상한 토큰 타입이 아니면 (예: 엑세스 토큰이 필요한데 갱신 토큰이 들어옴)
            return None 

        # 발급자(iss) 클레임 검증 (선택적)
        if payload.get('iss') != 'bootrun-backend':
            return None

        # 기타 필수 클레임 확인 (예: sub 클레임)
        if 'sub' not in payload:
            return None

        return payload
    except JWTError:
        return None
from datetime import datetime, timedelta, timezone
from typing import Optional

from jose import JWTError, jwt
from passlib.context import CryptContext
from cryptography.fernet import Fernet

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


def create_email_verification_token(user_id: int) -> str:
    """
    이메일 검증용 JWT 토큰 생성 (24시간 유효)

    Args:
        user_id: 사용자 ID

    Returns:
        인코딩된 JWT 토큰 문자열
    """
    to_encode = {'sub': user_id}
    expire = datetime.now(timezone.utc) + timedelta(hours=24)

    to_encode.update({
        'exp': expire,
        'type': 'email_verification',
        'iss': 'bootrun-backend'
    })

    encoded_jwt = jwt.encode(
        to_encode,
        settings.jwt_secret_key,
        algorithm=settings.jwt_algorithm,
    )

    return encoded_jwt


def verify_email_verification_token(token: str) -> Optional[int]:
    """
    이메일 검증 토큰을 검증하고 사용자 ID 추출

    Args:
        token: 검증할 이메일 검증 토큰

    Returns:
        유효한 경우 사용자 ID, 유효하지 않은 경우 None
    """
    try:
        payload = jwt.decode(
            token,
            settings.jwt_secret_key,
            algorithms=[settings.jwt_algorithm],
        )

        if payload.get('type') != 'email_verification':
            return None

        if payload.get('iss') != 'bootrun-backend':
            return None

        user_id = payload.get('sub')
        if user_id is None:
            return None

        return user_id
    except JWTError:
        return None


def create_password_reset_token(user_id: int) -> str:
    """
    비밀번호 재설정용 JWT 토큰 생성 (30분 유효)

    Args:
        user_id: 사용자 ID

    Returns:
        인코딩된 JWT 토큰 문자열
    """
    to_encode = {'sub': user_id}
    expire = datetime.now(timezone.utc) + timedelta(
        minutes=settings.jwt_reset_password_token_expire_minutes
    )

    to_encode.update({
        'exp': expire,
        'type': 'password_reset',
        'iss': 'bootrun-backend'
    })

    encoded_jwt = jwt.encode(
        to_encode,
        settings.jwt_secret_key,
        algorithm=settings.jwt_algorithm,
    )

    return encoded_jwt


def verify_password_reset_token(token: str) -> Optional[int]:
    """
    비밀번호 재설정 토큰을 검증하고 사용자 ID 추출

    Args:
        token: 검증할 비밀번호 재설정 토큰

    Returns:
        유효한 경우 사용자 ID, 유효하지 않은 경우 None
    """
    try:
        payload = jwt.decode(
            token,
            settings.jwt_secret_key,
            algorithms=[settings.jwt_algorithm],
        )

        if payload.get('type') != 'password_reset':
            return None

        if payload.get('iss') != 'bootrun-backend':
            return None

        user_id = payload.get('sub')
        if user_id is None:
            return None

        return user_id
    except JWTError:
        return None


def encrypt_data(data: str) -> str:
    """
    Fernet을 사용하여 데이터 암호화

    Args:
        data: 암호화할 일반 텍스트 데이터

    Returns:
        암호화된 데이터 문자열
    """
    cipher = Fernet(settings.fernet_key.encode() if isinstance(settings.fernet_key, str) else settings.fernet_key)
    encrypted = cipher.encrypt(data.encode())

    return encrypted.decode()


def decrypt_data(encrypted_data: str) -> str:
    """
    Fernet을 사용하여 데이터 복호화

    Args:
        encrypted_data: 복호화할 암호화된 데이터

    Returns:
        복호화된 일반 텍스트 데이터
    """
    cipher = Fernet(settings.fernet_key.encode() if isinstance(settings.fernet_key, str) else settings.fernet_key)
    decrypted = cipher.decrypt(encrypted_data.encode())

    return decrypted.decode()


def check_login_attempts(user_id: int, redis_client) -> None:
    """
    사용자의 로그인 시도 횟수 확인 (최대 5회 제한)

    Args:
        user_id: 사용자 ID
        redis_client: Redis 클라이언트 인스턴스

    Raises:
        Exception: 로그인 시도 횟수가 5회를 초과한 경우 예외 발생
    """
    key = f"login_attempts:{user_id}"
    attempts = redis_client.get(key)

    if attempts and int(attempts) >= 5:
        raise Exception("로그인 시도 횟수를 초과했습니다. 나중에 다시 시도해주세요.")


def increment_login_attempts(user_id: int, redis_client) -> None:
    """
    사용자의 로그인 시도 횟수 증가 (TTL: 15분)

    Args:
        user_id: 사용자 ID
        redis_client: Redis 클라이언트 인스턴스
    """
    key = f"login_attempts:{user_id}"
    attempts = redis_client.get(key)

    if attempts:
        redis_client.incr(key)
    else:
        redis_client.setex(key, 900, 1)  # 900초 = 15분


def reset_login_attempts(user_id: int, redis_client) -> None:
    """
    사용자의 로그인 시도 횟수 초기화

    Args:
        user_id: 사용자 ID
        redis_client: Redis 클라이언트 인스턴스
    """
    key = f"login_attempts:{user_id}"
    redis_client.delete(key)
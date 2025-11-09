from datetime import datetime, timedelta, timezone
from typing import Optional

from jose import JWTError, jwt
from passlib.context import CryptContext
from cryptography.fernet import Fernet

from app.core.config import settings

# bcrypt를 사용하는 비밀번호 해싱 컨텍스트
pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()

    # 만료 시간 설정
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(
            minutes=settings.jwt_access_token_expire_minutes
        )

    # exp 클레임
    to_encode.update({'exp': expire})

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
    cipher = Fernet(settings.fernet_key.encode() if isinstance(settings.fernet_key, str) else settings.fernet_key)
    encrypted = cipher.encrypt(data.encode())

    return encrypted.decode()

def decrypt_data(encrypted_data: str) -> str:
    cipher = Fernet(settings.fernet_key.encode() if isinstance(settings.fernet_key, str) else settings.fernet_key)
    decrypted = cipher.decrypt(encrypted_data.encode())

    return decrypted.decode()

def check_login_attempts(user_id: int, redis_client) -> None:
    key = f"login_attempts:{user_id}"
    attempts = redis_client.get(key)

    if attempts and int(attempts) >= 5:
        raise Exception("로그인 시도 횟수를 초과했습니다. 나중에 다시 시도해주세요.")

def increment_login_attempts(user_id: int, redis_client) -> None:
    key = f"login_attempts:{user_id}"
    attempts = redis_client.get(key)

    if attempts:
        redis_client.incr(key)
    else:
        redis_client.setex(key, 900, 1)  # 900초 = 15분

def reset_login_attempts(user_id: int, redis_client) -> None:
    key = f"login_attempts:{user_id}"
    redis_client.delete(key)
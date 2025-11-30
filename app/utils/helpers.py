"""
유틸리티 헬퍼 함수 모듈

이 모듈은 애플리케이션 전역에서 재사용 가능한 헬퍼 함수를 제공합니다.
"""

from datetime import datetime, timezone, date
from typing import Any, Dict, List, Optional, TypeVar, Union, Type
from math import ceil
from enum import Enum
from urllib.parse import urlencode
import re
import pytz

from app.utils.constants import (
    DEFAULT_PAGE,
    DEFAULT_PAGE_SIZE,
    TIMEZONE_KST,
    PASSWORD_PATTERN,
    PATTERN_EMAIL,
)

T = TypeVar('T')


# 날짜/시간 유틸리티

def get_current_utc_datetime():
    """timezone 정보가 없는 UTC datetime 반환 (PostgreSQL TIMESTAMP WITHOUT TIME ZONE 호환)"""
    return datetime.utcnow()


def get_korean_timezone_datetime() -> datetime:
    kst = pytz.timezone(TIMEZONE_KST)
    return datetime.now(kst)


def convert_to_kst(dt: datetime) -> datetime:
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)

    kst = pytz.timezone(TIMEZONE_KST)
    return dt.astimezone(kst)


def convert_to_utc(dt: datetime) -> datetime:
    if dt.tzinfo is None:
        kst = pytz.timezone(TIMEZONE_KST)
        dt = kst.localize(dt)

    return dt.astimezone(timezone.utc)


def calculate_age(birth_date: date) -> int:
    today = date.today()
    
    # 미래 날짜인 경우 0 반환
    if birth_date > today:
        return 0
    
    age = today.year - birth_date.year

    # 생일이 지나지 않았으면 1살 빼기
    if (today.month, today.day) < (birth_date.month, birth_date.day):
        age -= 1

    return age


def is_within_date_range(
    target_date: datetime,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None
) -> bool:
    # 타임존 일관성 확보: 모두 UTC로 변환
    if target_date.tzinfo is None:
        target_date = target_date.replace(tzinfo=timezone.utc)
    
    if start_date:
        if start_date.tzinfo is None:
            start_date = start_date.replace(tzinfo=timezone.utc)
        if target_date < start_date:
            return False
    
    if end_date:
        if end_date.tzinfo is None:
            end_date = end_date.replace(tzinfo=timezone.utc)
        if target_date > end_date:
            return False
    
    return True


def format_datetime_korean(dt: datetime) -> str:
    kst_dt = convert_to_kst(dt)
    return kst_dt.strftime("%Y년 %m월 %d일 %H:%M")


def get_days_until(target_date: datetime) -> int:
    now = get_current_utc_datetime()
    delta = target_date - now
    return delta.days


# 페이지네이션 유틸리티

def calculate_total_pages(total_items: int, page_size: int) -> int:
    if page_size <= 0:
        return 0
    return ceil(total_items / page_size)


def calculate_offset(page: int, page_size: int) -> int:
    if page < 1:
        raise ValueError("page must be greater than or equal to 1")
    return (page - 1) * page_size


def create_paginated_response(
    items: List[T],
    total: int,
    page: int = DEFAULT_PAGE,
    page_size: int = DEFAULT_PAGE_SIZE,
) -> Dict[str, Any]:
    total_pages = calculate_total_pages(total, page_size)

    return {
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": total_pages,
        "items": items,
    }


# 응답 빌더 유틸리티

def success_response(
    message: str,
    data: Optional[Any] = None,
    detail: Optional[str] = None
) -> Dict[str, Any]:
    response = {"message": message}

    if data is not None:
        response["data"] = data

    if detail:
        response["detail"] = detail

    return response


def error_response(
    error: str,
    detail: Optional[str] = None,
    path: Optional[str] = None
) -> Dict[str, Any]:
    response = {"error": error}

    if detail:
        response["detail"] = detail

    if path:
        response["path"] = path

    return response


def list_response(
    items: List[T],
    total: Optional[int] = None
) -> Dict[str, Any]:
    response = {"items": items}

    if total is not None:
        response["total"] = total
    else:
        response["total"] = len(items)

    return response


# 문자열 유틸리티

def truncate_string(text: str, max_length: int, suffix: str = "...") -> str:
    if len(text) <= max_length:
        return text

    if max_length < len(suffix):
        return text[:max_length]

    return text[:max_length - len(suffix)] + suffix


def sanitize_filename(filename: str) -> str:
    # 위험한 문자 제거
    safe_filename = re.sub(r'[^\w\s.-]', '', filename)
    # 공백을 언더스코어로 변환
    safe_filename = safe_filename.replace(' ', '_')
    # 연속된 점 제거
    safe_filename = re.sub(r'\.+', '.', safe_filename)

    return safe_filename


def format_phone_number(phone: str) -> str:
    # 숫자만 추출
    digits = re.sub(r'\D', '', phone)

    # 한국 휴대폰 번호 형식으로 변환
    if len(digits) == 11:
        return f"{digits[:3]}-{digits[3:7]}-{digits[7:]}"
    elif len(digits) == 10:
        return f"{digits[:3]}-{digits[3:6]}-{digits[6:]}"

    return phone


def snake_to_camel(snake_str: str) -> str:
    components = snake_str.split('_')
    return components[0] + ''.join(x.title() for x in components[1:])


def camel_to_snake(camel_str: str) -> str:
    return re.sub(r'(?<!^)(?=[A-Z])', '_', camel_str).lower()


# 검증 유틸리티

def is_valid_email(email: str) -> bool:
    return bool(re.match(PATTERN_EMAIL, email))


def is_valid_password(password: str) -> bool:
    return bool(re.match(PASSWORD_PATTERN, password))


def is_within_range(value: int, min_value: int, max_value: int) -> bool:
    return min_value <= value <= max_value


def validate_file_size(file_size_bytes: int, max_size_mb: int) -> bool:
    max_size_bytes = max_size_mb * 1024 * 1024
    return file_size_bytes <= max_size_bytes


# Redis 키 생성 유틸리티

def build_redis_key(prefix: str, identifier: Any) -> str:
    return f"{prefix}:{identifier}"


def build_cache_key(*parts: Any) -> str:
    return ':'.join(str(part) for part in parts)


# Enum 유틸리티

def enum_to_dict(enum_class: Type[Enum]) -> Dict[str, str]:
    return {item.name: item.value for item in enum_class}


def enum_values_list(enum_class: Type[Enum]) -> List[str]:
    return [item.value for item in enum_class]


def enum_names_list(enum_class: Type[Enum]) -> List[str]:
    return [item.name for item in enum_class]


# 숫자 포맷팅 유틸리티

def format_currency(amount: Union[int, float], currency: str = "KRW") -> str:
    if currency == "KRW":
        return f"{int(amount):,}원"
    elif currency == "USD":
        return f"${amount:,.2f}"
    else:
        return f"{amount:,} {currency}"


def format_percentage(value: float, decimal_places: int = 1) -> str:
    return f"{value:.{decimal_places}f}%"


def format_file_size(size_bytes: int) -> str:
    size = size_bytes
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if size < 1024.0:
            return f"{size:.1f} {unit}"
        size /= 1024.0

    return f"{size:.1f} PB"


# 데이터 변환 유틸리티

def decode_redis_value(value: Optional[Any]) -> Optional[str]:
    """
    Redis에서 가져온 값을 문자열로 변환합니다.

    Args:
        value: Redis에서 가져온 값 (bytes 또는 str)

    Returns:
        str 또는 None (유효하지 않은 UTF-8 바이트 시퀀스인 경우 None 반환)
    """
    if value is None:
        return None

    if isinstance(value, bytes):
        try:
            return value.decode('utf-8')
        except UnicodeDecodeError:
            return None

    if isinstance(value, str):
        return value

    return str(value)


def safe_int(value: Any, default: int = 0) -> int:
    try:
        return int(value)
    except (ValueError, TypeError):
        return default


def safe_float(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except (ValueError, TypeError):
        return default


def safe_bool(value: Any, default: bool = False) -> bool:
    if isinstance(value, bool):
        return value

    if isinstance(value, str):
        return value.lower() in ('true', '1', 'yes', 'on')

    try:
        return bool(value)
    except (ValueError, TypeError):
        return default


# 리스트 유틸리티

def chunk_list(items: List[T], chunk_size: int) -> List[List[T]]:
    return [items[i:i + chunk_size] for i in range(0, len(items), chunk_size)]


def remove_duplicates(items: List[T], key=None) -> List[T]:
    if key is None:
        return list(dict.fromkeys(items))

    seen = set()
    result = []

    for item in items:
        k = key(item)
        if k not in seen:
            seen.add(k)
            result.append(item)

    return result


# 딕셔너리 유틸리티

def filter_none_values(data: Dict[str, Any]) -> Dict[str, Any]:
    return {k: v for k, v in data.items() if v is not None}


def flatten_dict(data: Dict[str, Any], parent_key: str = '', sep: str = '.') -> Dict[str, Any]:
    items = []

    for k, v in data.items():
        new_key = f"{parent_key}{sep}{k}" if parent_key else k

        if isinstance(v, dict):
            items.extend(flatten_dict(v, new_key, sep=sep).items())
        else:
            items.append((new_key, v))

    return dict(items)


# URL 유틸리티

def build_url(base_url: str, path: str, **query_params) -> str:
    url = f"{base_url.rstrip('/')}/{path.lstrip('/')}"

    if query_params:
        filtered_params = filter_none_values(query_params)
        if filtered_params:
            query_string = urlencode(filtered_params)
            url = f"{url}?{query_string}"

    return url

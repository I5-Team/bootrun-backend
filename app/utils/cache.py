import json
import logging
from typing import Optional, Any, Callable
from functools import wraps
from datetime import timedelta

from app.core.redis import get_redis

logger = logging.getLogger(__name__)


class RedisCache:

    def __init__(self):
        self.redis = None

    async def get_redis(self):
        if not self.redis:
            self.redis = await get_redis()
        return self.redis

    async def get(self, key: str) -> Optional[str]:
        try:
            redis = await self.get_redis()
            if not redis:
                return None

            value = await redis.get(key)
            if value:
                if isinstance(value, bytes):
                    value = value.decode('utf-8')
                logger.debug(f"Cache HIT: {key}")
                return value

            logger.debug(f"Cache MISS: {key}")
            return None
        except Exception as e:
            logger.error(f"Redis get error for key {key}: {e}")
            return None

    async def set(
        self,
        key: str,
        value: Any,
        ttl: int = 300  # 기본 5분
    ) -> bool:
        try:
            redis = await self.get_redis()
            if not redis:
                return False

            # dict나 list는 JSON으로 직렬화
            if isinstance(value, (dict, list)):
                value = json.dumps(value, ensure_ascii=False)

            await redis.setex(key, ttl, str(value))
            logger.debug(f"Cache SET: {key} (TTL: {ttl}s)")
            return True
        except Exception as e:
            logger.error(f"Redis set error for key {key}: {e}")
            return False

    async def delete(self, key: str) -> bool:
        try:
            redis = await self.get_redis()
            if not redis:
                return False

            await redis.delete(key)
            logger.debug(f"Cache DELETE: {key}")
            return True
        except Exception as e:
            logger.error(f"Redis delete error for key {key}: {e}")
            return False

    async def delete_pattern(self, pattern: str) -> int:
        try:
            redis = await self.get_redis()
            if not redis:
                return 0

            keys = []
            async for key in redis.scan_iter(match=pattern):
                keys.append(key)

            if keys:
                deleted = await redis.delete(*keys)
                logger.debug(f"Cache DELETE pattern {pattern}: {deleted} keys")
                return deleted
            return 0
        except Exception as e:
            logger.error(f"Redis delete pattern error for {pattern}: {e}")
            return 0


# 전역 캐시 인스턴스
cache = RedisCache()


def cache_key(*args, **kwargs) -> str:
    parts = [str(arg) for arg in args]
    for k, v in sorted(kwargs.items()):
        parts.append(f"{k}={v}")
    return ":".join(parts)


def cached(
    prefix: str,
    ttl: int = 300,  # 5분
    key_builder: Optional[Callable] = None
):
    
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # 캐시 키 생성
            if key_builder:
                key = key_builder(*args, **kwargs)
            else:
                # 기본: prefix:함수명:인자들
                func_name = func.__name__
                key_parts = [prefix, func_name]

                # args에서 self 제외
                filtered_args = [arg for arg in args if not hasattr(arg, '__class__')]
                if filtered_args:
                    key_parts.extend([str(arg) for arg in filtered_args])

                # kwargs 추가
                for k, v in sorted(kwargs.items()):
                    key_parts.append(f"{k}={v}")

                key = ":".join(key_parts)

            # 캐시에서 조회
            cached_value = await cache.get(key)
            if cached_value:
                try:
                    # JSON으로 저장된 경우 파싱
                    return json.loads(cached_value)
                except (json.JSONDecodeError, TypeError):
                    return cached_value

            # 캐시 미스 - 함수 실행
            result = await func(*args, **kwargs)

            # 결과를 캐시에 저장
            if result is not None:
                await cache.set(key, result, ttl)

            return result

        return wrapper
    return decorator


async def invalidate_cache(pattern: str):
    await cache.delete_pattern(pattern)


async def invalidate_course_cache(course_id: Optional[int] = None):
    if course_id:
        # 특정 강의만 무효화
        await cache.delete_pattern(f"course:*:{course_id}*")
        logger.info(f"Invalidated cache for course {course_id}")
    else:
        # 모든 강의 캐시 무효화
        await cache.delete_pattern("course:*")
        logger.info("Invalidated all course caches")


async def invalidate_user_cache(user_id: Optional[int] = None):
    if user_id:
        await cache.delete_pattern(f"user:*:{user_id}*")
        logger.info(f"Invalidated cache for user {user_id}")
    else:
        await cache.delete_pattern("user:*")
        logger.info("Invalidated all user caches")

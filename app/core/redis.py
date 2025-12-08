from redis import asyncio as aioredis
from typing import Optional
import logging

from app.core.config import settings
from app.core.logging_config import configure_logging

logger = configure_logging()

redis_client: Optional[aioredis.Redis] = None


async def get_redis() -> Optional[aioredis.Redis]:
    return redis_client


async def init_redis():
    global redis_client
    try:
        redis_client = aioredis.from_url(
            settings.redis_url,
            decode_responses=True,
            socket_connect_timeout=5,
            socket_timeout=5,
            retry_on_timeout=True,
            health_check_interval=30,
        )
        await redis_client.ping()
        logger.info('Redis 연결 성공')
    except Exception as e:
        logger.error(f'Redis 연결 실패: {e}')
        redis_client = None
        logger.warning('Redis 없이 계속 진행합니다 (캐싱 기능 비활성화)')


async def close_redis():
    global redis_client
    if redis_client:
        await redis_client.aclose()
        logger.info('Redis 연결 종료')

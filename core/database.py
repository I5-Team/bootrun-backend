from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import (
    create_async_engine,
    AsyncSession,
    async_sessionmaker
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.pool import AsyncAdaptedQueuePool
from sqlalchemy import event, text
import redis.asyncio as redis
from redis.asyncio import Redis
import logging

from core.config import settings

logger = logging.getLogger(__name__)

# =====================================================
# AsyncPG 엔진 생성
# =====================================================

async_engine = create_async_engine(
    settings.database_url,
    echo=settings.database_echo,
    poolclass=AsyncAdaptedQueuePool,
    pool_size=settings.database_pool_size,
    max_overflow=settings.database_max_overflow,
    pool_pre_ping=True,
    pool_recycle=3600,
)

# 비동기 세션 메이커
async_session_maker = async_sessionmaker(
    async_engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)

Base = declarative_base()


# =====================================================
# Redis 비동기 클라이언트
# =====================================================

async def get_redis_client() -> Redis:
    """Redis 비동기 클라이언트 반환"""
    try:
        redis_client = redis.Redis(
            host=settings.redis_host,
            port=settings.redis_port,
            db=settings.redis_db,
            password=settings.redis_password,
            socket_timeout=settings.redis_timeout,
            decode_responses=True,
            socket_connect_timeout=settings.redis_timeout,
            health_check_interval=30,
        )
        
        await redis_client.ping()
        logger.info('Redis 연결 성공')
        return redis_client
        
    except redis.ConnectionError as e:
        logger.error(f'Redis 연결 실패: {e}')
        raise


# 전역 Redis 클라이언트 (앱 시작 시 초기화)
redis_client: Redis | None = None


async def init_redis():
    """Redis 초기화 (startup 이벤트에서 호출)"""
    global redis_client
    try:
        redis_client = await get_redis_client()
    except Exception as e:
        logger.warning(f'Redis 초기화 실패, 캐싱 기능 비활성화: {e}')
        redis_client = None


async def close_redis():
    """Redis 연결 종료 (shutdown 이벤트에서 호출)"""
    global redis_client
    if redis_client:
        await redis_client.close()
        logger.info('Redis 연결 종료')


# =====================================================
# 비동기 DB 세션 의존성
# =====================================================

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """비동기 DB 세션 제공"""
    async with async_session_maker() as session:
        try:
            yield session
        finally:
            await session.close()


# =====================================================
# DB 초기화
# =====================================================

async def init_db() -> None:
    """데이터베이스 테이블 생성 (개발용)"""
    try:
        async with async_engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        logger.info('데이터베이스 테이블 생성 완료')
    except Exception as e:
        logger.error(f'데이터베이스 초기화 실패: {e}')
        raise


async def drop_db() -> None:
    """모든 테이블 삭제 (개발용)"""
    if settings.env == 'production':
        raise RuntimeError('프로덕션 환경에서는 테이블 삭제가 금지됩니다')
    
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    logger.warning('모든 데이터베이스 테이블 삭제 완료')


# =====================================================
# 헬스체크
# =====================================================

async def check_db_connection() -> bool:
    """데이터베이스 연결 확인"""
    try:
        async with async_session_maker() as session:
            await session.execute(text('SELECT 1'))
            return True
    except Exception as e:
        logger.error(f'데이터베이스 연결 확인 실패: {e}')
        return False


async def check_redis_connection() -> bool:
    """Redis 연결 확인"""
    if redis_client is None:
        return False
    
    try:
        await redis_client.ping()
        return True
    except Exception as e:
        logger.error(f'Redis 연결 확인 실패: {e}')
        return False


# =====================================================
# 트랜잭션 헬퍼
# =====================================================

class AsyncDatabaseTransaction:
    """비동기 트랜잭션 컨텍스트 매니저"""
    
    def __init__(self):
        self.session: AsyncSession | None = None
    
    async def __aenter__(self) -> AsyncSession:
        self.session = async_session_maker()
        return self.session
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if exc_type is not None:
            await self.session.rollback()
            logger.error(f'트랜잭션 롤백: {exc_type.__name__}: {exc_val}')
        else:
            await self.session.commit()
        
        await self.session.close()
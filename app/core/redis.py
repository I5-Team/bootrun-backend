from redis import asyncio as aioredis
from app.core.config import settings

# 전역 Redis 클라이언트
redis_client = aioredis.from_url(
    settings.redis_url,
    decode_responses=True,
)

# FastAPI 의존성 주입용 함수
async def get_redis():
    return redis_client

# 서버 시작 시 연결 테스트
async def init_redis():
    try:
        await redis_client.ping()
        print("[OK] Redis connection successful")
    except Exception as e:
        print(f"[ERROR] Redis connection failed: {e}")

# 서버 종료 시 연결 종료
async def close_redis():
    await redis_client.aclose()
    print("[OK] Redis connection closed")

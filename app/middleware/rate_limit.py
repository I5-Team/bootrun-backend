from fastapi import Request, Response, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import (
    BaseHTTPMiddleware,
    RequestResponseEndpoint
)
from typing import Dict, Optional
import time
import logging

from app.core.redis import get_redis

logger = logging.getLogger(__name__)


class RateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(
        self,
        app,
        requests_per_minute: int = 60,
        burst_size: int = 10
    ):
        super().__init__(app)
        self.requests_per_minute = requests_per_minute
        self.burst_size = burst_size
        self.window_size = 60

    async def dispatch(
        self,
        request: Request,
        call_next: RequestResponseEndpoint
    ) -> Response:
        redis = await get_redis()

        if not redis:
            return await call_next(request)

        client_ip = self._get_client_ip(request)
        path = request.url.path

        if self._should_skip_rate_limit(path):
            return await call_next(request)

        rate_limit_key = f'rate_limit:{client_ip}:{path}'
        current_time = int(time.time())

        try:
            request_count = await redis.get(rate_limit_key)

            if request_count is None:
                await redis.setex(
                    rate_limit_key,
                    self.window_size,
                    1
                )
                return await call_next(request)

            request_count = int(request_count)

            if request_count >= self.requests_per_minute:
                logger.warning(
                    f'Rate limit exceeded: {client_ip} on {path}'
                )
                return JSONResponse(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    content={
                        'error': 'TOO_MANY_REQUESTS',
                        'detail': '요청 한도를 초과했습니다. 잠시 후 다시 시도해주세요',
                        'retry_after': self.window_size
                    }
                )

            await redis.incr(rate_limit_key)

        except Exception as e:
            logger.error(f'Rate limit check failed: {e}')

        return await call_next(request)

    def _get_client_ip(self, request: Request) -> str:
        forwarded = request.headers.get('X-Forwarded-For')
        if forwarded:
            return forwarded.split(',')[0].strip()
        return request.client.host if request.client else 'unknown'

    def _should_skip_rate_limit(self, path: str) -> bool:
        skip_paths = [
            '/docs',
            '/redoc',
            '/openapi.json',
            '/health',
            '/',
        ]
        return any(path.startswith(p) for p in skip_paths)

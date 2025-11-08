import os
import sys
import logging
from logging.handlers import RotatingFileHandler, TimedRotatingFileHandler
from pathlib import Path
from typing import Optional, Any, Union, Dict, List
from datetime import datetime

from core.config import settings


DETAILED_FORMAT = (
    '%(asctime)s | %(levelname)-8s | %(name)s | '
    '%(funcName)s:%(lineno)d | %(message)s'
)

SIMPLE_FORMAT = (
    '%(asctime)s | %(levelname)-8s | %(message)s'
)

JSON_FORMAT = (
    '{"timestamp": "%(asctime)s", "level": "%(levelname)s", '
    '"logger": "%(name)s", "function": "%(funcName)s", '
    '"line": %(lineno)d, "message": "%(message)s"}'
)

DATE_FORMAT = '%Y-%m-%d %H:%M:%S'


LOG_LEVEL_MAP = {
    'DEBUG': logging.DEBUG,
    'INFO': logging.INFO,
    'WARNING': logging.WARNING,
    'ERROR': logging.ERROR,
    'CRITICAL': logging.CRITICAL,
}


SENSITIVE_FIELD_NAMES = {
    'password', 'passwd', 'pwd',
    'token', 'access_token', 'refresh_token', 'jwt',
    'secret', 'secret_key', 'api_key', 'private_key',
    'credit_card', 'card_number', 'cvv', 'ssn',
    'authorization', 'auth',
}

SENSITIVE_PATTERNS = [
    (r'eyJ[A-Za-z0-9_-]*\.eyJ[A-Za-z0-9_-]*\.[A-Za-z0-9_-]*', '***JWT_TOKEN***'),
    (r'Bearer\s+[A-Za-z0-9_-]+', 'Bearer ***TOKEN***'),
    (r'password["\']?\s*[:=]\s*["\']?[^,\s}"\']+', 'password=***MASKED***'),
    (r'passwd["\']?\s*[:=]\s*["\']?[^,\s}"\']+', 'passwd=***MASKED***'),
    (r'pwd["\']?\s*[:=]\s*["\']?[^,\s}"\']+', 'pwd=***MASKED***'),
    (r'api[_-]?key["\']?\s*[:=]\s*["\']?[A-Za-z0-9_-]{20,}', 'api_key=***MASKED***'),
    (r'\b\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4}\b', '****-****-****-****'),
]


class SensitiveDataFilter(logging.Filter):

    def filter(self, record: logging.LogRecord) -> bool:

        if isinstance(record.msg, str):
            record.msg = self._mask_sensitive_data(record.msg)
        
        if record.args:
            masked_args = []
            for arg in record.args:
                if isinstance(arg, str):
                    masked_args.append(self._mask_sensitive_data(arg))
                elif isinstance(arg, dict):
                    masked_args.append(self._mask_dict(arg))
                else:
                    masked_args.append(arg)
            record.args = tuple(masked_args)
        
        return True
    
    def _mask_sensitive_data(self, text: str) -> str:
        import re
        
        masked_text = text
        
        for pattern, replacement in SENSITIVE_PATTERNS:
            masked_text = re.sub(
                pattern,
                replacement,
                masked_text,
                flags=re.IGNORECASE
            )
        
        return masked_text
    
    def _mask_dict(self, data: dict) -> dict:
        masked = data.copy()
        
        for key, value in masked.items():
            if key.lower() in SENSITIVE_FIELD_NAMES:
                masked[key] = '***MASKED***'
            elif isinstance(value, dict):
                masked[key] = self._mask_dict(value)
            elif isinstance(value, str):
                masked[key] = self._mask_sensitive_data(value)
        
        return masked


def mask_sensitive_info(data: Union[Dict, str, List, Any]) -> Union[Dict, str, List, Any]:
    if isinstance(data, dict):
        return SensitiveDataFilter()._mask_dict(data)
    elif isinstance(data, str):
        return SensitiveDataFilter()._mask_sensitive_data(data)
    elif isinstance(data, list):
        return [mask_sensitive_info(item) for item in data]
    else:
        return data


def create_log_directory() -> Path:
    log_dir = Path(settings.log_file_path).parent
    log_dir.mkdir(parents=True, exist_ok=True)
    return log_dir


def create_console_handler(
    log_level: int = logging.INFO,
    use_colors: bool = True
) -> logging.StreamHandler:
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(log_level)
    
    formatter = logging.Formatter(
        SIMPLE_FORMAT,
        datefmt=DATE_FORMAT
    )
    console_handler.setFormatter(formatter)
    
    console_handler.addFilter(SensitiveDataFilter())
    
    return console_handler


def create_file_handler(
    log_file_path: str,
    log_level: int = logging.INFO,
    max_bytes: int = 100 * 1024 * 1024,
    backup_count: int = 30
) -> RotatingFileHandler:
    file_handler = RotatingFileHandler(
        filename=log_file_path,
        maxBytes=max_bytes,
        backupCount=backup_count,
        encoding='utf-8'
    )
    file_handler.setLevel(log_level)
    
    formatter = logging.Formatter(
        DETAILED_FORMAT,
        datefmt=DATE_FORMAT
    )
    file_handler.setFormatter(formatter)
    
    file_handler.addFilter(SensitiveDataFilter())
    
    return file_handler


def create_timed_file_handler(
    log_file_path: str,
    log_level: int = logging.INFO,
    when: str = 'midnight',
    interval: int = 1,
    backup_count: int = 30
) -> TimedRotatingFileHandler:
    file_handler = TimedRotatingFileHandler(
        filename=log_file_path,
        when=when,
        interval=interval,
        backupCount=backup_count,
        encoding='utf-8'
    )
    file_handler.setLevel(log_level)
    
    formatter = logging.Formatter(
        DETAILED_FORMAT,
        datefmt=DATE_FORMAT
    )
    file_handler.setFormatter(formatter)
    
    file_handler.suffix = '%Y-%m-%d'
    
    file_handler.addFilter(SensitiveDataFilter())
    
    return file_handler


def create_error_file_handler(
    log_level: int = logging.ERROR
) -> RotatingFileHandler:
    log_dir = Path(settings.log_file_path).parent
    error_log_path = log_dir / 'error.log'
    
    error_handler = RotatingFileHandler(
        filename=str(error_log_path),
        maxBytes=settings.log_max_size * 1024 * 1024,
        backupCount=settings.log_retention_days,
        encoding='utf-8'
    )
    error_handler.setLevel(log_level)
    
    formatter = logging.Formatter(
        DETAILED_FORMAT,
        datefmt=DATE_FORMAT
    )
    error_handler.setFormatter(formatter)
    
    error_handler.addFilter(SensitiveDataFilter())
    
    return error_handler


def setup_logger(
    name: str = 'bootrun',
    log_level: Optional[str] = None,
    use_file_logging: bool = True,
    use_console_logging: bool = True,
    use_error_file: bool = True,
    use_timed_rotation: bool = False
) -> logging.Logger:
    if log_level is None:
        log_level = settings.log_level
    
    level = LOG_LEVEL_MAP.get(log_level.upper(), logging.INFO)
    
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    logger.handlers.clear()
    
    if use_file_logging:
        create_log_directory()
    
    if use_console_logging:
        console_handler = create_console_handler(
            log_level=level,
            use_colors=(settings.env == 'development')
        )
        logger.addHandler(console_handler)
    
    if use_file_logging:
        if use_timed_rotation:
            file_handler = create_timed_file_handler(
                log_file_path=settings.log_file_path,
                log_level=level,
                when='midnight',
                interval=1,
                backup_count=settings.log_retention_days
            )
        else:
            file_handler = create_file_handler(
                log_file_path=settings.log_file_path,
                log_level=level,
                max_bytes=settings.log_max_size * 1024 * 1024,
                backup_count=settings.log_retention_days
            )
        logger.addHandler(file_handler)
    
    if use_error_file and use_file_logging:
        error_handler = create_error_file_handler(
            log_level=logging.ERROR
        )
        logger.addHandler(error_handler)
    
    logger.propagate = False
    
    return logger


def configure_logging() -> logging.Logger:
    logger = setup_logger(
        name='bootrun',
        log_level=settings.log_level,
        use_file_logging=True,
        use_console_logging=True,
        use_error_file=True,
        use_timed_rotation=False
    )
    
    uvicorn_access_logger = logging.getLogger('uvicorn.access')
    uvicorn_access_logger.handlers = []
    uvicorn_access_logger.setLevel(logging.INFO)
    
    uvicorn_error_logger = logging.getLogger('uvicorn.error')
    uvicorn_error_logger.handlers = []
    uvicorn_error_logger.setLevel(logging.INFO)
    
    sqlalchemy_logger = logging.getLogger('sqlalchemy.engine')
    if settings.database_echo:
        sqlalchemy_logger.setLevel(logging.INFO)
    else:
        sqlalchemy_logger.setLevel(logging.WARNING)
    
    logger.info('=' * 60)
    logger.info(f'BootRun 로깅 시스템 초기화 완료')
    logger.info(f'환경: {settings.env}')
    logger.info(f'로그 레벨: {settings.log_level}')
    logger.info(f'로그 파일: {settings.log_file_path}')
    logger.info(f'최대 크기: {settings.log_max_size}MB')
    logger.info(f'보관 일수: {settings.log_retention_days}일')
    logger.info('=' * 60)
    
    return logger


class LoggerContext:
    def __init__(
        self,
        logger: logging.Logger,
        request_id: Optional[str] = None,
        user_id: Optional[int] = None
    ):
        self.logger = logger
        self.request_id = request_id
        self.user_id = user_id
    
    def _format_message(self, message: str) -> str:
        context_parts = []
        
        if self.request_id:
            context_parts.append(f'ReqID:{self.request_id}')
        
        if self.user_id:
            context_parts.append(f'UserID:{self.user_id}')
        
        if context_parts:
            context_str = ' | '.join(context_parts)
            return f'[{context_str}] {message}'
        
        return message
    
    def debug(self, message: str, *args, **kwargs):
        self.logger.debug(self._format_message(message), *args, **kwargs)
    
    def info(self, message: str, *args, **kwargs):
        self.logger.info(self._format_message(message), *args, **kwargs)
    
    def warning(self, message: str, *args, **kwargs):
        self.logger.warning(self._format_message(message), *args, **kwargs)
    
    def error(self, message: str, *args, **kwargs):
        self.logger.error(self._format_message(message), *args, **kwargs)
    
    def critical(self, message: str, *args, **kwargs):
        self.logger.critical(self._format_message(message), *args, **kwargs)


main_logger = setup_logger(
    name='bootrun',
    log_level=settings.log_level
)


def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(f'bootrun.{name}')


def log_function_call(func):
    import functools
    
    @functools.wraps(func)
    async def async_wrapper(*args, **kwargs):
        logger = get_logger(func.__module__)
        logger.debug(
            f'함수 호출: {func.__name__}() | '
            f'args={args}, kwargs={kwargs}'
        )
        try:
            result = await func(*args, **kwargs)
            logger.debug(f'함수 완료: {func.__name__}()')
            return result
        except Exception as e:
            logger.error(
                f'함수 에러: {func.__name__}() | {e}',
                exc_info=True
            )
            raise
    
    @functools.wraps(func)
    def sync_wrapper(*args, **kwargs):
        logger = get_logger(func.__module__)
        logger.debug(
            f'함수 호출: {func.__name__}() | '
            f'args={args}, kwargs={kwargs}'
        )
        try:
            result = func(*args, **kwargs)
            logger.debug(f'함수 완료: {func.__name__}()')
            return result
        except Exception as e:
            logger.error(
                f'함수 에러: {func.__name__}() | {e}',
                exc_info=True
            )
            raise
    
    import asyncio
    if asyncio.iscoroutinefunction(func):
        return async_wrapper
    else:
        return sync_wrapper


def test_logging():
    logger = configure_logging()
    
    logger.debug('디버그 메시지 테스트')
    logger.info('정보 메시지 테스트')
    logger.warning('경고 메시지 테스트')
    logger.error('에러 메시지 테스트')
    logger.critical('심각한 에러 메시지 테스트')
    
    context_logger = LoggerContext(
        logger=logger,
        request_id='req-12345',
        user_id=1
    )
    context_logger.info('컨텍스트 로거 테스트')
    
    logger.info('=' * 60)
    logger.info('민감정보 마스킹 테스트')
    logger.info('=' * 60)
    
    logger.info('로그인 시도: email=test@example.com, pass=test123')
    logger.info('password=TestPassword456')
    logger.info('pwd: demo789')
    
    logger.info('토큰: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.TEST.EXAMPLE')
    logger.info('Authorization: Bearer demo-bearer-token-xyz')
    
    logger.info('설정값: app_config=demo_value')
    
    logger.info('결제 정보: 1234-5678-9012-3456')
    
    test_data = {
        'email': 'user@example.com',
        'password': 'demo123',
        'token': 'demo-token-abc',
        'name': '홍길동'
    }
    logger.info(f'사용자 데이터: {mask_sensitive_info(test_data)}')
    
    logger.info('=' * 60)
    logger.info('마스킹 테스트 완료')
    logger.info('=' * 60)


if __name__ == '__main__':
    test_logging()
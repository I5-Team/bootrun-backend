"""
Logging Configuration
로깅 설정 및 로거 초기화

이 모듈은 다음을 제공합니다:
1. 구조화된 로깅 설정 (콘솔, 파일, 에러 로그 분리)
2. 예외 정보 자동 추출 및 포맷팅
3. 요청/응답 로깅 유틸리티
4. 성능 모니터링 데코레이터
"""

import logging
import sys
import time
import traceback
from functools import wraps
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import Any, Callable, Optional
from datetime import datetime


# ============= 로그 디렉토리 생성 =============

LOG_DIR = Path("logs")
LOG_DIR.mkdir(exist_ok=True)


# ============= 커스텀 로그 포맷터 =============

class StructuredFormatter(logging.Formatter):
    """
    구조화된 로그 포맷터
    
    예외 정보를 자동으로 감지하고 포맷팅합니다.
    """
    
    def format(self, record: logging.LogRecord) -> str:
        """로그 레코드를 포맷팅"""
        # 기본 포맷
        log_message = super().format(record)
        
        # 예외 정보가 있으면 추가
        if record.exc_info:
            log_message += f"\n{self.formatException(record.exc_info)}"
        
        return log_message
    
    def formatException(self, exc_info: tuple) -> str:
        """
        예외 정보를 포맷팅
        
        Args:
            exc_info: sys.exc_info() 반환값
            
        Returns:
            포맷팅된 예외 문자열
        """
        exc_type, exc_value, exc_tb = exc_info
        
        # 예외 타입과 메시지
        result = [
            f"Exception Type: {exc_type.__name__}",
            f"Exception Message: {str(exc_value)}"
        ]
        
        # 스택 트레이스
        if exc_tb:
            result.append("Traceback:")
            result.extend(traceback.format_tb(exc_tb))
        
        return "\n".join(result)


# ============= 로거 설정 함수 =============

def setup_logging(
    log_level: str = "INFO",
    log_file: str = "logs/bootrun.log",
    max_bytes: int = 10 * 1024 * 1024,  # 10MB
    backup_count: int = 5,
    enable_console: bool = True
) -> logging.Logger:
    """
    로깅 설정
    
    Args:
        log_level: 로그 레벨 (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: 로그 파일 경로
        max_bytes: 로그 파일 최대 크기 (바이트)
        backup_count: 백업 파일 개수
        enable_console: 콘솔 출력 활성화 여부
    
    Returns:
        설정된 로거
    """
    # 로거 생성
    logger = logging.getLogger("bootrun")
    logger.setLevel(getattr(logging, log_level.upper()))
    
    # 이미 핸들러가 있으면 제거 (중복 방지)
    if logger.handlers:
        logger.handlers.clear()
    
    # 로그 포맷 설정
    log_format = StructuredFormatter(
        fmt=(
            "%(asctime)s | %(levelname)-8s | "
            "%(name)s:%(funcName)s:%(lineno)d | "
            "%(message)s"
        ),
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    
    # 콘솔 핸들러
    if enable_console:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.DEBUG)
        console_handler.setFormatter(log_format)
        logger.addHandler(console_handler)
    
    # 일반 파일 핸들러 (INFO 이상)
    file_handler = RotatingFileHandler(
        log_file,
        maxBytes=max_bytes,
        backupCount=backup_count,
        encoding="utf-8"
    )
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(log_format)
    logger.addHandler(file_handler)
    
    # 에러 파일 핸들러 (ERROR 이상만 별도 기록)
    error_file_handler = RotatingFileHandler(
        "logs/error.log",
        maxBytes=max_bytes,
        backupCount=backup_count,
        encoding="utf-8"
    )
    error_file_handler.setLevel(logging.ERROR)
    error_file_handler.setFormatter(log_format)
    logger.addHandler(error_file_handler)
    
    # 중요 예외 파일 핸들러 (CRITICAL만 별도 기록)
    critical_file_handler = RotatingFileHandler(
        "logs/critical.log",
        maxBytes=max_bytes,
        backupCount=backup_count,
        encoding="utf-8"
    )
    critical_file_handler.setLevel(logging.CRITICAL)
    critical_file_handler.setFormatter(log_format)
    logger.addHandler(critical_file_handler)
    
    logger.info(f"로깅 설정 완료 (Level: {log_level})")
    return logger


# ============= 로거 초기화 =============

logger = setup_logging()


# ============= 로깅 유틸리티 함수 =============

def log_exception(
    exc: Exception,
    message: str = "",
    level: int = logging.ERROR,
    extra_data: Optional[dict] = None
) -> None:
    """
    예외 정보를 상세하게 로깅
    
    Args:
        exc: 발생한 예외
        message: 추가 메시지
        level: 로그 레벨
        extra_data: 추가 데이터 (딕셔너리)
    """
    exc_type = type(exc).__name__
    exc_message = str(exc)
    
    # 로그 메시지 구성
    log_msg_parts = []
    
    if message:
        log_msg_parts.append(message)
    
    log_msg_parts.append(f"Exception: {exc_type}")
    log_msg_parts.append(f"Message: {exc_message}")
    
    if extra_data:
        log_msg_parts.append(f"Extra Data: {extra_data}")
    
    log_msg = " | ".join(log_msg_parts)
    
    # 예외 정보와 함께 로깅
    logger.log(level, log_msg, exc_info=True)


def log_api_request(
    method: str,
    path: str,
    client_host: str = "Unknown",
    user_id: Optional[int] = None,
    **kwargs: Any
) -> None:
    """
    API 요청 로깅
    
    Args:
        method: HTTP 메소드
        path: 요청 경로
        client_host: 클라이언트 IP
        user_id: 사용자 ID (인증된 경우)
        **kwargs: 추가 정보
    """
    log_parts = [
        f"API Request: {method} {path}",
        f"Client: {client_host}"
    ]
    
    if user_id:
        log_parts.append(f"User: {user_id}")
    
    for key, value in kwargs.items():
        log_parts.append(f"{key}: {value}")
    
    logger.info(" | ".join(log_parts))


def log_api_response(
    method: str,
    path: str,
    status_code: int,
    duration_ms: float,
    **kwargs: Any
) -> None:
    """
    API 응답 로깅
    
    Args:
        method: HTTP 메소드
        path: 요청 경로
        status_code: HTTP 상태 코드
        duration_ms: 처리 시간 (밀리초)
        **kwargs: 추가 정보
    """
    log_level = logging.INFO if status_code < 400 else logging.WARNING
    
    log_parts = [
        f"API Response: {method} {path}",
        f"Status: {status_code}",
        f"Duration: {duration_ms:.2f}ms"
    ]
    
    for key, value in kwargs.items():
        log_parts.append(f"{key}: {value}")
    
    logger.log(log_level, " | ".join(log_parts))


def log_database_query(
    query_type: str,
    table: str,
    duration_ms: float,
    rows_affected: Optional[int] = None
) -> None:
    """
    데이터베이스 쿼리 로깅
    
    Args:
        query_type: 쿼리 타입 (SELECT, INSERT, UPDATE, DELETE)
        table: 테이블 명
        duration_ms: 실행 시간 (밀리초)
        rows_affected: 영향받은 행 수
    """
    log_parts = [
        f"DB Query: {query_type} {table}",
        f"Duration: {duration_ms:.2f}ms"
    ]
    
    if rows_affected is not None:
        log_parts.append(f"Rows: {rows_affected}")
    
    # 느린 쿼리 경고 (100ms 이상)
    if duration_ms > 100:
        logger.warning(" | ".join(log_parts) + " | SLOW QUERY")
    else:
        logger.debug(" | ".join(log_parts))


# ============= 데코레이터 =============

def log_execution_time(func: Callable) -> Callable:
    """
    함수 실행 시간을 로깅하는 데코레이터
    
    사용 예시:
    ```python
    @log_execution_time
    def my_function():
        pass
    ```
    """
    @wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        start_time = time.time()
        
        try:
            result = func(*args, **kwargs)
            duration_ms = (time.time() - start_time) * 1000
            
            logger.debug(
                f"Function '{func.__name__}' executed in {duration_ms:.2f}ms"
            )
            
            return result
        
        except Exception as exc:
            duration_ms = (time.time() - start_time) * 1000
            
            logger.error(
                f"Function '{func.__name__}' failed after {duration_ms:.2f}ms",
                exc_info=True
            )
            raise
    
    return wrapper


def log_async_execution_time(func: Callable) -> Callable:
    """
    비동기 함수 실행 시간을 로깅하는 데코레이터
    
    사용 예시:
    ```python
    @log_async_execution_time
    async def my_async_function():
        pass
    ```
    """
    @wraps(func)
    async def wrapper(*args: Any, **kwargs: Any) -> Any:
        start_time = time.time()
        
        try:
            result = await func(*args, **kwargs)
            duration_ms = (time.time() - start_time) * 1000
            
            logger.debug(
                f"Async function '{func.__name__}' executed in {duration_ms:.2f}ms"
            )
            
            return result
        
        except Exception as exc:
            duration_ms = (time.time() - start_time) * 1000
            
            logger.error(
                f"Async function '{func.__name__}' failed after {duration_ms:.2f}ms",
                exc_info=True
            )
            raise
    
    return wrapper


# ============= 컨텍스트 매니저 =============

class LogContext:
    """
    로그 컨텍스트 매니저
    
    특정 작업의 시작과 종료를 로깅합니다.
    
    사용 예시:
    ```python
    with LogContext("사용자 생성"):
        create_user()
    ```
    """
    
    def __init__(
        self,
        operation: str,
        level: int = logging.INFO,
        log_duration: bool = True
    ):
        """
        Args:
            operation: 작업 이름
            level: 로그 레벨
            log_duration: 실행 시간 로깅 여부
        """
        self.operation = operation
        self.level = level
        self.log_duration = log_duration
        self.start_time: Optional[float] = None
    
    def __enter__(self):
        """컨텍스트 시작"""
        self.start_time = time.time()
        logger.log(self.level, f"[START] {self.operation}")
        return self
    
    def __exit__(self, exc_type, exc_value, exc_tb):
        """컨텍스트 종료"""
        if exc_type is not None:
            # 예외 발생 시
            logger.error(
                f"[FAILED] {self.operation}: {exc_type.__name__}: {exc_value}",
                exc_info=True
            )
        else:
            # 정상 종료 시
            if self.log_duration and self.start_time:
                duration_ms = (time.time() - self.start_time) * 1000
                logger.log(
                    self.level,
                    f"[END] {self.operation} (Duration: {duration_ms:.2f}ms)"
                )
            else:
                logger.log(self.level, f"[END] {self.operation}")
        
        # 예외를 다시 발생시키지 않음 (False 반환)
        return False


# ============= 성능 모니터링 =============

class PerformanceMonitor:
    """
    성능 모니터링 유틸리티
    
    사용 예시:
    ```python
    monitor = PerformanceMonitor("데이터 처리")
    monitor.start()
    # ... 작업 수행 ...
    monitor.end()
    ```
    """
    
    def __init__(self, operation: str):
        """
        Args:
            operation: 작업 이름
        """
        self.operation = operation
        self.start_time: Optional[float] = None
        self.end_time: Optional[float] = None
    
    def start(self) -> None:
        """측정 시작"""
        self.start_time = time.time()
        logger.debug(f"[PERF] {self.operation} 시작")
    
    def end(self) -> float:
        """
        측정 종료
        
        Returns:
            경과 시간 (밀리초)
        """
        if self.start_time is None:
            logger.warning(f"[PERF] {self.operation}: start()가 호출되지 않았습니다")
            return 0.0
        
        self.end_time = time.time()
        duration_ms = (self.end_time - self.start_time) * 1000
        
        # 성능 임계값 경고 (1초 이상)
        if duration_ms > 1000:
            logger.warning(
                f"[PERF] {self.operation} 완료 (Duration: {duration_ms:.2f}ms) - SLOW"
            )
        else:
            logger.debug(
                f"[PERF] {self.operation} 완료 (Duration: {duration_ms:.2f}ms)"
            )
        
        return duration_ms
    
    def __enter__(self):
        """컨텍스트 매니저 지원"""
        self.start()
        return self
    
    def __exit__(self, exc_type, exc_value, exc_tb):
        """컨텍스트 매니저 지원"""
        self.end()
        return False


# ============= 사용 예시 =============

if __name__ == "__main__":
    # 기본 로깅
    logger.info("애플리케이션 시작")
    logger.debug("디버그 메시지")
    logger.warning("경고 메시지")
    logger.error("에러 메시지")
    
    # 예외 로깅
    try:
        raise ValueError("테스트 예외")
    except Exception as e:
        log_exception(e, "예외 발생", extra_data={"user_id": 123})
    
    # API 로깅
    log_api_request("POST", "/api/users", "127.0.0.1", user_id=123)
    log_api_response("POST", "/api/users", 201, 45.67)
    
    # 데코레이터 사용
    @log_execution_time
    def test_function():
        time.sleep(0.1)
        return "완료"
    
    test_function()
    
    # 컨텍스트 매니저 사용
    with LogContext("테스트 작업"):
        time.sleep(0.05)
    
    # 성능 모니터링
    with PerformanceMonitor("데이터 처리"):
        time.sleep(0.2)
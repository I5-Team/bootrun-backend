"""
Exception Handlers
전역 예외 처리 핸들러 및 로깅

"""

import os
import logging
import traceback
from typing import Union

from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError, HTTPException
from pydantic import ValidationError

from .base import BaseAPIException


# 로거 설정
logger = logging.getLogger('bootrun')

# 환경 변수 (개발/운영 환경 구분)
IS_DEBUG = os.getenv('DEBUG', 'False').lower() in ('true', '1', 'yes')


# ============= 1. 커스텀 예외 핸들러 =============

async def custom_exception_handler(
    request: Request,
    exc: BaseAPIException
) -> JSONResponse:
    """
    커스텀 예외 처리 핸들러
    
    BaseAPIException을 상속한 모든 예외를 처리합니다.
    예: LoginFailedError, CourseNotFoundError 등
    
    Args:
        request: FastAPI Request 객체
        exc: 발생한 커스텀 예외
    
    Returns:
        JSONResponse: 에러 응답
    """
    # 에러 로깅
    client_host = request.client.host if request.client else 'Unknown'
    logger.error(
        f'[{exc.error_code}] {exc.detail} | '
        f'Path: {request.url.path} | '
        f'Method: {request.method} | '
        f'Client: {client_host}'
    )
    
    # 에러 응답
    return JSONResponse(
        status_code=exc.status_code,
        content={
            'error': exc.error_code,
            'detail': exc.detail,
            'path': str(request.url.path),
        }
    )


# ============= 2. HTTP 예외 핸들러 =============

async def http_exception_handler(
    request: Request,
    exc: HTTPException
) -> JSONResponse:
    """
    FastAPI HTTP 예외 처리 핸들러
    
    raise HTTPException()으로 발생한 예외를 처리합니다.
    
    Args:
        request: FastAPI Request 객체
        exc: 발생한 HTTP 예외
    
    Returns:
        JSONResponse: 에러 응답
    """
    # 에러 로깅
    log_level = (
        logging.WARNING if exc.status_code < 500
        else logging.ERROR
    )
    logger.log(
        log_level,
        f'[HTTP_EXCEPTION:{exc.status_code}] {exc.detail} | '
        f'Path: {request.url.path} | '
        f'Method: {request.method}'
    )
    
    # 에러 응답
    return JSONResponse(
        status_code=exc.status_code,
        content={
            'error': 'HTTP_EXCEPTION',
            'detail': exc.detail,
            'path': str(request.url.path),
        }
    )


# ============= 3. 유효성 검증 예외 핸들러 =============

async def validation_exception_handler(
    request: Request,
    exc: Union[RequestValidationError, ValidationError]
) -> JSONResponse:
    """
    Pydantic 유효성 검증 예외 처리 핸들러
    
    요청 본문, 쿼리 파라미터, 경로 파라미터 등의 유효성 검증 실패를 처리합니다.
    
    Args:
        request: FastAPI Request 객체
        exc: 발생한 유효성 검증 예외
    
    Returns:
        JSONResponse: 에러 응답
    """
    # 에러 상세 정보 추출 (Pydantic 표준 형식 유지)
    errors = []
    for error in exc.errors():
        errors.append({
            'loc': error['loc'],
            'msg': error['msg'],
            'type': error['type'],
        })
    
    # 에러 로깅
    logger.warning(
        f'[VALIDATION_ERROR] 유효성 검사 실패 | '
        f'Path: {request.url.path} | '
        f'Method: {request.method} | '
        f'Errors: {errors}'
    )
    
    # 에러 응답
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            'error': 'VALIDATION_ERROR',
            'detail': '입력값이 올바르지 않습니다',
            'errors': errors,
            'path': str(request.url.path),
        }
    )


# ============= 4. 일반 예외 핸들러 (Catch-all) =============

async def general_exception_handler(
    request: Request,
    exc: Exception
) -> JSONResponse:
    """
    예상치 못한 일반 예외 처리 핸들러
    
    위의 핸들러들로 처리되지 않은 모든 예외를 처리합니다.
    개발 환경에서는 상세한 에러 정보를 포함하고,
    운영 환경에서는 숨깁니다.
    
    Args:
        request: FastAPI Request 객체
        exc: 발생한 일반 예외
    
    Returns:
        JSONResponse: 에러 응답
    """
    # 상세한 에러 정보 로깅 (스택 트레이스 포함)
    client_host = request.client.host if request.client else 'Unknown'
    logger.critical(
        f'[UNHANDLED_EXCEPTION] {type(exc).__name__}: {str(exc)} | '
        f'Path: {request.url.path} | '
        f'Method: {request.method} | '
        f'Client: {client_host}\n'
        f'Traceback: {traceback.format_exc()}'
    )
    
    # 기본 응답 내용
    response_content: dict = {
        'error': 'INTERNAL_SERVER_ERROR',
        'detail': '서버 오류가 발생했습니다. 관리자에게 문의하세요.',
        'path': str(request.url.path),
    }
    
    # 개발 환경에서만 상세 정보 포함
    if IS_DEBUG:
        response_content['debug_info'] = {
            'exception_type': type(exc).__name__,
            'exception_message': str(exc),
            'traceback': traceback.format_exc().split('\n')
        }
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=response_content
    )


# ============= 핸들러 등록 함수 =============

def register_exception_handlers(app: FastAPI) -> None:
    """
    FastAPI 앱에 모든 예외 핸들러를 등록합니다.
    
    사용법:
        from core.exceptions.handlers import register_exception_handlers
        
        app = FastAPI()
        register_exception_handlers(app)
    
    Args:
        app: FastAPI 애플리케이션 인스턴스
    """
    # 1. 커스텀 예외 핸들러
    app.add_exception_handler(
        BaseAPIException,
        custom_exception_handler
    )
    
    # 2. HTTP 예외 핸들러
    app.add_exception_handler(
        HTTPException,
        http_exception_handler
    )
    
    # 3. 유효성 검증 예외 핸들러
    app.add_exception_handler(
        RequestValidationError,
        validation_exception_handler
    )
    
    # 4. 일반 예외 핸들러 (catch-all)
    app.add_exception_handler(
        Exception,
        general_exception_handler
    )
    
    logger.info(
        f'모든 예외 핸들러가 등록되었습니다 (IS_DEBUG={IS_DEBUG})'
    )
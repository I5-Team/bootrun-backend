"""
Domain-specific Error Responses
도메인별 에러 응답 템플릿

"""

# ============= 헬퍼 함수 (중복 방지용) =============

def _make_error_response(
    error_code: str,
    detail: str,
    description: str | None = None
) -> dict:
    """에러 응답 템플릿 생성"""
    return {
        'description': description or detail,
        'content': {
            'application/json': {
                'example': {
                    'error': error_code,
                    'detail': detail
                }
            }
        }
    }


# ============= 공통 에러 응답 =============

COMMON_400 = _make_error_response(
    'BAD_REQUEST',
    '잘못된 요청입니다'
)

COMMON_401 = _make_error_response(
    'UNAUTHORIZED',
    '인증이 필요합니다'
)

COMMON_403 = _make_error_response(
    'FORBIDDEN',
    '접근 권한이 없습니다'
)

COMMON_404 = _make_error_response(
    'NOT_FOUND',
    '요청한 리소스를 찾을 수 없습니다'
)

COMMON_409 = _make_error_response(
    'CONFLICT',
    '리소스 충돌이 발생했습니다'
)

COMMON_410 = _make_error_response(
    'GONE',
    '리소스를 더 이상 사용할 수 없습니다'
)

COMMON_422 = {
    'description': '유효성 검사 실패',
    'content': {
        'application/json': {
            'example': {
                'error': 'VALIDATION_ERROR',
                'detail': '입력값이 올바르지 않습니다',
                'errors': [
                    {
                        'loc': ['body', 'email'],
                        'msg': '유효한 이메일 주소를 입력하세요',
                        'type': 'value_error.email'
                    }
                ],
                'path': '/api/users/register'
            }
        }
    }
}

COMMON_500 = _make_error_response(
    'INTERNAL_SERVER_ERROR',
    '서버 오류가 발생했습니다'
)


# ============= 인증/회원 관련 =============

LOGIN_RESPONSES = {
    401: _make_error_response(
        'LOGIN_FAILED',
        '이메일 또는 비밀번호가 일치하지 않습니다',
        '로그인 실패'
    ),
    422: COMMON_422,
    500: COMMON_500,
}

REGISTER_RESPONSES = {
    400: _make_error_response(
        'EMAIL_ALREADY_EXISTS',
        '이미 존재하는 이메일입니다',
        '회원가입 실패'
    ),
    422: COMMON_422,
    500: COMMON_500,
}

EMAIL_VERIFICATION_RESPONSES = {
    400: _make_error_response(
        'VERIFICATION_CODE_INVALID',
        '인증 코드가 올바르지 않습니다',
        '이메일 인증 실패'
    ),
    422: COMMON_422,
    500: COMMON_500,
}

PASSWORD_RESET_RESPONSES = {
    400: _make_error_response(
        'RESET_TOKEN_INVALID',
        '유효하지 않은 재설정 토큰입니다',
        '비밀번호 재설정 실패'
    ),
    404: COMMON_404,
    422: COMMON_422,
    500: COMMON_500,
}

USER_UPDATE_RESPONSES = {
    401: COMMON_401,
    403: COMMON_403,
    404: COMMON_404,
    422: COMMON_422,
    500: COMMON_500,
}


# ============= 강의 관련 =============

COURSE_CREATE_RESPONSES = {
    400: _make_error_response(
        'COURSE_CREATE_FAILED',
        '이미 존재하는 강의명입니다',
        '강의 생성 실패'
    ),
    401: COMMON_401,
    403: COMMON_403,
    422: COMMON_422,
    500: COMMON_500,
}

COURSE_UPDATE_RESPONSES = {
    400: COMMON_400,
    401: COMMON_401,
    403: COMMON_403,
    404: COMMON_404,
    422: COMMON_422,
    500: COMMON_500,
}

COURSE_LIST_RESPONSES = {
    422: COMMON_422,
    500: COMMON_500,
}

COURSE_DETAIL_RESPONSES = {
    404: _make_error_response(
        'COURSE_NOT_FOUND',
        '강의를 찾을 수 없습니다',
        '강의 조회 실패'
    ),
    422: COMMON_422,
    500: COMMON_500,
}

CHAPTER_CREATE_RESPONSES = {
    401: COMMON_401,
    403: COMMON_403,
    404: _make_error_response(
        'COURSE_NOT_FOUND',
        '강의를 찾을 수 없습니다',
        '챕터 생성 실패'
    ),
    422: COMMON_422,
    500: COMMON_500,
}

CHAPTER_DETAIL_RESPONSES = {
    404: {
        'description': '강의 또는 챕터를 찾을 수 없음',
        'content': {
            'application/json': {
                'examples': {
                    'course_not_found': {
                        'value': {
                            'error': 'COURSE_NOT_FOUND',
                            'detail': '강의를 찾을 수 없습니다'
                        }
                    },
                    'chapter_not_found': {
                        'value': {
                            'error': 'CHAPTER_NOT_FOUND',
                            'detail': '챕터를 찾을 수 없습니다'
                        }
                    }
                }
            }
        }
    },
    422: COMMON_422,
    500: COMMON_500,
}

LECTURE_CREATE_RESPONSES = {
    401: COMMON_401,
    403: COMMON_403,
    404: _make_error_response(
        'CHAPTER_NOT_FOUND',
        '챕터를 찾을 수 없습니다',
        '강의 영상 생성 실패'
    ),
    422: COMMON_422,
    500: COMMON_500,
}

LECTURE_LIST_RESPONSES = {
    404: {
        'description': '강의 또는 챕터를 찾을 수 없음',
        'content': {
            'application/json': {
                'examples': {
                    'course_not_found': {
                        'value': {
                            'error': 'COURSE_NOT_FOUND',
                            'detail': '강의를 찾을 수 없습니다'
                        }
                    },
                    'chapter_not_found': {
                        'value': {
                            'error': 'CHAPTER_NOT_FOUND',
                            'detail': '챕터를 찾을 수 없습니다'
                        }
                    }
                }
            }
        }
    },
    422: COMMON_422,
    500: COMMON_500,
}

LECTURE_DETAIL_RESPONSES = {
    403: _make_error_response(
        'ENROLLMENT_REQUIRED',
        '수강 등록이 필요합니다',
        '수강 권한 없음'
    ),
    404: {
        'description': '강의, 챕터 또는 강의 영상을 찾을 수 없음',
        'content': {
            'application/json': {
                'examples': {
                    'course_not_found': {
                        'value': {
                            'error': 'COURSE_NOT_FOUND',
                            'detail': '강의를 찾을 수 없습니다'
                        }
                    },
                    'chapter_not_found': {
                        'value': {
                            'error': 'CHAPTER_NOT_FOUND',
                            'detail': '챕터를 찾을 수 없습니다'
                        }
                    },
                    'lecture_not_found': {
                        'value': {
                            'error': 'LECTURE_NOT_FOUND',
                            'detail': '강의 영상을 찾을 수 없습니다'
                        }
                    }
                }
            }
        }
    },
    410: _make_error_response(
        'ENROLLMENT_EXPIRED',
        '수강 기간이 만료되었습니다',
        '수강 기간 만료'
    ),
    422: COMMON_422,
    500: COMMON_500,
}


# ============= Q&A 관련 =============

QNA_CREATE_RESPONSES = {
    401: COMMON_401,
    403: _make_error_response(
        'ENROLLMENT_REQUIRED',
        '수강 중인 강의에만 질문할 수 있습니다',
        '질문 작성 권한 없음'
    ),
    422: COMMON_422,
    500: COMMON_500,
}

QNA_UPDATE_RESPONSES = {
    401: COMMON_401,
    403: _make_error_response(
        'ONLY_AUTHOR_CAN_MODIFY',
        '본인이 작성한 질문만 수정할 수 있습니다',
        '수정 권한 없음'
    ),
    404: COMMON_404,
    422: COMMON_422,
    500: COMMON_500,
}

COMMENT_CREATE_RESPONSES = {
    401: COMMON_401,
    403: _make_error_response(
        'ADMIN_ONLY',
        '관리자만 답변할 수 있습니다',
        '답변 권한 없음'
    ),
    404: _make_error_response(
        'QUESTION_NOT_FOUND',
        '질문을 찾을 수 없습니다',
        '질문 조회 실패'
    ),
    422: COMMON_422,
    500: COMMON_500,
}


# ============= 수강 등록 관련 =============

ENROLLMENT_CREATE_RESPONSES = {
    400: _make_error_response(
        'ALREADY_ENROLLED',
        '이미 등록한 강의입니다',
        '수강 등록 실패'
    ),
    401: COMMON_401,
    403: COMMON_403,
    404: _make_error_response(
        'COURSE_NOT_FOUND',
        '강의를 찾을 수 없습니다',
        '수강 등록 실패'
    ),
    422: COMMON_422,
    500: COMMON_500,
}

ENROLLMENT_ACCESS_RESPONSES = {
    401: COMMON_401,
    403: _make_error_response(
        'ENROLLMENT_REQUIRED',
        '수강 등록이 필요합니다',
        '수강 권한 없음'
    ),
    410: _make_error_response(
        'ENROLLMENT_EXPIRED',
        '수강 기간이 만료되었습니다',
        '수강 기간 만료'
    ),
    422: COMMON_422,
    500: COMMON_500,
}

ENROLLMENT_CANCEL_RESPONSES = {
    400: _make_error_response(
        'CANCELLATION_NOT_ALLOWED',
        '환불 가능 기간이 지났습니다',
        '수강 취소 불가'
    ),
    401: COMMON_401,
    403: COMMON_403,
    404: COMMON_404,
    422: COMMON_422,
    500: COMMON_500,
}

PROGRESS_UPDATE_RESPONSES = {
    401: COMMON_401,
    403: _make_error_response(
        'ENROLLMENT_REQUIRED',
        '수강 등록된 강의만 학습 기록을 남길 수 있습니다',
        '학습 진행 권한 없음'
    ),
    404: _make_error_response(
        'LECTURE_NOT_FOUND',
        '강의를 찾을 수 없습니다',
        '학습 진행 실패'
    ),
    422: COMMON_422,
    500: COMMON_500,
}


# ============= 미션 관련 =============

MISSION_CREATE_RESPONSES = {
    401: COMMON_401,
    403: COMMON_403,
    404: _make_error_response(
        'COURSE_NOT_FOUND',
        '강의를 찾을 수 없습니다',
        '미션 생성 실패'
    ),
    422: COMMON_422,
    500: COMMON_500,
}

MISSION_SUBMIT_RESPONSES = {
    400: _make_error_response(
        'MAX_ATTEMPTS_EXCEEDED',
        '최대 제출 횟수를 초과했습니다',
        '미션 제출 실패'
    ),
    401: COMMON_401,
    403: _make_error_response(
        'ENROLLMENT_REQUIRED',
        '해당 강의를 수강하지 않았습니다',
        '미션 제출 권한 없음'
    ),
    404: _make_error_response(
        'MISSION_NOT_FOUND',
        '미션을 찾을 수 없습니다',
        '미션 제출 실패'
    ),
    422: COMMON_422,
    500: COMMON_500,
}


# ============= 결제 관련 =============

PAYMENT_CREATE_RESPONSES = {
    400: _make_error_response(
        'ALREADY_PAID',
        '이미 결제한 강의입니다',
        '결제 실패'
    ),
    401: COMMON_401,
    403: COMMON_403,
    404: _make_error_response(
        'COURSE_NOT_FOUND',
        '강의를 찾을 수 없습니다',
        '결제 실패'
    ),
    422: COMMON_422,
    500: COMMON_500,
}

PAYMENT_CONFIRM_RESPONSES = {
    400: _make_error_response(
        'PAYMENT_CONFIRM_FAILED',
        '결제 확인에 실패했습니다',
        '결제 확인 실패'
    ),
    401: COMMON_401,
    403: COMMON_403,
    404: COMMON_404,
    422: COMMON_422,
    500: COMMON_500,
}

COUPON_VALIDATE_RESPONSES = {
    400: _make_error_response(
        'COUPON_INVALID',
        '사용할 수 없는 쿠폰입니다',
        '쿠폰 검증 실패'
    ),
    401: COMMON_401,
    403: COMMON_403,
    404: _make_error_response(
        'COUPON_NOT_FOUND',
        '쿠폰을 찾을 수 없습니다',
        '쿠폰 조회 실패'
    ),
    422: COMMON_422,
    500: COMMON_500,
}

REFUND_CREATE_RESPONSES = {
    400: _make_error_response(
        'REFUND_NOT_ALLOWED',
        '환불 가능 기간이 지났습니다',
        '환불 신청 실패'
    ),
    401: COMMON_401,
    403: COMMON_403,
    404: _make_error_response(
        'PAYMENT_NOT_FOUND',
        '결제 내역을 찾을 수 없습니다',
        '환불 신청 실패'
    ),
    422: COMMON_422,
    500: COMMON_500,
}

REFUND_UPDATE_RESPONSES = {
    401: COMMON_401,
    403: COMMON_403,
    404: _make_error_response(
        'REFUND_NOT_FOUND',
        '환불 요청을 찾을 수 없습니다',
        '환불 처리 실패'
    ),
    422: COMMON_422,
    500: COMMON_500,
}


# ============= 수료증 관련 =============

CERTIFICATE_ISSUE_RESPONSES = {
    400: _make_error_response(
        'COMPLETION_REQUIREMENTS_NOT_MET',
        '수료 조건을 충족하지 않았습니다',
        '수료증 발급 실패'
    ),
    401: COMMON_401,
    403: COMMON_403,
    404: _make_error_response(
        'ENROLLMENT_NOT_FOUND',
        '수강 정보를 찾을 수 없습니다',
        '수료증 발급 실패'
    ),
    422: COMMON_422,
    500: COMMON_500,
}

CERTIFICATE_VERIFY_RESPONSES = {
    404: _make_error_response(
        'CERTIFICATE_NOT_FOUND',
        '유효하지 않은 수료증 번호입니다',
        '수료증 조회 실패'
    ),
    500: COMMON_500,
}

CERTIFICATE_GENERATE_RESPONSES = {
    400: _make_error_response(
        'PDF_GENERATE_FAILED',
        'PDF 생성에 실패했습니다',
        'PDF 생성 실패'
    ),
    401: COMMON_401,
    403: COMMON_403,
    404: COMMON_404,
    422: COMMON_422,
    500: COMMON_500,
}


# ============= 관리자 관련 =============

ADMIN_DASHBOARD_RESPONSES = {
    401: COMMON_401,
    403: COMMON_403,
    422: COMMON_422,
    500: COMMON_500,
}

ADMIN_USER_MANAGEMENT_RESPONSES = {
    401: COMMON_401,
    403: COMMON_403,
    404: _make_error_response(
        'USER_NOT_FOUND',
        '사용자를 찾을 수 없습니다',
        '사용자 조회 실패'
    ),
    422: COMMON_422,
    500: COMMON_500,
}

ADMIN_COURSE_MANAGEMENT_RESPONSES = {
    401: COMMON_401,
    403: COMMON_403,
    422: COMMON_422,
    500: COMMON_500,
}

ADMIN_PAYMENT_MANAGEMENT_RESPONSES = {
    401: COMMON_401,
    403: COMMON_403,
    422: COMMON_422,
    500: COMMON_500,
}

ADMIN_STATS_RESPONSES = {
    401: COMMON_401,
    403: COMMON_403,
    422: COMMON_422,
    500: COMMON_500,
}
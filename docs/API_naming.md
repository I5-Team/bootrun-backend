API 네이밍 규칙

기본 규칙
-snake_case 사용
-날짜/시간: ISO 8601 형식 (2025-10-30T12:00:00Z)

공통 필드 패턴

| 패턴 | 예시 | 설명 |
|------|------|------|
| *_at | created_at, updated_at, expired_at | 시간 |
| is_* | is_paid, is_completed, is_admin | Boolean |
| *_count | view_count, enrollment_count | 개수 |
| *_url | video_url, thumbnail_url | URL |
| *_rate | progress_rate, completion_rate | 비율 (0-100 기준) |

복수형 (리스트)
-관련된 여러 객체: 복수형 사용
-예: lectures, enrollments, missions

중첩 객체 정책

연관된 정보를 얼마나 자세히 반환할지 결정

규칙
-목록 조회 (여러 개): 연관 정보는 ID만 반환
-상세 조회 (하나): 연관 정보 객체 전체 포함

날짜/시간 처리

-ISO 8601 형식으로 전송
-예: "2025-10-30T12:00:00Z"

에러 응답 형식

주요 에러 코드 예시
| 에러 코드 | HTTP 상태 | 설명 |
|-----------|-----------|------|
| INVALID_EMAIL | 400 | 이메일 형식 오류 |
| INVALID_PASSWORD | 400 | 비밀번호 형식 오류 |
| USER_NOT_FOUND | 404 | 사용자를 찾을 수 없음 |
| COURSE_NOT_FOUND | 404 | 강의를 찾을 수 없음 |
| UNAUTHORIZED | 401 | 인증 필요 |
| FORBIDDEN | 403 | 권한 없음 |
| ALREADY_ENROLLED | 409 | 이미 수강 중 |
| PAYMENT_FAILED | 402 | 결제 실패 |
| ENROLLMENT_EXPIRED | 403 | 수강 기간 만료 |

페이지네이션 규칙

기본값
-page: 1
-page_size: 20
-최대 page_size: 100 
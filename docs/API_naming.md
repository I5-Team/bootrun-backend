API 네이밍 규칙

1. 기본 규칙
- snake_case 사용
- 날짜/시간: ISO 8601 형식 (`2025-10-30T12:00:00Z`)

2. ID 필드 규칙 중요
- 모든 ID는 `테이블명_id` 형식 사용
- PK든 FK든 동일한 패턴 (일관성)

<!-- 예시입니다. 추가하는 기능이 확정되면 전체테이블 공유드리겠습니다. -->
| 테이블 | ID 필드명 | 설명 |
|--------|-----------|------|
| User | `user_id` | 사용자 ID |
| Payment | `payment_id` | 결제 ID |
| Certificate | `certificate_id` | 수료증 ID |

3. 공통 필드 패턴

| 패턴 | 예시 | 설명 |
|------|------|------|
| `*_id` | `user_id`, `payment_id` | 모든 ID (PK/FK 구분 없음) |
| `*_at` | `created_at`, `updated_at`, `expired_at` | 시간 |
| `is_*` | `is_paid`, `is_completed`, `is_admin` | Boolean |
| `*_count` | `view_count`, `enrollment_count` | 개수 |
| `*_url` | `video_url`, `thumbnail_url` | URL |
| `*_rate` | `progress_rate`, `completion_rate` | 비율 (0-100 기준) |

4. 복수형 (리스트)
- 관련된 여러 객체: 복수형 사용
- 예: `lectures`, `enrollments`, `missions`

5. 중첩 객체 정책

연관된 정보를 얼마나 자세히 반환할지 결정

규칙
- 목록 조회 (여러 개): 연관 정보는 ID만 반환
- 상세 조회 (하나): 연관 정보 객체 전체 포함

예시
```json
// 목록 조회: GET /courses
[
  {
    "course_id": 1,
    "title": "React 완전정복",
    "instructor_id": 10,  // ← ID만
    "thumbnail_url": "...",
    "price": 50000
  }
]

// 상세 조회: GET /courses/1
{
  "course_id": 1,
  "title": "React 완전정복",
  "instructor": {        // ← 객체 전체
    "instructor_id": 10,
    "name": "김강사",
    "profile_image_url": "..."
  },
  "lectures": [...]      // ← 관련 목록도 포함
}
    // 강의 목록을 조회하거나 상세 조회 시에 각각 보여줄 내용은 나중에 상의해서 정하면 될 것 같습니다
```

6. 날짜/시간 처리 

- ISO 8601 형식으로 전송
- 예: `"2025-10-30T12:00:00Z"`

```

7. 예시

사용자 조회
```json
{
  "user_id": 123,
  "name": "홍길동",
  "email": "user@example.com",
  "is_admin": false,
  "created_at": "2025-10-30T03:00:00Z"
}
```

수강신청 조회
```json
{
  "enrollment_id": 456,
  "user_id": 123,
  "course_id": 789,
  "progress_rate": 45.5,
  "is_completed": false,
  "expired_at": "2027-10-30T14:59:59Z",
  "created_at": "2025-10-30T03:00:00Z"
}
```

8. 에러 응답 형식

기본 구조
```json
{
  "error_code": "INVALID_EMAIL",
  "message": "유효하지 않은 이메일 형식입니다",
  "details": {
    "field": "email",
    "value": "invalid-email"
  }
}
```

주요 에러 코드 예시
| 에러 코드 | HTTP 상태 | 설명 |
|-----------|-----------|------|
| `INVALID_EMAIL` | 400 | 이메일 형식 오류 |
| `INVALID_PASSWORD` | 400 | 비밀번호 형식 오류 |
| `USER_NOT_FOUND` | 404 | 사용자를 찾을 수 없음 |
| `COURSE_NOT_FOUND` | 404 | 강의를 찾을 수 없음 |
| `UNAUTHORIZED` | 401 | 인증 필요 |
| `FORBIDDEN` | 403 | 권한 없음 |
| `ALREADY_ENROLLED` | 409 | 이미 수강 중 |
| `PAYMENT_FAILED` | 402 | 결제 실패 |
| `ENROLLMENT_EXPIRED` | 403 | 수강 기간 만료 |

9. 페이지네이션 규칙

요청
```
GET /courses?page=1&page_size=20
```

응답
```json
{
  "items": [
    {
      "course_id": 1,
      "title": "React 완전정복"
    }
  ],
  "total_count": 150, // 전체 강의 갯수
  "page": 1,
  "page_size": 20,
  "total_pages": 8
}
```

기본값
- `page`: 1
- `page_size`: 20
- 최대 `page_size`: 100

10. 상태값 규칙

형식
- 소문자, snake_case 사용

주요 상태값

결제 상태 (`payment_status`)
```
pending      # 결제 대기
completed    # 결제 완료
failed       # 결제 실패
refunded     # 환불 완료
```

수강 상태 (`enrollment_status`)
```
active       # 수강 중
expired      # 기간 만료
completed    # 수강 완료
```

미션 상태 (`mission_status`)
```
not_started  # 미시작
in_progress  # 진행 중
submitted    # 제출 완료
graded       # 채점 완료
```

환불 요청 상태 (`refund_status`)
```
requested    # 환불 요청
approved     # 승인
rejected     # 거절
completed    # 환불 완료
```

11. 필터링 쿼리 파라미터

기본 형식
```
GET /courses?category=frontend&difficulty=beginner,intermediate&is_paid=true
```

규칙
- **다중 선택**: 콤마(`,`)로 구분
- **Boolean**: `true` 또는 `false` 문자열
- **날짜 범위**: `start_date`, `end_date` 사용

예시
```
# 카테고리 필터 (다중)
GET /courses?category=frontend,backend

# 난이도 필터 (다중)
GET /courses?difficulty=beginner,intermediate,advanced

# 가격 필터 (Boolean) // 유료 강의, 무료강의 구분 
GET /courses?is_paid=true

# 날짜 범위 필터
GET /payments?start_date=2025-01-01&end_date=2025-12-31

# 조합 사용
GET /courses?category=frontend&difficulty=beginner&is_paid=false
```

12. 정렬 규칙

기본 형식
```
GET /courses?sort_by=created_at&sort_order=desc
```

파라미터
- `sort_by`: 정렬 기준 필드명 (snake_case)
- `sort_order`: 정렬 방향
  - `asc`: 오름차순
  - `desc`: 내림차순 (기본값)

예시
```
# 최신순 정렬 (기본)
GET /courses?sort_by=created_at&sort_order=desc

# 가격 낮은 순
GET /courses?sort_by=price&sort_order=asc

# 수강생 많은 순
GET /courses?sort_by=enrollment_count&sort_order=desc

# 평점 높은 순
GET /courses?sort_by=rating&sort_order=desc

```

13. 미션 제출 관련

미션 조회
```json
{
  "mission_id": 45,
  "course_id": 1,
  "title": "React Hooks 이해하기",
  "mission_type": "multiple_choice",
  "question": "다음 중 React Hook이 아닌 것은?",
  "options": ["useState", "useEffect", "useContext", "useRedux"],
  "max_score": 100,
  "created_at": "2025-10-30T12:00:00Z"
}
```

미션 제출 (객관식)
```json
// POST /missions/45/submissions
{
  "user_id": 123,
  "answer": "3"
}
```

미션 제출 (코드)  
```json
// POST /missions/46/submissions
{
  "user_id": 123,
  "code": "function solution(arr) { return arr.filter(x => x % 2).reduce((a,b) => a+b, 0); }"
}
```

제출 결과
```json
{
  "submission_id": 789,
  "mission_id": 45,
  "user_id": 123,
  "mission_type": "multiple_choice",
  "answer": "3",
  "is_correct": true,
  "score": 100,
  "feedback": "정답입니다!",
  "submitted_at": "2025-10-30T12:30:00Z"
}
```

코드 제출 결과 
```json
{
  "submission_id": 790,
  "mission_id": 46,
  "user_id": 123,
  "mission_type": "code",
  "code": "function solution(arr) {...}",
  "is_correct": true,
  "score": 100,
  "test_results": [
    {
      "test_case": 1,
      "input": "[1, 2, 3, 4, 5]",
      "expected": "9",
      "actual": "9",
      "passed": true
    },
    {
      "test_case": 2,
      "input": "[2, 4, 6]",
      "expected": "0",
      "actual": "0",
      "passed": true
    }
  ],
  "submitted_at": "2025-10-30T12:35:00Z"
}

```





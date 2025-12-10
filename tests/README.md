# 진행률 계산 테스트

## 목적

백엔드가 **시간 기반**으로 진행률을 올바르게 계산하고 있음을 증명하는 테스트입니다.

## 테스트 시나리오

### 기본 시나리오 (test_시간_기반_진행률_계산)

강의: 10분 영상 2개 (총 20분)

1. **1번 영상 5분 시청** → 진행률 **25%** (5/20분)
2. **1번 영상 10분 완료** → 진행률 **50%** (10/20분)
3. **2번 영상 5분 시청** → 진행률 **75%** (15/20분)
4. **2번 영상 10분 완료** → 진행률 **100%** (20/20분)

**핵심**: 영상을 완료하지 않아도 시청한 만큼 진행률에 반영됨

### 추가 테스트

- **되감기 시 진행률 유지**: 사용자가 영상을 되감기해도 진행률이 감소하지 않음
- **자동 완료 판정**: 95% 이상 시청 시 자동으로 완료 처리
- **API 응답 검증**: `get_course_progress` API가 올바른 진행률을 반환

## 테스트 실행 방법

### 1. 필요한 패키지 설치

```bash
pip install pytest pytest-asyncio aiosqlite
```

### 2. 테스트 실행

```bash
# 모든 테스트 실행
pytest tests/ -v

# 진행률 테스트만 실행
pytest tests/test_enrollment_progress.py -v

# 상세 로그와 함께 실행
pytest tests/test_enrollment_progress.py -v -s
```

## 예상 결과

```
tests/test_enrollment_progress.py::TestProgressCalculation::test_시간_기반_진행률_계산 PASSED
✅ 시나리오 1 통과: 1번 영상 5분 시청 → 진행률 25.0%
✅ 시나리오 2 통과: 1번 영상 10분 완료 → 진행률 50.0%
✅ 시나리오 3 통과: 2번 영상 5분 시청 → 진행률 75.0%
✅ 시나리오 4 통과: 2번 영상 10분 완료 → 진행률 100.0%
🎉 모든 시나리오 통과! 백엔드는 시간 기반으로 진행률을 정확히 계산하고 있습니다.

tests/test_enrollment_progress.py::TestProgressCalculation::test_되감기_시_진행률_유지 PASSED
✅ 되감기 테스트 통과: 진행률이 유지됩니다

tests/test_enrollment_progress.py::TestProgressCalculation::test_영상_완료_판정_95퍼센트 PASSED
✅ 자동 완료 테스트 통과: 95% 이상 시청 시 자동 완료됩니다

tests/test_enrollment_progress.py::TestProgressCalculation::test_get_course_progress_API PASSED
✅ API 테스트 통과: get_course_progress가 올바른 진행률을 반환합니다
```

## 백엔드 동작 방식 요약

1. **`unique_watched_seconds`**: 최대 도달 위치를 추적 (되감기 시에도 유지)
2. **진행률 계산**: `(모든 영상의 unique_watched_seconds 합) / 전체 강의 시간 × 100`
3. **자동 업데이트**: `POST /enrollments/progress` 호출 시 자동으로 `Enrollment.progress_rate` 업데이트
4. **완료 판정**: 95% 이상 시청 시 자동으로 `is_completed = True`

## 결론

✅ **백엔드는 시간 기반으로 진행률을 정확히 계산하고 있습니다.**

만약 프론트엔드에서 진행률이 제대로 표시되지 않는다면:
1. 영상 재생 중에 주기적으로 `POST /enrollments/progress` API를 호출하고 있는지 확인
2. API 응답의 `progress_rate` 값을 UI에 제대로 반영하고 있는지 확인
3. `completed_lectures / total_lectures` 대신 `progress_rate`를 사용하고 있는지 확인

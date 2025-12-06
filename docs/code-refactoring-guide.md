# AI 코드 리팩토링 가이드

## AI 코드의 특징

### 1. 과도한 주석
- 모든 함수/클래스에 긴 docstring
- 자명한 코드에도 설명 주석
- 주석이 코드보다 긴 경우

### 2. 지나친 방어 코딩
- 불필요한 try-except 남발
- 발생하지 않을 에러까지 처리
- 과도한 유효성 검사

### 3. 네이밍
- 지나치게 서술적이고 긴 변수명
- 완벽하게 일관된 snake_case
- 약어를 거의 사용하지 않음

### 4. 구조
- 타입 힌트가 모든 곳에 존재
- 헬퍼 함수 과도하게 분리
- 완벽한 들여쓰기와 공백

---

## 자연스럽게 만드는 방법

### 주석 줄이기
```python
# Before (AI 스타일)
def calculate_total(items: list) -> float:
    """
    Calculate the total price of all items.
    Args: items - List of items
    Returns: Total price
    """
    # Initialize total
    total = 0
    # Loop through items
    for item in items:
        total += item.price
    return total

# After (자연스러운 스타일)
def calculate_total(items: list) -> float:
    """총 가격 계산"""
    return sum(item.price for item in items)
```

### 방어 코드 줄이기
```python
# Before
def get_user_name(user_id):
    if user_id is None:
        return None
    if not isinstance(user_id, int):
        return None
    try:
        user = User.query.get(user_id)
        if user is None:
            return None
        return user.name
    except Exception:
        return None

# After
def get_user_name(user_id):
    user = User.query.get(user_id)
    return user.name if user else None
```

### 변수명 적당히 줄이기
```python
# Before
retrieved_user_authentication_credentials = get_credentials()

# After
user_creds = get_credentials()
# 또는 문맥상 명확하면
creds = get_credentials()
```

### 타입 힌트 선택적 사용
```python
# Before - 모든 곳에
def process(data: Dict[str, Any]) -> List[Tuple[str, int]]:
    result: List[Tuple[str, int]] = []
    temp: int = 0

# After - 중요한 곳만
def process(data: dict) -> list:
    result = []
    temp = 0
```

---

## 리팩토링 체크리스트

- [ ] 불필요한 주석 삭제 (자명한 코드의 설명 주석)
- [ ] docstring 간결하게 수정
- [ ] 과도한 try-except 정리
- [ ] 변수명 적당히 축약 (문맥상 명확한 경우)
- [ ] 중복 검증 로직 제거
- [ ] 간단한 로직은 한 줄로 축약
- [ ] 모든 타입 힌트 제거 (주요 함수만 남기기)
- [ ] 리스트 컴프리헨션/람다 적절히 사용
- [ ] TODO, FIXME 주석 일부 추가 (자연스러움)

---

## 프롬프트 예시

### 기본 리팩토링
```
다음 코드를 자연스럽게 리팩토링해줘:
- 과도한 주석 제거
- 불필요한 방어 코드 제거
- 변수명 적당히 축약
- 타입 힌트는 주요 함수만
- 간단한 로직은 한 줄로

[코드 붙여넣기]
```

### 추가 요청 사항
```
리팩토링 시 다음도 포함해줘:
- 일부러 TODO 주석 1-2개 추가
- 일관성 없는 스타일 일부 포함
- 약어 적절히 사용
```

---

## 주의사항

- 너무 지저분하게 만들지 말 것
- 기능은 동일하게 유지
- 가독성은 유지하되 "완벽함"을 피할 것
- 팀 코딩 컨벤션 우선 준수

## 추가 주의사항 (가장 중요)
- '인간미'를 더하는 목적은 가독성을 해치는 것이 아님
- 기능은 동일하게 유지: 코드를 리팩토링하더라도 본래의 기능(결제, 관리자 API 로직)이 훼손되어서는 안 됨
- 핵심 컨벤션 유지: 팀이 정한 들여쓰기 크기(2칸/4칸), 라인 길이 제한 등 팀 컨벤션의 큰 틀은 반드시 준수해야 할 것. 미세한 불일치는 눈에 잘 띄지 않는 곳에만 적용
- 가독성 유지: 코드를 읽는 데 지장이 가는 수준의 약어나 불일치는 피해야 함
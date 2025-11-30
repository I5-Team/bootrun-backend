# Python 백엔드 코드 컨벤션
## 1. 네이밍 규칙
### 1.1 변수명/함수명: snake_case
python# 변수
user_count = 10
is_active = True

# 함수
def get_user_list():
    pass

def calculate_total_price():
    pass
1.2 클래스명: UpperCamelCase
pythonclass UserService:
    pass

class DatabaseConnection:
    pass
1.3 상수명: UPPER_SNAKE_CASE
pythonMAX_RETRY_COUNT = 3
DEFAULT_TIMEOUT = 30
API_BASE_URL = "https://api.example.com"
1.4 비공개 변수/메서드: 언더스코어(_) 접두사
pythonclass User:
    def __init__(self):
        self._password = None  # 내부용
    
    def _validate_password(self):  # 내부 메서드
        pass
2. 네이밍 원칙
2.1 "설명 + 요소" 순서
pythonanswer_btn = ...      # 올바른 예시
btn_answer = ...      # 잘못된 예시

user_list = []        # 올바른 예시
list_user = []        # 잘못된 예시
2.2 함수명: "동사 + 목적어"
pythondef get_comment():    # 올바른 예시
def comment_get():    # 잘못된 예시

def create_order():   # 올바른 예시
def validate_email(): # 올바른 예시
2.3 Boolean 변수: is/has/can 접두사
pythonis_valid = True
has_permission = False
can_edit = True
3. 포매팅
3.1 들여쓰기: 스페이스 4칸
pythondef example():
    if True:
        print("4 spaces")
3.2 최대 줄 길이: 79자 (PEP 8 기준)
python# 긴 import
from some.deep.module.inside.a.module import (
    a_nice_function, 
    another_nice_function, 
    yet_another_nice_function
)

# 긴 문자열
my_string = (
    "For a long time I used to go to bed early. "
    "Sometimes, when I had put out my candle, "
    "my eyes would close so quickly."
)
3.3 연산자 개행: 연산자를 다음 줄 앞에
python# 권장
total = (
    one
    + two
    + three
)

# 함수 호출
result = some_function(
    arg1,
    arg2,
    arg3
)
3.4 빈 줄
python# 최상위 함수/클래스: 2줄 띄우기
def first_function():
    pass


def second_function():
    pass


# 클래스 내 메서드: 1줄 띄우기
class MyClass:
    def method_one(self):
        pass
    
    def method_two(self):
        pass
4. Import 규칙
4.1 Import 순서
python# 1. 표준 라이브러리
import os
import sys

# 2. 서드파티 라이브러리
import requests
from flask import Flask

# 3. 로컬 애플리케이션
from .models import User
from .utils import helper
4.2 절대 경로 import 우선
pythonfrom myproject.models import User  # 올바른 예시
from .models import User           # 같은 패키지 내에서만
5. 문서화
5.1 Docstring: 큰따옴표 3개
pythondef calculate_price(quantity, unit_price):
    """
    총 가격을 계산합니다.
    
    Args:
        quantity (int): 수량
        unit_price (float): 단가
    
    Returns:
        float: 총 가격
    """
    return quantity * unit_price
5.2 주석: 코드 위에 작성
python# 사용자 인증 확인
if not user.is_authenticated:
    return error_response()
6. 기타 권장사항
6.1 타입 힌팅 사용
pythondef get_user_name(user_id: int) -> str:
    return "John"

def process_data(data: list[dict]) -> None:
    pass
6.2 비교 연산
python# 올바른 예시
if value is None:
if value is not None:

# 주의사항
if value == None:
6.3 문자열: 일관된 따옴표 사용 (작은따옴표 권장)
pythonname = 'John'
message = 'He said "Hello"'  # 내부에 큰따옴표 필요시
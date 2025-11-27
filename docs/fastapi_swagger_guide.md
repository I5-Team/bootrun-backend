# FastAPI Swagger(OpenAPI) 문서 작성 가이드

> **작성 기준**: FastAPI v0.120.2 (2025년 10월 최신 버전)

## 목차

1. [Swagger란 무엇인가?](#swagger란-무엇인가)
2. [FastAPI의 자동 문서화](#fastapi의-자동-문서화)
3. [기본 설정](#기본-설정)
4. [상세 문서화 방법](#상세-문서화-방법)
5. [실전 시나리오별 예제](#실전-시나리오별-예제)
6. [공통 예외처리 (중앙 집중식)](#공통-예외처리-중앙-집중식)

---

## Swagger란 무엇인가?

**Swagger**는 REST API를 설계, 빌드, 문서화하는 도구입니다. 현재는 **OpenAPI**라는 이름으로 표준화되었습니다.

### 주요 특징:
- **자동 문서 생성**: 코드만 작성하면 문서가 자동으로 만들어집니다
- **테스트 가능**: 브라우저에서 바로 API를 테스트할 수 있습니다
- **실시간 업데이트**: 코드를 수정하면 문서도 자동으로 업데이트됩니다

---

## FastAPI의 자동 문서화

FastAPI는 별도의 설정 없이도 **자동으로 Swagger UI와 ReDoc**을 제공합니다!

### 문서 접속 URL:
- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`
- **OpenAPI JSON**: `http://localhost:8000/openapi.json`

---

## 기본 설정

### 1. 패키지 설치

```bash
# 표준 패키지 설치 (권장)
pip install "fastapi[standard]"

# 또는 개별 설치
pip install fastapi
pip install "uvicorn[standard]"
```

### 2. 기본 앱 생성

```python
# main.py

from fastapi import FastAPI

# FastAPI 앱 인스턴스 생성
# title: API 문서의 제목
# description: API에 대한 설명
# version: API 버전
app = FastAPI(
    title="나의 첫 API",
    description="FastAPI를 이용한 샘플 API입니다",
    version="1.0.0"
)

@app.get("/")
async def root():
    """
    루트 엔드포인트
    
    간단한 환영 메시지를 반환합니다.
    """
    return {"message": "안녕하세요! FastAPI입니다"}
```

### 3. 서버 실행

```bash
# 개발 모드 (자동 재시작)
fastapi dev main.py

# 또는 uvicorn 직접 사용
uvicorn main:app --reload
```

브라우저에서 `http://localhost:8000/docs`로 접속하면 Swagger UI를 볼 수 있습니다!

---

## 상세 문서화 방법

### 1. 메타데이터 추가

```python
# main.py

from fastapi import FastAPI

# 태그 메타데이터 정의
# 태그는 API 엔드포인트를 그룹화하는 데 사용됩니다
tags_metadata = [
    {
        "name": "사용자",
        "description": "사용자 관련 API입니다. 회원가입, 로그인 등을 처리합니다.",
    },
    {
        "name": "상품",
        "description": "상품 관리 API입니다. 상품 조회, 등록, 수정, 삭제를 처리합니다.",
    },
    {
        "name": "주문",
        "description": "주문 처리 API입니다.",
    },
]

# FastAPI 앱 생성 (상세 설정)
app = FastAPI(
    title="쇼핑몰 API",
    description="""
    ## 쇼핑몰 백엔드 API
    
    이 API는 다음 기능을 제공합니다:
    
    * **사용자 관리** - 회원가입, 로그인, 프로필 관리
    * **상품 관리** - 상품 조회, 등록, 수정, 삭제
    * **주문 처리** - 주문 생성, 조회, 취소
    
    ### 인증 방식
    JWT 토큰 기반 인증을 사용합니다.
    """,
    version="1.0.0",
    openapi_tags=tags_metadata,  # 태그 메타데이터 적용
    docs_url="/docs",  # Swagger UI URL (기본값)
    redoc_url="/redoc",  # ReDoc URL (기본값)
    openapi_url="/openapi.json",  # OpenAPI 스키마 URL (기본값)
    # contact={
    #     "name": "개발팀",
    #     "email": "dev@example.com",
    # },
    # license_info={
    #     "name": "MIT",
    # },
)
```

### 2. Pydantic 모델을 사용한 데이터 검증 및 문서화

```python
# models.py

from pydantic import BaseModel, Field, EmailStr
from typing import Optional
from datetime import datetime

class UserCreate(BaseModel):
    """
    사용자 생성 요청 모델
    
    새로운 사용자를 등록할 때 필요한 정보입니다.
    """
    
    # Field를 사용하여 상세한 설명과 제약 조건 추가
    username: str = Field(
        ...,  # '...'는 필수 필드를 의미
        min_length=3,
        max_length=20,
        description="사용자 아이디 (3~20자)",
        example="hong_gildong"
    )
    
    email: EmailStr = Field(
        ...,
        description="이메일 주소 (유효한 이메일 형식이어야 함)",
        example="hong@example.com"
    )
    
    password: str = Field(
        ...,
        min_length=8,
        description="비밀번호 (최소 8자)",
        example="secure_password123"
    )
    
    age: Optional[int] = Field(
        None,  # None은 선택적 필드를 의미
        ge=14,  # ge: greater than or equal (크거나 같음)
        le=120,  # le: less than or equal (작거나 같음)
        description="나이 (14세 이상)",
        example=25
    )
    
    # Config 클래스로 추가 설정
    class Config:
        # JSON 스키마에 표시될 예제
        json_schema_extra = {
            "example": {
                "username": "hong_gildong",
                "email": "hong@example.com",
                "password": "secure_password123",
                "age": 25
            }
        }


class UserResponse(BaseModel):
    """
    사용자 응답 모델
    
    사용자 정보를 반환할 때 사용됩니다.
    비밀번호는 포함하지 않습니다.
    """
    
    id: int = Field(
        ...,
        description="사용자 고유 ID",
        example=1
    )
    
    username: str = Field(
        ...,
        description="사용자 아이디",
        example="hong_gildong"
    )
    
    email: EmailStr = Field(
        ...,
        description="이메일 주소",
        example="hong@example.com"
    )
    
    age: Optional[int] = Field(
        None,
        description="나이",
        example=25
    )
    
    created_at: datetime = Field(
        ...,
        description="계정 생성 일시",
        example="2025-10-31T12:00:00"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": 1,
                "username": "hong_gildong",
                "email": "hong@example.com",
                "age": 25,
                "created_at": "2025-10-31T12:00:00"
            }
        }


class ProductCreate(BaseModel):
    """상품 등록 요청 모델"""
    
    name: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="상품명",
        example="맥북 프로 16인치"
    )
    
    description: str = Field(
        ...,
        min_length=10,
        max_length=1000,
        description="상품 설명",
        example="M3 Max 칩이 탑재된 최신 맥북 프로입니다"
    )
    
    price: int = Field(
        ...,
        gt=0,  # gt: greater than (보다 큼)
        description="가격 (원)",
        example=3500000
    )
    
    stock: int = Field(
        ...,
        ge=0,
        description="재고 수량",
        example=10
    )
    
    is_available: bool = Field(
        True,
        description="판매 가능 여부",
        example=True
    )


class ProductResponse(BaseModel):
    """상품 응답 모델"""
    
    id: int = Field(..., description="상품 ID", example=1)
    name: str = Field(..., description="상품명", example="맥북 프로 16인치")
    description: str = Field(..., description="상품 설명", example="M3 Max 칩이 탑재된 최신 맥북 프로입니다")
    price: int = Field(..., description="가격", example=3500000)
    stock: int = Field(..., description="재고", example=10)
    is_available: bool = Field(..., description="판매 가능 여부", example=True)
    created_at: datetime = Field(..., description="등록일시", example="2025-10-31T12:00:00")
```

---

## 실전 시나리오별 예제

### 시나리오 1: 사용자 관리 API

```python
# routers/users.py

from fastapi import APIRouter, HTTPException, status, Query, Path, Body
from typing import List
from datetime import datetime
from models import UserCreate, UserResponse

# APIRouter 생성 - 라우터를 사용하면 엔드포인트를 모듈화할 수 있습니다
router = APIRouter(
    prefix="/users",  # 모든 경로 앞에 /users가 붙습니다
    tags=["사용자"],  # Swagger UI에서 이 그룹으로 표시됩니다
)

# 가짜 데이터베이스 (실제로는 DB를 사용해야 합니다)
fake_users_db = []


@router.post(
    "/",
    response_model=UserResponse,  # 응답 모델 지정 (문서화 및 검증)
    status_code=status.HTTP_201_CREATED,  # 성공 시 201 상태 코드 반환
    summary="사용자 등록",  # Swagger UI에 표시될 짧은 요약
    description="새로운 사용자를 등록합니다. 이메일과 아이디는 중복될 수 없습니다.",
    response_description="생성된 사용자 정보",  # 응답에 대한 설명
    # responses 파라미터로 다양한 응답 상태 코드 문서화
    responses={
        201: {
            "description": "사용자가 성공적으로 생성됨",
            "content": {
                "application/json": {
                    "example": {
                        "id": 1,
                        "username": "hong_gildong",
                        "email": "hong@example.com",
                        "age": 25,
                        "created_at": "2025-10-31T12:00:00"
                    }
                }
            }
        },
        400: {
            "description": "잘못된 요청 (이미 존재하는 사용자)",
            "content": {
                "application/json": {
                    "example": {"detail": "이미 존재하는 사용자입니다"}
                }
            }
        },
        422: {
            "description": "유효성 검사 실패",
            "content": {
                "application/json": {
                    "example": {
                        "detail": [
                            {
                                "loc": ["body", "email"],
                                "msg": "유효한 이메일 주소를 입력해주세요",
                                "type": "value_error.email"
                            }
                        ]
                    }
                }
            }
        }
    }
)
async def create_user(
    user: UserCreate = Body(
        ...,
        description="생성할 사용자 정보",
        # Body 파라미터에 직접 example 추가 가능
        example={
            "username": "hong_gildong",
            "email": "hong@example.com",
            "password": "secure_password123",
            "age": 25
        }
    )
):
    """
    # 사용자 등록 API
    
    새로운 사용자를 시스템에 등록합니다.
    
    ## 요청 본문
    - **username**: 사용자 아이디 (3~20자, 필수)
    - **email**: 이메일 주소 (필수)
    - **password**: 비밀번호 (최소 8자, 필수)
    - **age**: 나이 (14세 이상, 선택)
    
    ## 응답
    - 성공 시 생성된 사용자 정보를 반환합니다 (비밀번호 제외)
    - 이미 존재하는 사용자인 경우 400 에러를 반환합니다
    
    ## 주의사항
    - 이메일과 아이디는 중복될 수 없습니다
    - 비밀번호는 해시화되어 저장됩니다 (응답에 포함되지 않음)
    """
    
    # 중복 체크
    for existing_user in fake_users_db:
        if existing_user["username"] == user.username:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="이미 존재하는 아이디입니다"
            )
        if existing_user["email"] == user.email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="이미 존재하는 이메일입니다"
            )
    
    # 새 사용자 생성 (실제로는 DB에 저장)
    new_user = {
        "id": len(fake_users_db) + 1,
        "username": user.username,
        "email": user.email,
        "age": user.age,
        "created_at": datetime.now()
    }
    
    fake_users_db.append(new_user)
    
    return new_user


@router.get(
    "/",
    response_model=List[UserResponse],  # 리스트 형태의 응답
    status_code=status.HTTP_200_OK,
    summary="사용자 목록 조회",
    description="전체 사용자 목록을 페이지네이션하여 조회합니다",
    response_description="사용자 목록"
)
async def get_users(
    # Query 파라미터로 쿼리스트링 문서화
    skip: int = Query(
        0,
        ge=0,
        description="건너뛸 항목 수 (페이지네이션)",
        example=0
    ),
    limit: int = Query(
        10,
        ge=1,
        le=100,
        description="가져올 최대 항목 수 (1~100)",
        example=10
    ),
    search: str = Query(
        None,
        min_length=2,
        description="검색어 (사용자명 검색, 선택사항)",
        example="hong"
    )
):
    """
    # 사용자 목록 조회 API
    
    등록된 사용자 목록을 조회합니다.
    
    ## 쿼리 파라미터
    - **skip**: 건너뛸 항목 수 (기본값: 0)
    - **limit**: 가져올 최대 항목 수 (기본값: 10, 최대: 100)
    - **search**: 사용자명 검색어 (선택사항)
    
    ## 예시
    - 첫 10명 조회: `GET /users/`
    - 11~20번째 사용자 조회: `GET /users/?skip=10&limit=10`
    - 'hong' 검색: `GET /users/?search=hong`
    """
    
    # 검색어가 있으면 필터링
    users = fake_users_db
    if search:
        users = [u for u in users if search.lower() in u["username"].lower()]
    
    # 페이지네이션
    return users[skip : skip + limit]


@router.get(
    "/{user_id}",
    response_model=UserResponse,
    status_code=status.HTTP_200_OK,
    summary="사용자 상세 조회",
    description="특정 사용자의 상세 정보를 조회합니다",
    responses={
        200: {"description": "사용자 정보 조회 성공"},
        404: {
            "description": "사용자를 찾을 수 없음",
            "content": {
                "application/json": {
                    "example": {"detail": "사용자를 찾을 수 없습니다"}
                }
            }
        }
    }
)
async def get_user(
    # Path 파라미터로 경로 변수 문서화
    user_id: int = Path(
        ...,
        gt=0,
        description="조회할 사용자의 ID",
        example=1
    )
):
    """
    # 사용자 상세 조회 API
    
    특정 ID의 사용자 상세 정보를 조회합니다.
    
    ## 경로 파라미터
    - **user_id**: 조회할 사용자의 고유 ID
    
    ## 응답
    - 성공 시 해당 사용자의 상세 정보를 반환합니다
    - 사용자가 없으면 404 에러를 반환합니다
    """
    
    # 사용자 찾기
    for user in fake_users_db:
        if user["id"] == user_id:
            return user
    
    # 없으면 404 에러
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"ID {user_id}인 사용자를 찾을 수 없습니다"
    )


@router.delete(
    "/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,  # 삭제 성공 시 204 (No Content)
    summary="사용자 삭제",
    description="특정 사용자를 삭제합니다",
    responses={
        204: {"description": "사용자가 성공적으로 삭제됨"},
        404: {
            "description": "사용자를 찾을 수 없음",
            "content": {
                "application/json": {
                    "example": {"detail": "사용자를 찾을 수 없습니다"}
                }
            }
        }
    }
)
async def delete_user(
    user_id: int = Path(
        ...,
        gt=0,
        description="삭제할 사용자의 ID",
        example=1
    )
):
    """
    # 사용자 삭제 API
    
    특정 ID의 사용자를 시스템에서 삭제합니다.
    
    ## 경로 파라미터
    - **user_id**: 삭제할 사용자의 고유 ID
    
    ## 응답
    - 성공 시 204 상태 코드를 반환합니다 (본문 없음)
    - 사용자가 없으면 404 에러를 반환합니다
    
    ## 주의사항
    - 이 작업은 되돌릴 수 없습니다
    """
    
    # 사용자 찾아서 삭제
    for i, user in enumerate(fake_users_db):
        if user["id"] == user_id:
            fake_users_db.pop(i)
            return  # 204는 본문을 반환하지 않음
    
    # 없으면 404 에러
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"ID {user_id}인 사용자를 찾을 수 없습니다"
    )
```

### 시나리오 2: 상품 관리 API

```python
# routers/products.py

from fastapi import APIRouter, HTTPException, status, Query, Path
from typing import List, Optional
from datetime import datetime
from models import ProductCreate, ProductResponse

router = APIRouter(
    prefix="/products",
    tags=["상품"],
)

# 가짜 상품 데이터베이스
fake_products_db = []


@router.post(
    "/",
    response_model=ProductResponse,
    status_code=status.HTTP_201_CREATED,
    summary="상품 등록",
    description="새로운 상품을 등록합니다"
)
async def create_product(product: ProductCreate):
    """
    # 상품 등록 API
    
    새로운 상품을 시스템에 등록합니다.
    
    ## 요청 본문
    - **name**: 상품명 (1~100자, 필수)
    - **description**: 상품 설명 (10~1000자, 필수)
    - **price**: 가격 (0보다 큰 정수, 필수)
    - **stock**: 재고 수량 (0 이상, 필수)
    - **is_available**: 판매 가능 여부 (기본값: True)
    """
    
    new_product = {
        "id": len(fake_products_db) + 1,
        "name": product.name,
        "description": product.description,
        "price": product.price,
        "stock": product.stock,
        "is_available": product.is_available,
        "created_at": datetime.now()
    }
    
    fake_products_db.append(new_product)
    return new_product


@router.get(
    "/",
    response_model=List[ProductResponse],
    summary="상품 목록 조회",
    description="전체 상품 목록을 조회합니다"
)
async def get_products(
    skip: int = Query(0, ge=0, description="건너뛸 항목 수"),
    limit: int = Query(10, ge=1, le=100, description="가져올 최대 항목 수"),
    min_price: Optional[int] = Query(None, ge=0, description="최소 가격 필터"),
    max_price: Optional[int] = Query(None, ge=0, description="최대 가격 필터"),
    available_only: bool = Query(False, description="판매 가능한 상품만 조회")
):
    """
    # 상품 목록 조회 API
    
    등록된 상품 목록을 조회하고 필터링할 수 있습니다.
    
    ## 쿼리 파라미터
    - **skip**: 건너뛸 항목 수
    - **limit**: 가져올 최대 항목 수
    - **min_price**: 최소 가격 (선택)
    - **max_price**: 최대 가격 (선택)
    - **available_only**: True면 판매 가능한 상품만 조회
    """
    
    products = fake_products_db
    
    # 가격 필터링
    if min_price is not None:
        products = [p for p in products if p["price"] >= min_price]
    if max_price is not None:
        products = [p for p in products if p["price"] <= max_price]
    
    # 판매 가능 여부 필터링
    if available_only:
        products = [p for p in products if p["is_available"]]
    
    return products[skip : skip + limit]


@router.get(
    "/{product_id}",
    response_model=ProductResponse,
    summary="상품 상세 조회"
)
async def get_product(
    product_id: int = Path(..., gt=0, description="조회할 상품 ID")
):
    """상품 상세 정보를 조회합니다"""
    
    for product in fake_products_db:
        if product["id"] == product_id:
            return product
    
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"ID {product_id}인 상품을 찾을 수 없습니다"
    )


@router.put(
    "/{product_id}",
    response_model=ProductResponse,
    summary="상품 정보 수정"
)
async def update_product(
    product_id: int = Path(..., gt=0, description="수정할 상품 ID"),
    product: ProductCreate = None
):
    """
    # 상품 정보 수정 API
    
    기존 상품의 정보를 수정합니다.
    
    ## 참고
    - 전체 정보를 새로 입력해야 합니다 (PUT 방식)
    - 부분 수정은 PATCH를 사용하세요
    """
    
    for i, existing_product in enumerate(fake_products_db):
        if existing_product["id"] == product_id:
            updated_product = {
                "id": product_id,
                "name": product.name,
                "description": product.description,
                "price": product.price,
                "stock": product.stock,
                "is_available": product.is_available,
                "created_at": existing_product["created_at"]
            }
            fake_products_db[i] = updated_product
            return updated_product
    
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"ID {product_id}인 상품을 찾을 수 없습니다"
    )
```

### 시나리오 3: 메인 앱에서 라우터 통합

```python
# main.py

from fastapi import FastAPI
from fastapi.responses import JSONResponse
from routers import users, products

# 태그 메타데이터
tags_metadata = [
    {
        "name": "사용자",
        "description": "사용자 관련 API입니다. 회원가입, 로그인 등을 처리합니다.",
    },
    {
        "name": "상품",
        "description": "상품 관리 API입니다. 상품 조회, 등록, 수정, 삭제를 처리합니다.",
    },
]

# FastAPI 앱 생성
app = FastAPI(
    title="쇼핑몰 API",
    description="""
    ## 쇼핑몰 백엔드 API
    
    이 API는 다음 기능을 제공합니다:
    
    * **사용자 관리** - 회원가입, 로그인, 프로필 관리
    * **상품 관리** - 상품 조회, 등록, 수정, 삭제
    
    ### 기술 스택
    - FastAPI 0.120.2
    - Python 3.8+
    - Pydantic v2
    """,
    version="1.0.0",
    openapi_tags=tags_metadata,
)

# 라우터 등록
app.include_router(users.router)
app.include_router(products.router)


@app.get(
    "/",
    tags=["기본"],
    summary="루트 엔드포인트",
    description="API 상태를 확인합니다"
)
async def root():
    """
    # API 상태 확인
    
    API가 정상적으로 동작하는지 확인합니다.
    """
    return {
        "message": "쇼핑몰 API 서버가 정상 작동 중입니다",
        "version": "1.0.0",
        "docs": "/docs",
        "redoc": "/redoc"
    }


@app.get(
    "/health",
    tags=["기본"],
    summary="헬스 체크",
    description="서버 상태를 확인합니다"
)
async def health_check():
    """서버가 살아있는지 확인하는 헬스 체크 엔드포인트"""
    return {"status": "healthy"}
```

---

## 공통 예외처리 (중앙 집중식)

FastAPI에서 예외를 중앙에서 처리하는 방법은 여러 가지가 있습니다.

### 방법 1: Exception Handler 사용 (권장)

```python
# exceptions.py

from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

class CustomException(Exception):
    """
    커스텀 예외 클래스
    
    비즈니스 로직에서 발생하는 특정 예외를 처리하기 위한 클래스입니다.
    """
    def __init__(self, status_code: int, detail: str):
        self.status_code = status_code
        self.detail = detail


# 커스텀 예외 핸들러
async def custom_exception_handler(request: Request, exc: CustomException):
    """
    커스텀 예외를 처리하는 핸들러
    
    Args:
        request: 요청 객체
        exc: 발생한 예외 객체
    
    Returns:
        JSONResponse: 에러 응답
    """
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": "CustomError",
            "detail": exc.detail,
            "path": str(request.url),
        }
    )


# HTTP 예외 핸들러
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    """
    HTTP 예외(404, 500 등)를 처리하는 핸들러
    
    FastAPI의 HTTPException이 발생했을 때 호출됩니다.
    """
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": "HTTPError",
            "detail": exc.detail,
            "status_code": exc.status_code,
            "path": str(request.url),
        }
    )


# 유효성 검사 예외 핸들러
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """
    Pydantic 유효성 검사 실패 시 처리하는 핸들러
    
    Request body, query parameter 등의 유효성 검사가 실패했을 때 호출됩니다.
    """
    # 에러 메시지를 더 읽기 쉽게 가공
    errors = []
    for error in exc.errors():
        errors.append({
            "field": " -> ".join(str(loc) for loc in error["loc"]),
            "message": error["msg"],
            "type": error["type"],
        })
    
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "error": "ValidationError",
            "detail": "입력값이 올바르지 않습니다",
            "errors": errors,
            "path": str(request.url),
        }
    )


# 일반 예외 핸들러 (마지막 안전망)
async def general_exception_handler(request: Request, exc: Exception):
    """
    모든 예상치 못한 예외를 처리하는 핸들러
    
    위의 핸들러들이 처리하지 못한 모든 예외가 여기서 처리됩니다.
    """
    # 실제 운영 환경에서는 로깅을 해야 합니다
    print(f"예상치 못한 에러 발생: {exc}")
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": "InternalServerError",
            "detail": "서버 내부 오류가 발생했습니다. 잠시 후 다시 시도해주세요.",
            "path": str(request.url),
        }
    )
```

```python
# main.py (예외 핸들러 등록)

from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.exceptions.responses import (
    CustomException,
    custom_exception_handler,
    http_exception_handler,
    validation_exception_handler,
    general_exception_handler,
)
from routers import users, products

app = FastAPI(
    title="쇼핑몰 API",
    version="1.0.0"
)

# 예외 핸들러 등록
# 등록 순서는 중요하지 않습니다 - FastAPI가 예외 타입에 따라 자동으로 매칭합니다
app.add_exception_handler(CustomException, custom_exception_handler)
app.add_exception_handler(StarletteHTTPException, http_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(Exception, general_exception_handler)  # 모든 예외의 마지막 안전망

# 라우터 등록
app.include_router(users.router)
app.include_router(products.router)


@app.get("/")
async def root():
    return {"message": "쇼핑몰 API"}


# 예외 테스트 엔드포인트들
@app.get("/test/custom-error")
async def test_custom_error():
    """커스텀 예외 테스트"""
    raise CustomException(
        status_code=400,
        detail="이것은 커스텀 예외 테스트입니다"
    )


@app.get("/test/http-error")
async def test_http_error():
    """HTTP 예외 테스트"""
    from fastapi import HTTPException
    raise HTTPException(
        status_code=403,
        detail="접근 권한이 없습니다"
    )


@app.get("/test/validation-error")
async def test_validation_error(age: int):
    """유효성 검사 예외 테스트 - age에 문자를 넣으면 에러 발생"""
    return {"age": age}


@app.get("/test/general-error")
async def test_general_error():
    """일반 예외 테스트"""
    # 의도적으로 에러 발생
    result = 1 / 0  # ZeroDivisionError
    return {"result": result}
```

### 방법 2: 미들웨어 사용

```python
# middlewares/error_handler.py

from fastapi import Request, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
import traceback
import logging

# 로거 설정
logging.basicConfig(level=logging.ERROR)
logger = logging.getLogger(__name__)


class ErrorHandlerMiddleware(BaseHTTPMiddleware):
    """
    에러 처리 미들웨어
    
    모든 요청/응답을 가로채서 에러가 발생하면 일관된 형식으로 응답합니다.
    """
    
    async def dispatch(self, request: Request, call_next):
        """
        요청을 처리하고 에러를 잡아냅니다
        
        Args:
            request: 요청 객체
            call_next: 다음 미들웨어 또는 엔드포인트 호출 함수
        
        Returns:
            Response: 응답 객체
        """
        try:
            # 다음 미들웨어나 엔드포인트 실행
            response = await call_next(request)
            return response
            
        except Exception as exc:
            # 에러 로깅
            logger.error(
                f"에러 발생: {exc}\n"
                f"경로: {request.url}\n"
                f"메서드: {request.method}\n"
                f"상세:\n{traceback.format_exc()}"
            )
            
            # 에러 타입에 따른 처리
            if isinstance(exc, ValueError):
                status_code = status.HTTP_400_BAD_REQUEST
                detail = "잘못된 값이 입력되었습니다"
            elif isinstance(exc, KeyError):
                status_code = status.HTTP_400_BAD_REQUEST
                detail = "필수 항목이 누락되었습니다"
            elif isinstance(exc, FileNotFoundError):
                status_code = status.HTTP_404_NOT_FOUND
                detail = "파일을 찾을 수 없습니다"
            else:
                # 기타 모든 예외
                status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
                detail = "서버 내부 오류가 발생했습니다"
            
            # 에러 응답 반환
            return JSONResponse(
                status_code=status_code,
                content={
                    "error": exc.__class__.__name__,
                    "detail": detail,
                    "path": str(request.url),
                }
            )
```

```python
# main.py (미들웨어 등록)

from fastapi import FastAPI
from middlewares.error_handler import ErrorHandlerMiddleware

app = FastAPI(title="쇼핑몰 API")

# 미들웨어 등록
# 주의: 미들웨어는 등록 순서의 역순으로 실행됩니다
app.add_middleware(ErrorHandlerMiddleware)

# ... 나머지 코드
```

### 방법 3: 의존성 주입을 활용한 에러 처리

```python
# dependencies.py

from fastapi import Depends, HTTPException, status
from typing import Optional

def verify_token(token: Optional[str] = None) -> str:
    """
    토큰 검증 의존성
    
    Args:
        token: 인증 토큰
    
    Returns:
        str: 검증된 토큰
    
    Raises:
        HTTPException: 토큰이 없거나 유효하지 않을 때
    """
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="인증 토큰이 필요합니다",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # 실제로는 JWT 검증 등을 수행
    if token != "valid_token":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="유효하지 않은 토큰입니다",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return token


def check_admin_permission(token: str = Depends(verify_token)) -> str:
    """
    관리자 권한 확인 의존성
    
    Args:
        token: 검증된 토큰
    
    Returns:
        str: 검증된 토큰
    
    Raises:
        HTTPException: 관리자 권한이 없을 때
    """
    # 실제로는 토큰에서 사용자 정보를 추출하여 권한 확인
    is_admin = False  # 예시
    
    if not is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="관리자 권한이 필요합니다"
        )
    
    return token
```

```python
# routers/admin.py

from fastapi import APIRouter, Depends
from dependencies import check_admin_permission

router = APIRouter(
    prefix="/admin",
    tags=["관리자"],
)


@router.get(
    "/dashboard",
    summary="관리자 대시보드",
    description="관리자만 접근 가능한 대시보드입니다"
)
async def admin_dashboard(
    # 의존성을 사용하여 권한 확인
    # 이 의존성에서 에러가 발생하면 자동으로 에러 응답이 반환됩니다
    token: str = Depends(check_admin_permission)
):
    """
    # 관리자 대시보드
    
    관리자만 접근할 수 있습니다.
    
    ## 인증
    - 유효한 관리자 토큰이 필요합니다
    """
    return {
        "message": "관리자 대시보드에 오신 것을 환영합니다",
        "data": {
            "total_users": 100,
            "total_products": 50,
            "total_orders": 200
        }
    }
```

### 완전한 예제: 모든 방법 통합

```python
# main.py (최종 완성본)

from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from fastapi.middleware.cors import CORSMiddleware
import logging

# 로거 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# 커스텀 예외 클래스들
class BusinessLogicError(Exception):
    """비즈니스 로직 에러"""
    def __init__(self, detail: str):
        self.detail = detail


class DatabaseError(Exception):
    """데이터베이스 에러"""
    def __init__(self, detail: str):
        self.detail = detail


# 앱 생성
app = FastAPI(
    title="쇼핑몰 API",
    description="완전한 에러 처리가 적용된 쇼핑몰 API입니다",
    version="1.0.0"
)

# CORS 미들웨어 추가 (선택사항)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 실제 운영에서는 특정 도메인만 허용
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# === 예외 핸들러 등록 ===

@app.exception_handler(BusinessLogicError)
async def business_logic_error_handler(request: Request, exc: BusinessLogicError):
    """비즈니스 로직 에러 핸들러"""
    logger.warning(f"비즈니스 로직 에러: {exc.detail} - 경로: {request.url}")
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={
            "error": "BusinessLogicError",
            "detail": exc.detail,
            "path": str(request.url),
        }
    )


@app.exception_handler(DatabaseError)
async def database_error_handler(request: Request, exc: DatabaseError):
    """데이터베이스 에러 핸들러"""
    logger.error(f"데이터베이스 에러: {exc.detail} - 경로: {request.url}")
    return JSONResponse(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        content={
            "error": "DatabaseError",
            "detail": "데이터베이스 오류가 발생했습니다. 잠시 후 다시 시도해주세요.",
            "path": str(request.url),
        }
    )


@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    """HTTP 예외 핸들러"""
    logger.info(f"HTTP 에러: {exc.status_code} - {exc.detail} - 경로: {request.url}")
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": "HTTPException",
            "detail": exc.detail,
            "status_code": exc.status_code,
            "path": str(request.url),
        }
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """유효성 검사 예외 핸들러"""
    errors = []
    for error in exc.errors():
        errors.append({
            "field": " -> ".join(str(loc) for loc in error["loc"]),
            "message": error["msg"],
            "type": error["type"],
        })
    
    logger.warning(f"유효성 검사 실패 - 경로: {request.url} - 에러: {errors}")
    
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "error": "ValidationError",
            "detail": "입력값이 올바르지 않습니다",
            "errors": errors,
            "path": str(request.url),
        }
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """모든 예외의 마지막 안전망"""
    logger.error(f"예상치 못한 에러: {exc} - 경로: {request.url}", exc_info=True)
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": "InternalServerError",
            "detail": "서버 내부 오류가 발생했습니다. 잠시 후 다시 시도해주세요.",
            "path": str(request.url),
        }
    )


# === 엔드포인트 ===

@app.get("/")
async def root():
    """루트 엔드포인트"""
    return {
        "message": "쇼핑몰 API",
        "version": "1.0.0",
        "docs": "/docs"
    }


@app.get("/test/business-error")
async def test_business_error():
    """비즈니스 로직 에러 테스트"""
    raise BusinessLogicError("재고가 부족합니다")


@app.get("/test/database-error")
async def test_database_error():
    """데이터베이스 에러 테스트"""
    raise DatabaseError("데이터베이스 연결 실패")


@app.get("/test/http-error")
async def test_http_error():
    """HTTP 에러 테스트"""
    from fastapi import HTTPException
    raise HTTPException(
        status_code=404,
        detail="요청하신 리소스를 찾을 수 없습니다"
    )


@app.get("/test/validation-error")
async def test_validation_error(age: int):
    """유효성 검사 에러 테스트 - age에 문자를 넣어보세요"""
    return {"age": age}


@app.get("/test/general-error")
async def test_general_error():
    """일반 에러 테스트"""
    result = 1 / 0  # ZeroDivisionError
    return {"result": result}


# 서버 실행 코드 (개발용)
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True  # 코드 변경 시 자동 재시작
    )
```

---

## 요약 및 팁

### Swagger 문서화 핵심 요점

1. **자동 생성**: FastAPI는 코드만 작성하면 Swagger 문서가 자동으로 생성됩니다
2. **타입 힌트 활용**: Python의 타입 힌트를 사용하면 자동으로 검증 및 문서화됩니다
3. **Pydantic 모델**: `BaseModel`을 상속받아 데이터 구조를 정의하면 자동으로 문서화됩니다
4. **상세 설명 추가**: 
   - Docstring (함수 아래 `"""..."""`)
   - `Field(description="...")`
   - 데코레이터 파라미터 (`summary`, `description`, `responses` 등)

### 예외처리 핵심 요점

1. **Exception Handler**: 가장 권장되는 방법, 예외 타입별로 다른 처리 가능
2. **미들웨어**: 모든 요청/응답을 가로채서 처리, 로깅에 유용
3. **의존성 주입**: 인증/권한 체크 등에 활용
4. **일관된 에러 응답**: 모든 에러는 일관된 JSON 형식으로 반환

### 초심자를 위한 팁

- `/docs`에서 실시간으로 테스트하면서 개발하세요
- 먼저 간단하게 만들고, 점진적으로 문서를 보강하세요
- Pydantic의 `Field`와 `example`을 적극 활용하세요
- 에러는 명확하고 도움이 되는 메시지로 작성하세요
- 로깅을 꼭 추가하세요 (디버깅에 큰 도움이 됩니다)

---

## 실행 방법

### 1. 프로젝트 구조

```
bootrun-backend/
├── app/
│   ├── main.py                 # FastAPI 앱 진입점, 라우터 등록, 미들웨어 설정
│   │
│   ├── core/                   # 핵심 설정 및 의존성
│   │   ├── config.py           # 환경 변수 및 설정 관리
│   │   ├── database.py         # PostgreSQL 연결 및 세션 관리
│   │   ├── redis.py            # Redis 캐시 초기화 및 관리
│   │   ├── security.py         # JWT 토큰 생성/검증, 비밀번호 해싱
│   │   ├── dependencies.py     # FastAPI 의존성 주입 
│   │   └── logging_config.py   # 구조화된 로깅 설정 
│   │
│   ├── models/                 # SQLAlchemy ORM 모델
│   │   ├── base.py             # 기본 모델 클래스
│   │   ├── user.py             # 사용자 모델
│   │   ├── course.py           # 강의, 챕터, 강의 영상 모델
│   │   ├── payment.py          # 결제 정보 모델
│   │   └── progress.py         # 수강 등록 및 학습 진행률 모델
│   │
│   ├── schemas/                # Pydantic 요청/응답 스키마
│   │   ├── user.py             # 사용자 스키마
│   │   ├── course.py           # 강의 스키마
│   │   ├── enrollment.py       # 수강 등록 스키마
│   │   ├── payment.py          # 결제 스키마
│   │   ├── admin.py            # 관리자 대시보드 응답 스키마
│   │   └── common.py           # 공통 응답 스키마 
│   │
│   ├── routers/                # API 엔드포인트
│   │   ├── auth.py             # 인증 API 
│   │   ├── user.py             # 사용자 API 
│   │   ├── course.py           # 강의 조회 API 
│   │   ├── enrollment.py       # 수강 등록 API
│   │   ├── payment.py          # 결제 API 
│   │   └── admin/              # 관리자 API
│   │       ├── dashboard.py    # 대시보드 통계 API
│   │       ├── users.py        # 사용자 관리 API
│   │       ├── courses.py      # 강의 관리 API 
│   │       └── payments.py     # 결제 관리 API 
│   │
│   ├── services/               # 비즈니스 로직 계층
│   │   ├── user_service.py                 # 사용자 서비스
│   │   ├── course_service.py               # 강의 조회 서비스
│   │   ├── enrollment_service.py           # 수강 등록 서비스
│   │   ├── payment_service.py              # 결제 서비스
│   │   ├── admin_dashboard_service.py      # 관리자 대시보드 서비스
│   │   ├── admin_user_service.py           # 관리자 사용자 관리 서비스
│   │   └── admin_course_service.py         # 관리자 강의 관리 서비스
│   │
│   ├── middleware/             # 미들웨어
│   │   └── rate_limit.py       # API 요청 속도 제한
│   │
│   ├── exceptions/             # 커스텀 예외 처리
│   │   └── responses.py        # 표준화된 에러 응답 
│   │
│   └── utils/                  # 유틸리티 함수
│       └── file_utils.py       # 파일 업로드/삭제 유틸   
│
├── alembic/                    # 데이터베이스 마이그레이션
│   ├── versions/               # 마이그레이션 버전 파일
│   └── env.py                  # Alembic 환경 설정
│
├── scripts/                    # 운영 스크립트
│   └── recalculate_progress_rates.py  # 진행률 재계산 스크립트
│
├── docs/                       # 프로젝트 문서
│   └── FOLDER_STRUCTURE.md            # 폴더 구조 문서
│
├── uploads/                    # 로컬 파일 저장 디렉토리
│   ├── thumbnails/             # 강의 썸네일 이미지
│   ├── instructors/            # 강사 프로필 이미지
│   └── profiles/               # 사용자 프로필 이미지
│
├── logs/                       # 로그 파일
│   ├── app.log                 # 애플리케이션 로그
│   └── error.log               # 에러 전용 로그
│
├── docker-compose.yml          # Docker Compose 설정
├── Dockerfile                  # Docker 이미지 빌드 설정
├── .dockerignore               # Docker 빌드 시 제외 파일
├── requirements.txt            # Python 패키지 의존성
├── alembic.ini                # Alembic 설정 파일
├── .env                       # 환경 변수 
├── .env.example               # 환경 변수 예제
├── .gitignore                 # Git 제외 파일 목록
├── deploy-ec2.sh              # EC2 배포 스크립트
├── update-deployment.sh       # 배포 업데이트 스크립트
└── README.md                  # 프로젝트 README
```

### 2. 설치 및 실행

```bash
# 패키지 설치
pip install "fastapi[standard]"

# 개발 서버 실행
fastapi dev main.py

# 또는
uvicorn main:app --reload

# 브라우저에서 접속
# Swagger UI: http://localhost:8000/docs
# ReDoc: http://localhost:8000/redoc
```

### 3. 테스트

Swagger UI(`/docs`)에서 직접 각 엔드포인트를 테스트해보세요!
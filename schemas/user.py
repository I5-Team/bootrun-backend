from pydantic import BaseModel, EmailStr, field_validator, Field
from typing import Optional
from datetime import datetime, date
from enum import Enum
import re


# Enums
class UserRole(str, Enum):
    STUDENT = "student"
    ADMIN = "admin"


class Gender(str, Enum):
    MALE = "MALE"
    FEMALE = "FEMALE"
    OTHER = "OTHER"


class SocialProvider(str, Enum):
    EMAIL = "email"
    GOOGLE = "google"
    GITHUB = "github"


# 회원가입
class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=16)
    password_confirm: str
    name: str = Field(min_length=2, max_length=50)
    gender: Gender
    birth_date: date
    profile_image: Optional[str] = None
    provider: SocialProvider = SocialProvider.EMAIL
    social_id: Optional[str] = None

    @field_validator('password')
    @classmethod
    def validate_password(cls, v):
        # 8~16자의 영문 대/소문자, 숫자, 특수문자
        pattern = r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,16}$'
        if not re.match(pattern, v):
            raise ValueError('비밀번호는 8~16자의 영문 대/소문자, 숫자, 특수문자를 포함해야 합니다')
        return v

    @field_validator('password_confirm')
    @classmethod
    def passwords_match(cls, v, info):
        if 'password' in info.data and v != info.data['password']:
            raise ValueError('비밀번호가 일치하지 않습니다')
        return v


# 이메일 인증
class EmailVerificationRequest(BaseModel):
    email: EmailStr


class EmailVerificationConfirm(BaseModel):
    email: EmailStr
    verification_code: str


# 로그인
class UserLogin(BaseModel):
    email: EmailStr
    password: str


# 소셜 로그인 (선택사항)
class SocialLoginRequest(BaseModel):
    provider: SocialProvider
    access_token: str
    email: Optional[EmailStr] = None
    name: Optional[str] = None


# 프로필 수정
class UserUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=2, max_length=50)
    gender: Optional[Gender] = None
    birth_date: Optional[date] = None
    profile_image: Optional[str] = None
    password: Optional[str] = Field(None, min_length=8, max_length=16)
    password_confirm: Optional[str] = None

    @field_validator('password')
    @classmethod
    def validate_password(cls, v):
        if v is None:
            return v
        pattern = r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,16}$'
        if not re.match(pattern, v):
            raise ValueError('비밀번호는 8~16자의 영문 대/소문자, 숫자, 특수문자를 포함해야 합니다')
        return v


# 응답
class UserResponse(BaseModel):
    id: int
    email: str
    name: str
    gender: Gender
    birth_date: date
    profile_image: Optional[str]
    role: UserRole
    is_active: bool
    created_at: datetime
    last_login: Optional[datetime]
    total_study_time: int = 0  # 총 학습 시간(분)
    enrollment_expires_at: Optional[datetime] = None  # 수강 만료일 (결제 후 2년)
    provider: SocialProvider

    class Config:
        from_attributes = True  # ORM 모드 (Pydantic v2)


# 간단한 사용자 정보 (목록용)
class UserListResponse(BaseModel):
    id: int
    email: str
    name: str
    role: UserRole
    is_active: bool
    created_at: datetime
    last_login: Optional[datetime]

    class Config:
        from_attributes = True


# 토큰 응답
class TokenResponse(BaseModel):
    access_token: str
    refresh_token: Optional[str] = None
    token_type: str = "bearer"
    user: UserResponse


# 비밀번호 재설정 요청
class PasswordResetRequest(BaseModel):
    email: EmailStr


class PasswordResetConfirm(BaseModel):
    email: EmailStr
    reset_token: str
    new_password: str = Field(min_length=8, max_length=16)
    password_confirm: str

    @field_validator('new_password')
    @classmethod
    def validate_password(cls, v):
        pattern = r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,16}$'
        if not re.match(pattern, v):
            raise ValueError('비밀번호는 8~16자의 영문 대/소문자, 숫자, 특수문자를 포함해야 합니다')
        return v


# 회원 탈퇴
class UserDeleteRequest(BaseModel):
    password: str
    confirm_text: str = Field(..., description="'회원탈퇴'를 입력해주세요")

    @field_validator('confirm_text')
    @classmethod
    def validate_confirm(cls, v):
        if v != "회원탈퇴":
            raise ValueError("'회원탈퇴'를 정확히 입력해주세요")
        return v
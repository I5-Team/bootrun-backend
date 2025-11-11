from pydantic import BaseModel, EmailStr, field_validator, Field, model_validator
from typing import Optional
from datetime import datetime, date
from enum import Enum
import re

# Enums
class UserRole(str, Enum):
    STUDENT = "student"
    ADMIN = "admin"

class Gender(str, Enum):
    MALE = "male"
    FEMALE = "female"
    OTHER = "other"

class SocialProvider(str, Enum):
    EMAIL = "email"
    GOOGLE = "google"
    GITHUB = "github"

# 회원가입
class UserCreate(BaseModel):
    email: EmailStr = Field(
        ..., 
        description="이메일 주소 (유효한 이메일 형식)", 
        example="hong@example.com"
    )
    password: str = Field(
        ...,
        min_length=8, 
        max_length=32,
        description="비밀번호 (8~32자, 영문 대/소문자, 숫자, 특수문자 포함)", 
        example="Test1234!@"
    )
    password_confirm: str = Field(
        ...,
        description="비밀번호 확인 (password와 동일해야 함)", 
        example="Test1234!@"
    )
    nickname: str = Field(
        ...,
        min_length=2, 
        max_length=18,
        description="닉네임 (2~18자)", 
        example="홍길동"
    )
    gender: Gender = Field(
        ...,
        description="성별 (male, female, other)", 
        example="male"
    )
    birth_date: date = Field(
        ...,
        description="생년월일 (YYYY-MM-DD)", 
        example="1995-01-01"
    )
    profile_image: Optional[str] = Field(
        None,
        description="프로필 이미지 URL (선택)", 
        example="https://example.com/profile.jpg"
    )
    # provider와 social_id는 소셜 로그인 시에만 제공됨 (기본값 제거)
    provider: Optional[SocialProvider] = None
    social_id: Optional[str] = None

    @field_validator('gender', mode='before')
    @classmethod
    def normalize_gender(cls, v):
        if isinstance(v, str):
            return v.lower()
        return v

    @field_validator('password')
    @classmethod
    def validate_password(cls, v):
        pattern = r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,32}$'
        if not re.match(pattern, v):
            raise ValueError('비밀번호는 8~32자의 영문 대/소문자, 숫자, 특수문자를 포함해야 합니다')
        return v

    @model_validator(mode='after')
    def passwords_match(self) -> 'UserCreate':
        if self.password and self.password_confirm and self.password != self.password_confirm:
            raise ValueError('비밀번호가 일치하지 않습니다')
        return self

# 이메일 인증
class EmailVerificationRequest(BaseModel):
    email: EmailStr = Field(
        ..., 
        description="인증할 이메일 주소", 
        example="hong@example.com"
    )

class EmailVerificationConfirm(BaseModel):
    email: EmailStr = Field(
        ..., 
        description="이메일 주소", 
        example="hong@example.com"
    )
    verification_code: str = Field(
        ...,
        description="이메일로 받은 인증 코드", 
        example="123456"
    )

# 로그인
class UserLogin(BaseModel):
    email: EmailStr = Field(
        ..., 
        description="로그인 이메일", 
        example="hong@example.com"
    )
    password: str = Field(
        ...,
        description="로그인 비밀번호", 
        example="Test1234!@"
    )

# 소셜 로그인 (선택사항)
class SocialLoginRequest(BaseModel):
    provider: SocialProvider = Field(
        ...,
        description="소셜 로그인 제공자 (google, github)", 
        example="google"
    )
    access_token: str = Field(
        ...,
        description="소셜 로그인 액세스 토큰", 
        example="ya29.a0AfH6SMB..."
    )
    email: Optional[EmailStr] = None
    nickname: Optional[str] = None

# 프로필 수정
class UserUpdate(BaseModel):
    nickname: Optional[str] = Field(
        None, 
        min_length=2, 
        max_length=18,
        description="닉네임 (2~18자)", 
        example="새로운닉네임"
    )
    gender: Optional[Gender] = Field(
        None,
        description="성별", 
        example="male"
    )
    birth_date: Optional[date] = Field(
        None,
        description="생년월일", 
        example="1995-01-01"
    )
    profile_image: Optional[str] = Field(
        None,
        description="프로필 이미지 URL", 
        example="https://example.com/new_profile.jpg"
    )
    password: Optional[str] = Field(
        None, 
        min_length=8, 
        max_length=32,
        description="새 비밀번호 (변경 시)", 
        example="NewPass1234!@"
    )
    password_confirm: Optional[str] = Field(
        None,
        description="새 비밀번호 확인", 
        example="NewPass1234!@"
    )

    @field_validator('gender', mode='before')
    @classmethod
    def validate_gender(cls, v):
        if v is not None and isinstance(v, str):
            return v.lower()
        return v

    @field_validator('password')
    @classmethod
    def validate_password(cls, v):
        if v is None:
            return v
        pattern = r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,32}$'
        if not re.match(pattern, v):
            raise ValueError('비밀번호는 8~32자의 영문 대/소문자, 숫자, 특수문자를 포함해야 합니다')
        return v

    @model_validator(mode='after')
    def passwords_match(self) -> 'UserUpdate':
        if self.password and self.password_confirm and self.password != self.password_confirm:
            raise ValueError('비밀번호가 일치하지 않습니다')
        return self

# 응답 (DB 테이블 구조와 일치하도록 수정)
class UserResponse(BaseModel):
    id: int
    email: str
    nickname: str
    gender: Gender
    birth_date: date
    profile_image: Optional[str]
    role: UserRole
    is_active: bool
    is_email_verified: bool  # DB 테이블에 있는 필드 추가
    created_at: datetime
    updated_at: datetime  # DB 테이블에 있는 필드 추가
    last_login: Optional[datetime]
    social_provider: SocialProvider  # DB 컬럼명과 일치
    social_id: Optional[str]  # DB 테이블에 있는 필드 추가

    class Config:
        from_attributes = True  # ORM 모드 (Pydantic v2)

# 마이페이지용 확장 응답 (계산된 필드 포함)
class UserProfileResponse(UserResponse):
    total_study_time: int = 0  # 총 학습 시간(분) - Progress에서 계산
    enrollment_expires_at: Optional[datetime] = None  # Enrollments에서 가져옴
    
    class Config:
        from_attributes = True

# 간단한 사용자 정보 (목록용)
class UserListResponse(BaseModel):
    id: int
    email: str
    nickname: str
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

# 계정 복구 요청
class AccountRestoreRequest(BaseModel):
    email: EmailStr = Field(
        ...,
        description="복구할 계정 이메일", 
        example="hong@example.com"
    )
    password: str = Field(
        ...,
        description="계정 비밀번호", 
        example="Test1234!@"
    )

class PasswordChangeRequest(BaseModel):
    current_password: str = Field(
        ...,
        description="현재 비밀번호", 
        example="OldPass1234!@"
    )
    new_password: str = Field(
        ...,
        min_length=8, 
        max_length=32,
        description="새 비밀번호 (8~32자)", 
        example="NewPass1234!@"
    )
    new_password_confirm: str = Field(
        ...,
        description="새 비밀번호 확인", 
        example="NewPass1234!@"
    )
    
    @field_validator('new_password')
    @classmethod
    def validate_password(cls, v):
        pattern = r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,32}$'
        if not re.match(pattern, v):
            raise ValueError('비밀번호는 8~32자의 영문 대/소문자, 숫자, 특수문자를 포함해야 합니다')
        return v
    
    @model_validator(mode='after')
    def passwords_match(self) -> 'PasswordChangeRequest':
        if self.new_password and self.new_password_confirm and self.new_password != self.new_password_confirm:
            raise ValueError('비밀번호가 일치하지 않습니다')
        return self

class EmailChangeRequest(BaseModel):
    new_email: EmailStr = Field(
        ...,
        description="변경할 이메일 주소", 
        example="newemail@example.com"
    )

class EmailChangeConfirm(BaseModel):
    new_email: EmailStr = Field(
        ...,
        description="변경할 이메일 주소", 
        example="newemail@example.com"
    )
    verification_code: str = Field(
        ...,
        description="이메일로 받은 인증 코드", 
        example="123456"
    )
    
class PasswordResetRequest(BaseModel):
    email: EmailStr = Field(
        ...,
        description="비밀번호를 재설정할 이메일", 
        example="hong@example.com"
    )

class PasswordResetConfirm(BaseModel):
    email: EmailStr = Field(
        ...,
        description="이메일 주소", 
        example="hong@example.com"
    )
    reset_token: str = Field(
        ...,
        description="비밀번호 재설정 토큰", 
        example="abc123def456"
    )
    new_password: str = Field(
        ...,
        min_length=8, 
        max_length=16,
        description="새 비밀번호", 
        example="NewPass1234!@"
    )
    password_confirm: str = Field(
        ...,
        description="새 비밀번호 확인", 
        example="NewPass1234!@"
    )

    @field_validator('new_password')
    @classmethod
    def validate_password(cls, v):
        pattern = r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,32}$'
        if not re.match(pattern, v):
            raise ValueError('비밀번호는 8~32자의 영문 대/소문자, 숫자, 특수문자를 포함해야 합니다')
        return v

    @model_validator(mode='after')
    def passwords_match(self) -> 'PasswordResetConfirm':
        if self.new_password and self.password_confirm and self.new_password != self.password_confirm:
            raise ValueError('비밀번호가 일치하지 않습니다')
        return self

class ActivityResponse(BaseModel):
    id: int
    activity_type: str  # 'question', 'comment', 'enrollment', 'payment'
    title: str
    description: Optional[str]
    created_at: datetime
    related_id: int  # 관련 리소스 ID
    
    class Config:
        from_attributes = True

class NotificationResponse(BaseModel):
    id: int
    user_id: int
    type: str  # 'expiry_warning', 'mission_deadline', 'question_answered'
    title: str
    content: str
    is_read: bool = False
    related_url: Optional[str]  # 클릭 시 이동할 URL
    created_at: datetime
    
    class Config:
        from_attributes = True        

class NotificationUpdateRequest(BaseModel):
    is_read: bool = True

UserProfileResponse.model_rebuild()
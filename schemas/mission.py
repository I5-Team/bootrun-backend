from pydantic import BaseModel, Field, field_validator
from pydantic_core import ValidationInfo 
from typing import Optional, Dict, Any, List
from datetime import datetime
from enum import Enum


# Enums
class MissionType(str, Enum):
    MIDTERM = "midterm"
    FINAL = "final"


class QuestionType(str, Enum):
    MULTIPLE_CHOICE = "multiple_choice"
    CODE = "code"


# ============= 미션 =============
class MissionCreate(BaseModel):
    course_id: int = Field(..., gt=0)
    title: str = Field(..., min_length=1, max_length=200)
    description: str
    mission_type: MissionType
    question_type: QuestionType
    question_data: Dict[str, Any]
    answer_data: Dict[str, Any]
    max_score: int = Field(default=100, ge=0)
    passing_score: int = Field(default=60, ge=0, le=100)
    max_attempts: int = Field(default=3, ge=1)
    
    @field_validator('passing_score')
    @classmethod
    def validate_passing_score(cls, v: int, info: ValidationInfo) -> int:  # 타입 힌트 추가
        max_score = info.data.get('max_score', 100)
        if v > max_score:
            raise ValueError('통과 점수는 최대 점수를 초과할 수 없습니다')
        return v

class MissionUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    question_data: Optional[Dict[str, Any]] = None
    answer_data: Optional[Dict[str, Any]] = None
    max_score: Optional[int] = Field(None, ge=0)
    passing_score: Optional[int] = Field(None, ge=0, le=100)
    max_attempts: Optional[int] = Field(None, ge=1)


class MissionResponse(BaseModel):
    id: int
    course_id: int
    course_title: str
    title: str
    description: str
    mission_type: MissionType
    question_type: QuestionType
    question_data: Dict[str, Any]
    max_score: int
    passing_score: int
    max_attempts: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class MissionWithUserStatus(BaseModel):
    id: int
    course_id: int
    course_title: str
    title: str
    description: str
    mission_type: MissionType
    question_type: QuestionType
    question_data: Dict[str, Any]
    max_score: int
    passing_score: int
    max_attempts: int
    # 사용자 관련 정보
    user_attempts: int = 0
    remaining_attempts: int
    best_score: Optional[int] = None
    is_passed: bool = False
    last_submitted_at: Optional[datetime] = None
    created_at: datetime
    
    class Config:
        from_attributes = True


# ============= 미션 제출 =============
class MissionSubmissionCreate(BaseModel):
    mission_id: int = Field(..., gt=0)
    answer: Dict[str, Any]  # JSON 형태의 답안


class MissionSubmissionResponse(BaseModel):
    id: int
    mission_id: int
    mission_title: str
    user_id: int
    answer: Dict[str, Any]
    score: int
    is_passed: bool
    feedback: str
    attempt_number: int
    remaining_attempts: int
    submitted_at: datetime
    # 실행 결과 (코드 제출형)
    execution_result: Optional[Dict[str, Any]] = None
    
    class Config:
        from_attributes = True


class MissionSubmissionHistory(BaseModel):
    id: int
    mission_id: int
    mission_title: str
    mission_type: MissionType
    score: int
    is_passed: bool
    attempt_number: int
    submitted_at: datetime


class UserMissionProgress(BaseModel):
    mission_id: int
    mission_title: str
    mission_type: MissionType
    max_score: int
    passing_score: int
    max_attempts: int
    user_attempts: int
    remaining_attempts: int
    best_score: Optional[int]
    is_passed: bool
    submissions: List[MissionSubmissionHistory] = []


# ============= 코드 실행 (코드 제출형) =============
class CodeExecutionRequest(BaseModel):
    mission_id: int = Field(..., gt=0)
    code: str = Field(..., min_length=1)


class CodeExecutionResponse(BaseModel):
    success: bool
    output: Optional[str]
    error: Optional[str]
    execution_time: Optional[float]  # 실행 시간 (ms)
    test_results: Optional[List[Dict[str, Any]]] = None


# ============= 미션 통계 =============
class MissionStats(BaseModel):
    mission_id: int
    mission_title: str
    mission_type: MissionType
    total_attempts: int
    total_submissions: int
    pass_count: int
    fail_count: int
    pass_rate: float
    avg_score: float
    avg_attempts: float
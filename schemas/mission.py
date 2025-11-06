from pydantic import BaseModel, Field, field_validator
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
    title: str = Field(
        ..., 
        min_length=1, 
        max_length=200,
        description="미션 제목", 
        example="중간 평가 - Python 기초"
    )
    description: str = Field(
        ...,
        description="미션 설명", 
        example="Python 기초 문법을 평가하는 중간 미션입니다."
    )
    mission_type: MissionType = Field(
        ...,
        description="미션 유형 (midterm: 중간, final: 기말)", 
        example="midterm"
    )
    question_type: QuestionType = Field(
        ...,
        description="문제 유형 (multiple_choice: 객관식, code: 코드제출)", 
        example="multiple_choice"
    )
    question_data: Dict[str, Any] = Field(
        ...,
        description="문제 데이터 (JSON 형식)", 
        example={
            "questions": [
                {
                    "question": "Python에서 리스트를 나타내는 기호는?",
                    "options": ["[]", "{}", "()", "<>"],
                    "answer_index": 0
                }
            ]
        }
    )
    answer_data: Dict[str, Any] = Field(
        ...,
        description="정답 데이터 (JSON 형식)", 
        example={"answers": [0]}
    )
    max_score: int = Field(
        default=100, 
        ge=0,
        description="최대 점수", 
        example=100
    )
    passing_score: int = Field(
        default=60, 
        ge=0, 
        le=100,
        description="통과 기준 점수", 
        example=60
    )
    max_attempts: int = Field(
        default=3, 
        ge=1,
        description="최대 제출 횟수", 
        example=3
    )
    

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
    mission_id: int = Field(
        ..., 
        ge=1,
        description="제출할 미션 ID", 
        example=1
    )
    answer: Dict[str, Any] = Field(
        ...,
        description="제출 답안 (JSON 형태)", 
        example={"answers": [0, 2, 1, 3, 0]}
    )


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
"""
Pydantic schemas for Feedback and Feedback Questions
"""
from pydantic import BaseModel, Field, ConfigDict, field_validator
from typing import List, Optional, Dict, Any, Literal
from datetime import datetime


# ========== Feedback Question Schemas ==========

class QuestionOption(BaseModel):
    """Option for a feedback question"""
    label: str = Field(..., description="Display label for the option")
    value: str = Field(..., description="Value to submit when selected")
    
    model_config = ConfigDict(from_attributes=True)


class FeedbackQuestionDetail(BaseModel):
    """Detailed feedback question"""
    question_id: int
    week_table: Literal['workout_weeks', 'nutrition_weeks']
    week_id: int
    focus: Literal['performance_enhancement', 'body_recomposition', 'efficiency', 'rebuilding_rehab']
    question_text: str
    question_type: Literal['radio', 'multi-select']
    options: Optional[List[Dict[str, str]]] = Field(None, description="Static options or null if dynamic")
    allow_text: bool = Field(False, description="Whether user can add text response")
    dynamic_options: Optional[Literal['exercises', 'meals']] = Field(None, description="Generate options from week data")
    question_order: int
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


class FeedbackQuestionListResponse(BaseModel):
    """Response for listing feedback questions"""
    questions: List[FeedbackQuestionDetail]
    total: int


# ========== Feedback Response Schemas ==========

class FeedbackResponse(BaseModel):
    """Single question response within feedback"""
    question_id: str = Field(..., description="Unique identifier for the question")
    answer: Any = Field(..., description="User's answer (can be string, list, or other type)")
    text_response: Optional[str] = Field(None, description="Optional text response from user")
    selected_exercises: Optional[List[str]] = Field(None, description="Optional list of exercise names if relevant")
    
    model_config = ConfigDict(from_attributes=True)


class FeedbackCreate(BaseModel):
    """Schema for creating feedback"""
    week_table: Literal['workout_weeks', 'nutrition_weeks'] = Field(..., description="Type of week: workout_weeks or nutrition_weeks")
    week_id: int = Field(..., gt=0, description="ID of the week being reviewed")
    responses: List[Dict[str, Any]] = Field(..., min_length=1, description="Array of question responses")
    
    @field_validator('responses')
    @classmethod
    def validate_responses(cls, v):
        """Validate that responses contain required fields"""
        if not v:
            raise ValueError("At least one response is required")
        
        for response in v:
            if not isinstance(response, dict):
                raise ValueError("Each response must be an object")
            if 'question_id' not in response:
                raise ValueError("Each response must have a question_id")
            if 'answer' not in response:
                raise ValueError("Each response must have an answer")
        
        return v


class FeedbackDetail(BaseModel):
    """Schema for feedback response"""
    feedback_id: int
    user_id: int
    week_table: str
    week_id: int
    responses: List[Dict[str, Any]]
    submitted_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


class FeedbackSummary(BaseModel):
    """Summary of feedback (without full responses)"""
    feedback_id: int
    user_id: int
    week_table: str
    week_id: int
    submitted_at: datetime
    questions_answered: int
    
    model_config = ConfigDict(from_attributes=True)


class FeedbackListResponse(BaseModel):
    """Response for listing feedback"""
    feedback: List[FeedbackSummary]
    total: int

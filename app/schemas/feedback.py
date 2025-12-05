"""
Pydantic schemas for Feedback
"""
from pydantic import BaseModel, Field, ConfigDict, field_validator
from typing import List, Optional, Dict, Any, Literal
from datetime import datetime


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

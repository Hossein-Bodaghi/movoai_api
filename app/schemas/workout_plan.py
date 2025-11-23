"""
Pydantic schemas for Workout Plans (Phase 2)
"""
from pydantic import BaseModel, ConfigDict, Field
from typing import List, Optional, Dict, Any
from datetime import datetime


# ========== Exercise Schemas (nested) ==========
class ExerciseBase(BaseModel):
    """Basic exercise information"""
    exercise_id: int
    name_en: str
    name_fa: Optional[str] = None
    
    model_config = ConfigDict(from_attributes=True)


class ExerciseInWorkout(BaseModel):
    """Exercise information within a workout day"""
    exercise_id: int
    name_en: str
    name_fa: Optional[str] = None
    
    model_config = ConfigDict(from_attributes=True)


# ========== Workout Day Exercise Schemas ==========
class WorkoutDayExerciseBase(BaseModel):
    """Base schema for workout day exercise"""
    exercise_id: int
    sets: Optional[str] = None
    reps: Optional[str] = None
    tempo: Optional[str] = None
    rest: Optional[str] = None
    notes: Optional[str] = None
    exercise_order: int


class WorkoutDayExerciseCreate(WorkoutDayExerciseBase):
    """Schema for creating workout day exercise"""
    pass


class WorkoutDayExerciseResponse(BaseModel):
    """Schema for workout day exercise response"""
    workout_day_exercise_id: int
    day_id: int
    exercise_id: int
    sets: Optional[str] = None
    reps: Optional[str] = None
    tempo: Optional[str] = None
    rest: Optional[str] = None
    notes: Optional[str] = None
    exercise_order: int
    created_at: datetime
    exercise: Optional[ExerciseInWorkout] = None
    
    model_config = ConfigDict(from_attributes=True)


# ========== Workout Day Schemas ==========
class WorkoutDayBase(BaseModel):
    """Base schema for workout day"""
    day_name: str = Field(..., max_length=50)
    focus: Optional[str] = None
    warmup: Optional[str] = None
    cooldown: Optional[str] = None


class WorkoutDayCreate(WorkoutDayBase):
    """Schema for creating workout day"""
    exercises: List[WorkoutDayExerciseCreate] = []


class WorkoutDayResponse(WorkoutDayBase):
    """Schema for workout day response"""
    day_id: int
    week_id: int
    created_at: datetime
    exercises: List[WorkoutDayExerciseResponse] = []
    
    model_config = ConfigDict(from_attributes=True)


# ========== Workout Week Schemas ==========
class WorkoutWeekBase(BaseModel):
    """Base schema for workout week"""
    week_number: int = Field(..., ge=1, le=12)
    title: Optional[str] = Field(None, max_length=255)
    description: Optional[str] = None


class WorkoutWeekCreate(WorkoutWeekBase):
    """Schema for creating workout week"""
    days: List[WorkoutDayCreate] = []


class WorkoutWeekResponse(WorkoutWeekBase):
    """Schema for workout week response"""
    week_id: int
    plan_id: int
    created_at: datetime
    days: List[WorkoutDayResponse] = []
    
    model_config = ConfigDict(from_attributes=True)


# ========== Workout Plan Schemas ==========
class WorkoutPlanBase(BaseModel):
    """Base schema for workout plan"""
    name: str = Field(..., max_length=255)
    workout_goal_id: Optional[int] = None
    total_weeks: int = Field(..., ge=1, le=12)


class WorkoutPlanCreate(WorkoutPlanBase):
    """Schema for creating workout plan - AI will generate weeks"""
    # User provides basic info, AI generates the rest
    pass


class WorkoutPlanUpdate(BaseModel):
    """Schema for updating workout plan"""
    name: Optional[str] = Field(None, max_length=255)
    current_week: Optional[int] = Field(None, ge=1)


class WorkoutPlanResponse(WorkoutPlanBase):
    """Schema for workout plan response"""
    plan_id: int
    user_id: int
    current_week: int
    completed_weeks: List[int] = []
    strategy: Optional[Dict[str, Any]] = None
    expectations: Optional[Dict[str, Any]] = None
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


class WorkoutPlanDetailResponse(WorkoutPlanResponse):
    """Schema for workout plan with full details including weeks"""
    weeks: List[WorkoutWeekResponse] = []
    
    model_config = ConfigDict(from_attributes=True)


class WorkoutPlanListResponse(BaseModel):
    """Schema for list of workout plans"""
    plans: List[WorkoutPlanResponse]
    total: int


# ========== Week Completion Schemas ==========
class WeekCompletionRequest(BaseModel):
    """Schema for marking a week as completed"""
    week_number: int = Field(..., ge=1, le=12)


class WeekCompletionResponse(BaseModel):
    """Schema for week completion response"""
    plan_id: int
    week_number: int
    current_week: int
    completed_weeks: List[int]
    message: str

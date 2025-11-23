"""
Pydantic schemas for Goals
"""
from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime


class WorkoutGoalBase(BaseModel):
    """Base workout goal schema"""
    focus: str
    goal_key: str
    goal_label_en: str
    goal_label_fa: Optional[str] = None
    description_en: Optional[str] = None
    description_fa: Optional[str] = None


class WorkoutGoalResponse(WorkoutGoalBase):
    """Workout goal response schema"""
    workout_goal_id: int
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


class NutritionGoalBase(BaseModel):
    """Base nutrition goal schema"""
    focus: str
    goal_key: str
    goal_label_en: str
    goal_label_fa: Optional[str] = None
    description_en: Optional[str] = None
    description_fa: Optional[str] = None


class NutritionGoalResponse(NutritionGoalBase):
    """Nutrition goal response schema"""
    nutrition_goal_id: int
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)

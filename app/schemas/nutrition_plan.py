"""
Pydantic schemas for Nutrition Plans (Phase 3)
"""
from pydantic import BaseModel, ConfigDict, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from decimal import Decimal


# ========== Meal Schemas ==========
class MealBase(BaseModel):
    """Base schema for meal"""
    meal_type: str = Field(..., pattern="^(breakfast|lunch|dinner|snacks)$")
    name: str = Field(..., max_length=255)
    description: Optional[str] = None
    calories: Optional[int] = None
    protein: Optional[Decimal] = None
    carbs: Optional[Decimal] = None
    fats: Optional[Decimal] = None


class MealCreate(MealBase):
    """Schema for creating meal"""
    pass


class MealResponse(MealBase):
    """Schema for meal response"""
    meal_id: int
    day_id: int
    created_at: datetime
    
    model_config = ConfigDict(
        from_attributes=True,
        json_encoders={Decimal: float}
    )


# ========== Nutrition Day Schemas ==========
class NutritionDayBase(BaseModel):
    """Base schema for nutrition day"""
    day_name: str = Field(..., max_length=50)
    daily_calories: Optional[int] = None


class NutritionDayCreate(NutritionDayBase):
    """Schema for creating nutrition day"""
    meals: List[MealCreate] = []


class NutritionDayResponse(NutritionDayBase):
    """Schema for nutrition day response"""
    day_id: int
    week_id: int
    created_at: datetime
    meals: List[MealResponse] = []
    
    model_config = ConfigDict(
        from_attributes=True,
        json_encoders={Decimal: float}
    )


# ========== Nutrition Week Schemas ==========
class NutritionWeekBase(BaseModel):
    """Base schema for nutrition week"""
    week_number: int = Field(..., ge=1, le=12)
    title: Optional[str] = Field(None, max_length=255)
    description: Optional[str] = None


class NutritionWeekCreate(NutritionWeekBase):
    """Schema for creating nutrition week"""
    days: List[NutritionDayCreate] = []


class NutritionWeekResponse(NutritionWeekBase):
    """Schema for nutrition week response"""
    week_id: int
    plan_id: int
    created_at: datetime
    days: List[NutritionDayResponse] = []
    
    model_config = ConfigDict(
        from_attributes=True,
        json_encoders={Decimal: float}
    )


# ========== Nutrition Plan Schemas ==========
class NutritionPlanBase(BaseModel):
    """Base schema for nutrition plan"""
    name: str = Field(..., max_length=255)
    nutrition_goal_id: Optional[int] = None
    total_weeks: int = Field(..., ge=1, le=12)


class NutritionPlanCreate(NutritionPlanBase):
    """Schema for creating nutrition plan - AI will generate weeks"""
    # User provides basic info, AI generates the rest
    pass


class NutritionPlanUpdate(BaseModel):
    """Schema for updating nutrition plan"""
    name: Optional[str] = Field(None, max_length=255)
    current_week: Optional[int] = Field(None, ge=1)


class NutritionPlanResponse(NutritionPlanBase):
    """Schema for nutrition plan response"""
    plan_id: int
    user_id: int
    current_week: int
    completed_weeks: List[int] = []
    strategy: Optional[Dict[str, Any]] = None
    expectations: Optional[Dict[str, Any]] = None
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(
        from_attributes=True,
        json_encoders={Decimal: float}
    )


class NutritionPlanDetailResponse(NutritionPlanResponse):
    """Schema for nutrition plan with full details including weeks"""
    weeks: List[NutritionWeekResponse] = []
    
    model_config = ConfigDict(
        from_attributes=True,
        json_encoders={Decimal: float}
    )


class NutritionPlanListResponse(BaseModel):
    """Schema for list of nutrition plans"""
    plans: List[NutritionPlanResponse]
    total: int


# ========== Week Completion Schemas ==========
class NutritionWeekCompletionRequest(BaseModel):
    """Schema for marking a week as completed"""
    week_number: int = Field(..., ge=1, le=12)


class NutritionWeekCompletionResponse(BaseModel):
    """Schema for week completion response"""
    plan_id: int
    week_number: int
    current_week: int
    completed_weeks: List[int]
    message: str

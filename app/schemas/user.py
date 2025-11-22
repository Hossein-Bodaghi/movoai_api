"""
Pydantic schemas for User
"""
from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional
from datetime import datetime


class UserBase(BaseModel):
    """Base user schema"""
    name: str = Field(..., min_length=1, max_length=200)
    gender: str = Field(..., pattern="^(male|female|other)$")
    age: int = Field(..., ge=10, le=120)
    daily_activity: str = Field(..., pattern="^(sedentary|lightly_active|moderately_active|very_active|extra_active)$")
    fitness_level: str = Field(..., pattern="^(beginner|intermediate|advanced)$")
    fitness_goals: List[str] = Field(..., min_length=1)
    height_cm: int = Field(..., ge=100, le=250)
    weight_kg: int = Field(..., ge=30, le=300)
    workout_style: Optional[str] = None


class UserCreate(UserBase):
    """Schema for creating a new user"""
    pass


class UserUpdate(BaseModel):
    """Schema for updating user profile"""
    # Basic profile
    age: Optional[int] = Field(None, ge=10, le=120)
    weight: Optional[float] = Field(None, ge=30, le=300)
    height: Optional[float] = Field(None, ge=100, le=250)
    gender: Optional[str] = Field(None, pattern="^(male|female|other)$")
    
    # Fitness fields
    focus: Optional[str] = Field(None, pattern="^(performance_enhancement|body_recomposition|efficiency|rebuilding_rehab)$")
    physical_fitness: Optional[str] = Field(None, pattern="^(novice|beginner|intermediate|advanced)$")
    fitness_days: Optional[int] = Field(None, ge=0, le=7)
    workout_goal_id: Optional[int] = None
    nutrition_goal_id: Optional[int] = None
    
    # Sport fields
    sport: Optional[str] = Field(None, max_length=100)
    sport_days: Optional[int] = Field(None, ge=0, le=7)
    specialized_sport: Optional[str] = Field(None, max_length=100)
    
    # Training fields
    training_location: Optional[str] = Field(None, pattern="^(home|gym)$")
    workout_limitations: Optional[str] = None
    
    # Nutrition fields
    dietary_restrictions: Optional[str] = None
    cooking_time: Optional[str] = Field(None, pattern="^(under_15|15_30|30_60|over_60)$")
    cooking_skill: Optional[str] = Field(None, pattern="^(beginner|intermediate|advanced)$")
    kitchen_appliances: Optional[str] = None  # JSON string or comma-separated
    food_preferences: Optional[str] = None  # JSON string or comma-separated
    forbidden_ingredients: Optional[str] = None  # JSON string or comma-separated


class UserResponse(BaseModel):
    """Schema for user response"""
    id: int  # Will map to user_id via property
    user_id: int
    email: Optional[str] = None
    telegram_id: Optional[int] = None
    
    # Basic profile
    age: Optional[int] = None
    weight: Optional[float] = None
    height: Optional[float] = None
    gender: Optional[str] = None
    
    # Fitness fields
    focus: Optional[str] = None
    physical_fitness: Optional[str] = None
    fitness_days: Optional[int] = None
    workout_goal_id: Optional[int] = None
    nutrition_goal_id: Optional[int] = None
    
    # Sport fields
    sport: Optional[str] = None
    sport_days: Optional[int] = None
    specialized_sport: Optional[str] = None
    
    # Training fields
    training_location: Optional[str] = None
    workout_limitations: Optional[str] = None
    
    # Nutrition fields
    dietary_restrictions: Optional[str] = None
    cooking_time: Optional[str] = None
    cooking_skill: Optional[str] = None
    kitchen_appliances: Optional[str] = None
    food_preferences: Optional[str] = None
    forbidden_ingredients: Optional[str] = None
    
    # System fields
    credits: Optional[int] = 0
    referral_code: Optional[str] = None
    has_used_referral: Optional[bool] = False
    
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    model_config = ConfigDict(from_attributes=True)


class UserWithAuthMethods(UserResponse):
    """User response with auth methods"""
    auth_methods: List["AuthMethodResponse"] = []


# Forward reference resolution
from app.schemas.auth import AuthMethodResponse
UserWithAuthMethods.model_rebuild()

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
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    gender: Optional[str] = Field(None, pattern="^(male|female|other)$")
    age: Optional[int] = Field(None, ge=10, le=120)
    daily_activity: Optional[str] = Field(None, pattern="^(sedentary|lightly_active|moderately_active|very_active|extra_active)$")
    fitness_level: Optional[str] = Field(None, pattern="^(beginner|intermediate|advanced)$")
    fitness_goals: Optional[List[str]] = Field(None, min_length=1)
    height_cm: Optional[int] = Field(None, ge=100, le=250)
    weight_kg: Optional[int] = Field(None, ge=30, le=300)
    workout_style: Optional[str] = None


class UserResponse(UserBase):
    """Schema for user response"""
    id: int
    telegram_id: Optional[int] = None
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


class UserWithAuthMethods(UserResponse):
    """User response with auth methods"""
    auth_methods: List["AuthMethodResponse"] = []


# Forward reference resolution
from app.schemas.auth import AuthMethodResponse
UserWithAuthMethods.model_rebuild()

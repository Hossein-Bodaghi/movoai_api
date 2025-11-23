"""
SQLAlchemy models for Nutrition Plan System (Phase 3)
"""
from sqlalchemy import Column, Integer, String, Text, ForeignKey, CheckConstraint, UniqueConstraint, ARRAY, TIMESTAMP, Numeric
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database.base import Base


class NutritionPlan(Base):
    """Main nutrition plans table"""
    __tablename__ = "nutrition_plans"
    
    plan_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False, index=True)
    nutrition_goal_id = Column(Integer, ForeignKey("nutrition_goals.nutrition_goal_id", ondelete="SET NULL"))
    name = Column(String(255), nullable=False)
    total_weeks = Column(Integer, nullable=False)
    current_week = Column(Integer, default=1)
    completed_weeks = Column(ARRAY(Integer), default=[])
    strategy = Column(JSONB)
    expectations = Column(JSONB)
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="nutrition_plans")
    nutrition_goal = relationship("NutritionGoal")
    weeks = relationship("NutritionWeek", back_populates="plan", cascade="all, delete-orphan")
    
    # Constraints
    __table_args__ = (
        CheckConstraint("total_weeks IN (1, 4, 12)", name="chk_nutrition_total_weeks"),
        CheckConstraint("current_week >= 1", name="chk_nutrition_current_week_positive"),
        CheckConstraint("current_week <= total_weeks", name="chk_nutrition_current_week_range"),
    )


class NutritionWeek(Base):
    """Weekly breakdowns within nutrition plans"""
    __tablename__ = "nutrition_weeks"
    
    week_id = Column(Integer, primary_key=True, index=True)
    plan_id = Column(Integer, ForeignKey("nutrition_plans.plan_id", ondelete="CASCADE"), nullable=False, index=True)
    week_number = Column(Integer, nullable=False)
    title = Column(String(255))
    description = Column(Text)
    created_at = Column(TIMESTAMP, server_default=func.now())
    
    # Relationships
    plan = relationship("NutritionPlan", back_populates="weeks")
    days = relationship("NutritionDay", back_populates="week", cascade="all, delete-orphan")
    
    # Constraints
    __table_args__ = (
        UniqueConstraint("plan_id", "week_number", name="uq_nutrition_plan_week"),
        CheckConstraint("week_number >= 1 AND week_number <= 12", name="chk_nutrition_week_number"),
    )


class NutritionDay(Base):
    """Daily meal plans within each week"""
    __tablename__ = "nutrition_days"
    
    day_id = Column(Integer, primary_key=True, index=True)
    week_id = Column(Integer, ForeignKey("nutrition_weeks.week_id", ondelete="CASCADE"), nullable=False, index=True)
    day_name = Column(String(50), nullable=False)
    daily_calories = Column(Integer)
    created_at = Column(TIMESTAMP, server_default=func.now())
    
    # Relationships
    week = relationship("NutritionWeek", back_populates="days")
    meals = relationship("Meal", back_populates="day", cascade="all, delete-orphan")


class Meal(Base):
    """Individual meals within nutrition days"""
    __tablename__ = "meals"
    
    meal_id = Column(Integer, primary_key=True, index=True)
    day_id = Column(Integer, ForeignKey("nutrition_days.day_id", ondelete="CASCADE"), nullable=False, index=True)
    meal_type = Column(String(20), nullable=False)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    calories = Column(Integer)
    protein = Column(Numeric(5, 1))
    carbs = Column(Numeric(5, 1))
    fats = Column(Numeric(5, 1))
    created_at = Column(TIMESTAMP, server_default=func.now())
    
    # Relationships
    day = relationship("NutritionDay", back_populates="meals")
    
    # Constraints
    __table_args__ = (
        CheckConstraint("meal_type IN ('breakfast', 'lunch', 'dinner', 'snacks')", name="chk_meal_type"),
    )

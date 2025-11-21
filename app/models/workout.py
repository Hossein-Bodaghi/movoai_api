"""
Placeholder models for workout-related tables (to be implemented in Phase 2)
"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text, ARRAY
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.database.base import Base


class WorkoutPlan(Base):
    """Workout plans - to be fully implemented in Phase 2"""
    __tablename__ = "workout_plans"
    
    id = Column(Integer, primary_key=True, index=True)
    name_en = Column(String(100), nullable=True)
    description_en = Column(Text, nullable=True)
    name_fr = Column(String(100), nullable=True)
    description_fr = Column(Text, nullable=True)
    is_template = Column(Boolean, default=False)
    created_by_user_id = Column(Integer, ForeignKey("users.user_id", ondelete="SET NULL"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    plan_exercises = relationship("PlanExercise", back_populates="plan", cascade="all, delete-orphan")
    user_plans = relationship("UserPlan", back_populates="plan", cascade="all, delete-orphan")


class Exercise(Base):
    """Exercises - to be fully implemented in Phase 2"""
    __tablename__ = "exercises"
    
    id = Column(Integer, primary_key=True, index=True)
    exercise_en = Column(String(100), nullable=True)
    difficulty_en = Column(String(50), nullable=True)
    goal_en = Column(String(50), nullable=True)
    muscles_en = Column(ARRAY(String), default=[])
    instructions_en = Column(ARRAY(String), default=[])
    equipments_en = Column(ARRAY(String), default=[])
    exercise_fr = Column(String(100), nullable=True)
    difficulty_fr = Column(String(50), nullable=True)
    goal_fr = Column(String(50), nullable=True)
    muscles_fr = Column(ARRAY(String), default=[])
    instructions_fr = Column(ARRAY(String), default=[])
    male_gif_urls = Column(ARRAY(String), default=[])
    female_gif_urls = Column(ARRAY(String), default=[])
    
    # Relationships
    plan_exercises = relationship("PlanExercise", back_populates="exercise")


class PlanExercise(Base):
    """Plan exercises junction table - to be fully implemented in Phase 2"""
    __tablename__ = "plan_exercises"
    
    id = Column(Integer, primary_key=True, index=True)
    plan_id = Column(Integer, ForeignKey("workout_plans.id", ondelete="CASCADE"))
    exercise_id = Column(Integer, ForeignKey("exercises.id", ondelete="CASCADE"))
    day_number = Column(Integer, nullable=True)
    week_number = Column(Integer, default=1)
    sets = Column(Integer, nullable=True)
    reps = Column(Integer, nullable=True)
    duration_seconds = Column(Integer, nullable=True)
    rest_seconds = Column(Integer, nullable=True)
    order_in_day = Column(Integer, nullable=True)
    
    # Relationships
    plan = relationship("WorkoutPlan", back_populates="plan_exercises")
    exercise = relationship("Exercise", back_populates="plan_exercises")
    workout_logs = relationship("UserWorkoutLog", back_populates="plan_exercise", cascade="all, delete-orphan")


class UserPlan(Base):
    """User workout plans - to be fully implemented in Phase 2"""
    __tablename__ = "user_plans"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.user_id", ondelete="CASCADE"))
    plan_id = Column(Integer, ForeignKey("workout_plans.id", ondelete="CASCADE"))
    start_date = Column(DateTime(timezone=True), nullable=True)
    status = Column(String(20), default='active')
    
    # Relationships
    user = relationship("User", back_populates="user_plans")
    plan = relationship("WorkoutPlan", back_populates="user_plans")


class UserWorkoutLog(Base):
    """User workout logs - to be fully implemented in Phase 2"""
    __tablename__ = "user_workout_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.user_id", ondelete="CASCADE"))
    plan_exercise_id = Column(Integer, ForeignKey("plan_exercises.id", ondelete="CASCADE"))
    date_performed = Column(DateTime(timezone=True), nullable=True)
    sets_completed = Column(Integer, nullable=True)
    reps_completed = Column(Integer, nullable=True)
    duration_seconds_completed = Column(Integer, nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="workout_logs")
    plan_exercise = relationship("PlanExercise", back_populates="workout_logs")

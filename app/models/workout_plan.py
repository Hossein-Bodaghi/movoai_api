"""
SQLAlchemy models for Workout Plan System (Phase 2)
"""
from sqlalchemy import Column, Integer, String, Text, ForeignKey, CheckConstraint, UniqueConstraint, ARRAY, TIMESTAMP
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database.base import Base


class WorkoutPlan(Base):
    """Main workout plans table"""
    __tablename__ = "workout_plans"
    
    plan_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False, index=True)
    workout_goal_id = Column(Integer, ForeignKey("workout_goals.workout_goal_id", ondelete="SET NULL"))
    name = Column(String(255), nullable=False)
    total_weeks = Column(Integer, nullable=False)
    current_week = Column(Integer, default=1)
    completed_weeks = Column(ARRAY(Integer), default=[])
    strategy = Column(JSONB)
    expectations = Column(JSONB)
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="workout_plans")
    workout_goal = relationship("WorkoutGoal")
    weeks = relationship("WorkoutWeek", back_populates="workout_plan", cascade="all, delete-orphan")
    
    # Constraints
    __table_args__ = (
        CheckConstraint("total_weeks IN (1, 4, 12)", name="chk_workout_total_weeks"),
        CheckConstraint("current_week >= 1", name="chk_workout_current_week_positive"),
        CheckConstraint("current_week <= total_weeks", name="chk_workout_current_week_range"),
    )


class WorkoutWeek(Base):
    """Weekly breakdowns within workout plans"""
    __tablename__ = "workout_weeks"
    
    week_id = Column(Integer, primary_key=True, index=True)
    plan_id = Column(Integer, ForeignKey("workout_plans.plan_id", ondelete="CASCADE"), nullable=False, index=True)
    week_number = Column(Integer, nullable=False)
    title = Column(String(255))
    description = Column(Text)
    created_at = Column(TIMESTAMP, server_default=func.now())
    
    # Relationships
    workout_plan = relationship("WorkoutPlan", back_populates="weeks")
    days = relationship("WorkoutDay", back_populates="week", cascade="all, delete-orphan")
    
    # Constraints
    __table_args__ = (
        UniqueConstraint("plan_id", "week_number", name="uq_workout_plan_week"),
        CheckConstraint("week_number >= 1 AND week_number <= 12", name="chk_workout_week_number"),
    )


class WorkoutDay(Base):
    """Daily workouts within each week"""
    __tablename__ = "workout_days"
    
    day_id = Column(Integer, primary_key=True, index=True)
    week_id = Column(Integer, ForeignKey("workout_weeks.week_id", ondelete="CASCADE"), nullable=False, index=True)
    day_name = Column(String(50), nullable=False)
    focus = Column(Text)
    warmup = Column(Text)
    cooldown = Column(Text)
    created_at = Column(TIMESTAMP, server_default=func.now())
    
    # Relationships
    week = relationship("WorkoutWeek", back_populates="days")
    exercises = relationship("WorkoutDayExercise", back_populates="day", cascade="all, delete-orphan")


class WorkoutDayExercise(Base):
    """Junction table linking workout days to exercises with AI-generated parameters"""
    __tablename__ = "workout_day_exercises"
    
    workout_day_exercise_id = Column(Integer, primary_key=True, index=True)
    day_id = Column(Integer, ForeignKey("workout_days.day_id", ondelete="CASCADE"), nullable=False, index=True)
    exercise_id = Column(Integer, ForeignKey("exercise.exercise_id", ondelete="CASCADE"), nullable=False, index=True)
    
    # AI-generated attributes for this specific workout day
    sets = Column(String(50))
    reps = Column(String(50))
    tempo = Column(String(50))
    rest = Column(String(50))
    notes = Column(Text)
    exercise_order = Column(Integer, nullable=False)
    
    created_at = Column(TIMESTAMP, server_default=func.now())
    
    # Relationships
    day = relationship("WorkoutDay", back_populates="exercises")
    exercise = relationship("Exercise")
    
    # Constraints
    __table_args__ = (
        UniqueConstraint("day_id", "exercise_order", name="uq_workout_day_exercise_order"),
    )

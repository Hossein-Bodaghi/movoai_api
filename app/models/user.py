"""
User model
"""
from sqlalchemy import Column, Integer, BigInteger, String, Float, ARRAY, DateTime, Text
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.database.base import Base


class User(Base):
    """User model - matches existing users table from schema.sql"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    telegram_id = Column(BigInteger, unique=True, nullable=True, index=True)
    name = Column(Text, nullable=False)
    gender = Column(Text, nullable=False)
    age = Column(Integer, nullable=False)
    daily_activity = Column(Text, nullable=False)
    fitness_level = Column(Text, nullable=False)
    fitness_goals = Column(ARRAY(Text), nullable=False)
    height_cm = Column(Integer, nullable=False)
    weight_kg = Column(Integer, nullable=False)
    workout_style = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    # Relationships
    auth_methods = relationship("UserAuthMethod", back_populates="user", cascade="all, delete-orphan")
    user_plans = relationship("UserPlan", back_populates="user", cascade="all, delete-orphan")
    workout_logs = relationship("UserWorkoutLog", back_populates="user", cascade="all, delete-orphan")

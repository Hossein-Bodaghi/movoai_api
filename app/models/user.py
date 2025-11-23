"""
User model
"""
from sqlalchemy import Column, Integer, BigInteger, String, Float, Boolean, ARRAY, DateTime, Text, Numeric, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.database.base import Base


class User(Base):
    """User model - matches existing users table from database"""
    __tablename__ = "users"
    
    # Primary key - database uses user_id
    user_id = Column(Integer, primary_key=True, index=True, name='user_id')
    
    # Authentication fields
    email = Column(String(255), unique=True, nullable=True)
    password_hash = Column(String(255), nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    telegram_id = Column(BigInteger, unique=True, nullable=True, index=True)
    
    # Profile fields
    age = Column(Integer, nullable=True)
    weight = Column(Numeric(5, 2), nullable=True)
    height = Column(Numeric(5, 2), nullable=True)
    gender = Column(String(20), nullable=True)
    
    # Fitness fields
    focus = Column(String(50), nullable=True)
    physical_fitness = Column(String(50), nullable=True)
    fitness_days = Column(Integer, nullable=True)
    workout_goal_id = Column(Integer, ForeignKey('workout_goals.workout_goal_id', ondelete='SET NULL'), nullable=True)
    nutrition_goal_id = Column(Integer, ForeignKey('nutrition_goals.nutrition_goal_id', ondelete='SET NULL'), nullable=True)
    
    # Sport fields
    sport = Column(String(100), nullable=True)
    sport_days = Column(Integer, nullable=True)
    specialized_sport = Column(String(100), nullable=True)
    
    # Training fields
    training_location = Column(String(50), nullable=True)
    workout_limitations = Column(Text, nullable=True)
    
    # Nutrition fields
    dietary_restrictions = Column(Text, nullable=True)
    cooking_time = Column(String(50), nullable=True)
    cooking_skill = Column(String(50), nullable=True)
    kitchen_appliances = Column(ARRAY(Text), nullable=True)
    food_preferences = Column(ARRAY(Text), nullable=True)
    forbidden_ingredients = Column(ARRAY(Text), nullable=True)
    
    # Credits and referrals
    credits = Column(Integer, default=0, nullable=False)
    referral_code = Column(String(20), unique=True, nullable=True)
    has_used_referral = Column(Boolean, default=False, nullable=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Relationships
    auth_methods = relationship("UserAuthMethod", back_populates="user", cascade="all, delete-orphan", foreign_keys="[UserAuthMethod.user_id]")
    workout_goal = relationship("WorkoutGoal", back_populates="users", foreign_keys=[workout_goal_id])
    nutrition_goal = relationship("NutritionGoal", back_populates="users", foreign_keys=[nutrition_goal_id])
    workout_plans = relationship("WorkoutPlan", back_populates="user", cascade="all, delete-orphan")
    nutrition_plans = relationship("NutritionPlan", back_populates="user", cascade="all, delete-orphan")
    
    # Property for backward compatibility
    @property
    def id(self):
        return self.user_id

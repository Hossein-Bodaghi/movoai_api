"""
Feedback models
"""
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, CheckConstraint, Boolean, Text
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import JSONB

from app.database.base import Base


class Feedback(Base):
    """User feedback for workout/nutrition weeks"""
    __tablename__ = "feedback"
    
    feedback_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.user_id', ondelete='CASCADE'), nullable=False)
    week_table = Column(String(20), nullable=False)
    week_id = Column(Integer, nullable=False)
    responses = Column(JSONB, nullable=False)
    submitted_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    user = relationship("User", backref="feedback_submissions")
    
    # Add constraint
    __table_args__ = (
        CheckConstraint(
            "week_table IN ('workout_weeks', 'nutrition_weeks')",
            name='check_week_table'
        ),
    )


class FeedbackQuestion(Base):
    """AI-generated feedback questions for specific weeks"""
    __tablename__ = "feedback_questions"
    
    question_id = Column(Integer, primary_key=True, index=True)
    week_table = Column(String(20), nullable=False)
    week_id = Column(Integer, nullable=False)
    focus = Column(String(50), nullable=False)
    question_text = Column(Text, nullable=False)
    question_type = Column(String(20), nullable=False)
    options = Column(JSONB, nullable=True)
    allow_text = Column(Boolean, default=False, nullable=False)
    dynamic_options = Column(String(20), nullable=True)
    question_order = Column(Integer, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Add constraints
    __table_args__ = (
        CheckConstraint(
            "week_table IN ('workout_weeks', 'nutrition_weeks')",
            name='check_question_week_table'
        ),
        CheckConstraint(
            "focus IN ('performance_enhancement', 'body_recomposition', 'efficiency', 'rebuilding_rehab')",
            name='check_question_focus'
        ),
        CheckConstraint(
            "question_type IN ('radio', 'multi-select')",
            name='check_question_type'
        ),
        CheckConstraint(
            "dynamic_options IN ('exercises', 'meals') OR dynamic_options IS NULL",
            name='check_dynamic_options'
        ),
    )

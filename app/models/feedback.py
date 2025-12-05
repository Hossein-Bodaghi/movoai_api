"""
Feedback model
"""
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, CheckConstraint
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

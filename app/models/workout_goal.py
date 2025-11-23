"""
WorkoutGoal model
"""
from sqlalchemy import Column, Integer, String, Text, DateTime
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.database.base import Base


class WorkoutGoal(Base):
    """WorkoutGoal model - workout plan generation goals"""
    __tablename__ = "workout_goals"
    
    workout_goal_id = Column(Integer, primary_key=True, index=True)
    focus = Column(String(50), nullable=False, index=True)
    goal_key = Column(String(100), unique=True, nullable=False, index=True)
    goal_label_en = Column(String(255), nullable=False)
    goal_label_fa = Column(String(255), nullable=True)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    # Relationships
    users = relationship("User", back_populates="workout_goal", foreign_keys="[User.workout_goal_id]")
    
    def __repr__(self):
        return f"<WorkoutGoal(id={self.workout_goal_id}, key={self.goal_key}, focus={self.focus})>"

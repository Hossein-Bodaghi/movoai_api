"""
NutritionGoal model
"""
from sqlalchemy import Column, Integer, String, Text, DateTime
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.database.base import Base


class NutritionGoal(Base):
    """NutritionGoal model - nutrition plan generation goals"""
    __tablename__ = "nutrition_goals"
    
    nutrition_goal_id = Column(Integer, primary_key=True, index=True)
    focus = Column(String(50), nullable=False, index=True)
    goal_key = Column(String(100), unique=True, nullable=False, index=True)
    goal_label_en = Column(String(255), nullable=False)
    goal_label_fa = Column(String(255), nullable=True)
    description_en = Column(Text, nullable=True)
    description_fa = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    # Relationships
    users = relationship("User", back_populates="nutrition_goal", foreign_keys="[User.nutrition_goal_id]")
    
    def __repr__(self):
        return f"<NutritionGoal(id={self.nutrition_goal_id}, key={self.goal_key}, focus={self.focus})>"

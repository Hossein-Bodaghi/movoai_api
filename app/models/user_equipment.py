"""
User equipment models (home and gym)
"""
from sqlalchemy import Column, Integer, ForeignKey, DateTime
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.database.base import Base


class UserHomeEquipment(Base):
    """User home equipment - junction table linking users to their available equipment"""
    __tablename__ = "user_home_equipment"
    
    user_equipment_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.user_id', ondelete='CASCADE'), nullable=False)
    equipment_id = Column(Integer, ForeignKey('equipment.equipment_id', ondelete='CASCADE'), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    user = relationship("User", back_populates="home_equipment_rel")
    equipment = relationship("Equipment")


class UserGymEquipment(Base):
    """User gym equipment - junction table linking users to their available gym equipment"""
    __tablename__ = "user_gym_equipment"
    
    user_equipment_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.user_id', ondelete='CASCADE'), nullable=False)
    equipment_id = Column(Integer, ForeignKey('equipment.equipment_id', ondelete='CASCADE'), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    user = relationship("User", back_populates="gym_equipment_rel")
    equipment = relationship("Equipment")

"""
Exercise model - references the exercise table from the database
"""
from sqlalchemy import Column, Integer, String, Text, ForeignKey, ARRAY, Table
from sqlalchemy.orm import relationship
from app.database.base import Base


# Lookup tables
class Difficulty(Base):
    """Difficulty levels for exercises"""
    __tablename__ = "difficulty"
    
    difficulty_id = Column(Integer, primary_key=True)
    name_en = Column(String(100), unique=True, nullable=False)
    name_fa = Column(String(100), nullable=False)


class Equipment(Base):
    """Equipment types for exercises"""
    __tablename__ = "equipment"
    
    equipment_id = Column(Integer, primary_key=True)
    name_en = Column(String(100), unique=True, nullable=False)
    name_fa = Column(String(100), nullable=False)


class Muscle(Base):
    """Muscle groups for exercises"""
    __tablename__ = "muscle"
    
    muscle_id = Column(Integer, primary_key=True)
    name_en = Column(String(100), unique=True, nullable=False)
    name_fa = Column(String(100), nullable=False)


# Junction tables (existing in DB)
exercise_equipment = Table(
    'exercise_equipment',
    Base.metadata,
    Column('exercise_id', Integer, ForeignKey('exercise.exercise_id', ondelete='CASCADE'), primary_key=True),
    Column('equipment_id', Integer, ForeignKey('equipment.equipment_id', ondelete='CASCADE'), primary_key=True)
)

exercise_muscle = Table(
    'exercise_muscle',
    Base.metadata,
    Column('exercise_id', Integer, ForeignKey('exercise.exercise_id', ondelete='CASCADE'), primary_key=True),
    Column('muscle_id', Integer, ForeignKey('muscle.muscle_id', ondelete='CASCADE'), primary_key=True)
)


class Exercise(Base):
    """Exercise model - matches existing exercise table from database"""
    __tablename__ = "exercise"
    
    exercise_id = Column(Integer, primary_key=True, index=True)
    name_en = Column(Text, nullable=False)
    name_fa = Column(Text, nullable=False)
    
    difficulty_id = Column(Integer, ForeignKey("difficulty.difficulty_id"))
    style_id = Column(Integer, ForeignKey("style.style_id"))
    
    instructions_en = Column(ARRAY(Text))
    instructions_fa = Column(ARRAY(Text))
    
    page_url = Column(Text)
    
    male_urls = Column(ARRAY(Text))
    female_urls = Column(ARRAY(Text))
    male_image_urls = Column(ARRAY(Text))
    female_image_urls = Column(ARRAY(Text))
    
    # Relationships
    difficulty = relationship("Difficulty")
    equipment = relationship("Equipment", secondary=exercise_equipment, lazy="joined")
    muscles = relationship("Muscle", secondary=exercise_muscle, lazy="joined")

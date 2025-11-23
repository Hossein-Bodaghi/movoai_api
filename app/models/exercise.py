"""
Exercise model - references the exercise table from the database
"""
from sqlalchemy import Column, Integer, String, Text, ForeignKey, ARRAY
from sqlalchemy.orm import relationship
from app.database.base import Base


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
    
    # Relationships (basic - can be extended)
    # difficulty = relationship("Difficulty")
    # style = relationship("Style")

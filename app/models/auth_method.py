"""
User authentication methods model
"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, JSON, UniqueConstraint
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.database.base import Base


class UserAuthMethod(Base):
    """User authentication methods - stores multiple login methods per user"""
    __tablename__ = "user_auth_methods"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False, index=True)
    auth_provider = Column(String(20), nullable=False)  # telegram, sms, email, google
    auth_identifier = Column(String(255), nullable=False, index=True)  # telegram_id, phone, email, google_id
    auth_data = Column(JSON, nullable=True)  # Additional data like tokens, usernames
    is_verified = Column(Boolean, default=True, nullable=False)
    is_primary = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Relationships
    user = relationship("User", back_populates="auth_methods")
    
    # Constraints: unique combination of provider and identifier
    __table_args__ = (
        UniqueConstraint('auth_provider', 'auth_identifier', name='uix_provider_identifier'),
    )

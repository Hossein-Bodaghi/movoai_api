"""
Verification codes model for SMS and Email authentication
"""
from sqlalchemy import Column, Integer, String, DateTime, Boolean
from sqlalchemy.sql import func

from app.database.base import Base


class VerificationCode(Base):
    """Verification codes for SMS and Email authentication"""
    __tablename__ = "verification_codes"
    
    id = Column(Integer, primary_key=True, index=True)
    identifier = Column(String(255), nullable=False, index=True)  # phone number or email
    code = Column(String(6), nullable=False)  # 6-digit code
    code_type = Column(String(10), nullable=False)  # 'sms' or 'email'
    expires_at = Column(DateTime(timezone=True), nullable=False)
    attempts = Column(Integer, default=0, nullable=False)
    verified = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

"""
Pydantic schemas for Authentication
"""
from pydantic import BaseModel, Field, EmailStr, ConfigDict
from typing import Optional, Dict, Any
from datetime import datetime


# ============= Token Schemas =============
class Token(BaseModel):
    """Token response schema"""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class TokenRefresh(BaseModel):
    """Token refresh request"""
    refresh_token: str


class TokenData(BaseModel):
    """Token payload data"""
    user_id: Optional[int] = None


# ============= Telegram Auth Schemas =============
class TelegramAuthRequest(BaseModel):
    """Telegram authentication request"""
    id: int = Field(..., description="Telegram user ID")
    first_name: str
    last_name: Optional[str] = None
    username: Optional[str] = None
    photo_url: Optional[str] = None
    auth_date: int
    hash: str


class TelegramAuthResponse(BaseModel):
    """Telegram authentication response"""
    user: "UserResponse"
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    is_new_user: bool = False


# ============= Phone/SMS Auth Schemas =============
class PhoneSendCodeRequest(BaseModel):
    """Request to send SMS code"""
    phone_number: str = Field(..., pattern=r'^\+?[1-9]\d{1,14}$', description="Phone number in E.164 format")


class PhoneVerifyCodeRequest(BaseModel):
    """Request to verify SMS code"""
    phone_number: str = Field(..., pattern=r'^\+?[1-9]\d{1,14}$')
    code: str = Field(..., pattern=r'^\d{6}$', description="6-digit verification code")
    user_data: Optional["UserCreate"] = None  # Required for new users


class PhoneAuthResponse(BaseModel):
    """Phone authentication response"""
    user: "UserResponse"
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    is_new_user: bool = False


class CodeSentResponse(BaseModel):
    """Response after sending verification code"""
    message: str
    expires_in_seconds: int


# ============= Email Auth Schemas =============
class EmailSendCodeRequest(BaseModel):
    """Request to send email code"""
    email: EmailStr


class EmailVerifyCodeRequest(BaseModel):
    """Request to verify email code"""
    email: EmailStr
    code: str = Field(..., pattern=r'^\d{6}$', description="6-digit verification code")
    user_data: Optional["UserCreate"] = None  # Required for new users


class EmailAuthResponse(BaseModel):
    """Email authentication response"""
    user: "UserResponse"
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    is_new_user: bool = False


# ============= Google OAuth Schemas =============
class GoogleAuthResponse(BaseModel):
    """Google authentication response"""
    user: "UserResponse"
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    is_new_user: bool = False


# ============= Auth Method Management Schemas =============
class AuthMethodBase(BaseModel):
    """Base auth method schema"""
    auth_provider: str = Field(..., pattern="^(telegram|sms|email|google)$")
    auth_identifier: str


class AuthMethodCreate(AuthMethodBase):
    """Create auth method"""
    auth_data: Optional[Dict[str, Any]] = None


class AuthMethodResponse(AuthMethodBase):
    """Auth method response"""
    id: int
    user_id: int
    is_verified: bool
    is_primary: bool
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


class AuthMethodUpdate(BaseModel):
    """Update auth method"""
    is_primary: Optional[bool] = None


class LinkAccountRequest(BaseModel):
    """Request to link additional auth method to existing account"""
    pass  # Specific data depends on auth type


# ============= General Auth Schemas =============
class MessageResponse(BaseModel):
    """Generic message response"""
    message: str


# Forward reference resolution
from app.schemas.user import UserResponse, UserCreate

TelegramAuthResponse.model_rebuild()
PhoneVerifyCodeRequest.model_rebuild()
PhoneAuthResponse.model_rebuild()
EmailVerifyCodeRequest.model_rebuild()
EmailAuthResponse.model_rebuild()
GoogleAuthResponse.model_rebuild()

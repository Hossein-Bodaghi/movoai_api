"""
Application Configuration
"""
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    
    # Database
    DATABASE_URL: str
    
    # JWT
    JWT_SECRET_KEY: str
    JWT_REFRESH_SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    REFRESH_TOKEN_EXPIRE_DAYS: int = 30
    
    # Telegram
    TELEGRAM_BOT_TOKEN: str
    TELEGRAM_BOT_USERNAME: str
    
    # Twilio (SMS)
    TWILIO_ACCOUNT_SID: Optional[str] = None
    TWILIO_AUTH_TOKEN: Optional[str] = None
    TWILIO_PHONE_NUMBER: Optional[str] = None
    
    # SendGrid (Email)
    SENDGRID_API_KEY: Optional[str] = None
    EMAIL_FROM_ADDRESS: str = "noreply@movoai.com"
    EMAIL_FROM_NAME: str = "MovoAI"
    
    # Google OAuth
    GOOGLE_CLIENT_ID: Optional[str] = None
    GOOGLE_CLIENT_SECRET: Optional[str] = None
    GOOGLE_REDIRECT_URI: Optional[str] = None
    
    # Application
    APP_NAME: str = "MovoAI API"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    FRONTEND_URL: str = "http://localhost:5173"
    
    # Security
    RATE_LIMIT_PER_MINUTE: int = 5
    CODE_EXPIRY_MINUTES_SMS: int = 5
    CODE_EXPIRY_MINUTES_EMAIL: int = 10
    MAX_CODE_ATTEMPTS: int = 3
    MAX_CODES_PER_HOUR: int = 3
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()

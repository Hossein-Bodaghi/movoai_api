"""
Security utilities for authentication and authorization
"""
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import hashlib
import hmac
import secrets
from jose import JWTError, jwt
from passlib.context import CryptContext

from app.core.config import settings


# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against a hash"""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Hash a password"""
    return pwd_context.hash(password)


def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """Create JWT access token"""
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire, "type": "access"})
    encoded_jwt = jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
    return encoded_jwt


def create_refresh_token(data: Dict[str, Any]) -> str:
    """Create JWT refresh token"""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire, "type": "refresh"})
    encoded_jwt = jwt.encode(to_encode, settings.JWT_REFRESH_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
    return encoded_jwt


def decode_access_token(token: str) -> Optional[Dict[str, Any]]:
    """Decode and verify JWT access token"""
    try:
        payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        if payload.get("type") != "access":
            return None
        return payload
    except JWTError:
        return None


def decode_refresh_token(token: str) -> Optional[Dict[str, Any]]:
    """Decode and verify JWT refresh token"""
    try:
        payload = jwt.decode(token, settings.JWT_REFRESH_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        if payload.get("type") != "refresh":
            return None
        return payload
    except JWTError:
        return None


def verify_telegram_auth(auth_data: Dict[str, Any]) -> bool:
    """
    Verify Telegram login data
    https://core.telegram.org/widgets/login#checking-authorization
    """
    check_hash = auth_data.get("hash")
    if not check_hash:
        return False
    
    # Create data check string
    data_check_arr = []
    for key, value in sorted(auth_data.items()):
        if key != "hash":
            data_check_arr.append(f"{key}={value}")
    data_check_string = "\n".join(data_check_arr)
    
    # Calculate secret key
    secret_key = hashlib.sha256(settings.TELEGRAM_BOT_TOKEN.encode()).digest()
    
    # Calculate hash
    calculated_hash = hmac.new(
        secret_key,
        data_check_string.encode(),
        hashlib.sha256
    ).hexdigest()
    
    # Verify hash matches
    if calculated_hash != check_hash:
        return False
    
    # Check auth date (not older than 1 day)
    auth_date = auth_data.get("auth_date")
    if auth_date:
        try:
            auth_timestamp = int(auth_date)
            current_timestamp = int(datetime.utcnow().timestamp())
            if current_timestamp - auth_timestamp > 86400:  # 24 hours
                return False
        except (ValueError, TypeError):
            return False
    
    return True


def generate_verification_code() -> str:
    """Generate a 6-digit verification code"""
    return str(secrets.randbelow(1000000)).zfill(6)


def generate_secure_token(length: int = 32) -> str:
    """Generate a secure random token"""
    return secrets.token_urlsafe(length)

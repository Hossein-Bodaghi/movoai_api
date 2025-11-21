"""
Optional authentication dependencies for FastAPI
Allows endpoints to work with or without authentication
"""
from typing import Optional
from fastapi import Depends, Header
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.core.security import decode_access_token
from app.models.user import User


# HTTP Bearer token scheme (optional)
security_optional = HTTPBearer(auto_error=False)


async def get_optional_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security_optional),
    db: Session = Depends(get_db)
) -> Optional[User]:
    """
    Dependency to get current authenticated user from JWT token (OPTIONAL)
    Returns None if no valid token is provided
    Endpoints can work for both authenticated and anonymous users
    """
    if credentials is None:
        return None
    
    token = credentials.credentials
    
    # Decode token
    payload = decode_access_token(token)
    if payload is None:
        return None
    
    user_id: Optional[int] = payload.get("user_id")
    if user_id is None:
        return None
    
    # Get user from database
    user = db.query(User).filter(User.user_id == user_id).first()
    return user


async def get_user_by_id_param(
    user_id: int,
    db: Session = Depends(get_db)
) -> Optional[User]:
    """
    Get user by user_id path parameter (no JWT validation)
    Used for Phase 2 endpoints that work with simple user_id
    WARNING: This provides NO security - Phase 4 will replace this
    """
    user = db.query(User).filter(User.user_id == user_id).first()
    return user


async def get_session_id(
    x_session_id: Optional[str] = Header(None)
) -> Optional[str]:
    """
    Get session ID from header for anonymous tracking
    Used for AI chat sessions and temporary data
    """
    return x_session_id

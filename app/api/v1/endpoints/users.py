"""
User management endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload

from app.database.session import get_db
from app.models.user import User
from app.models.auth_method import UserAuthMethod
from app.schemas.user import UserResponse, UserUpdate, UserWithAuthMethods
from app.schemas.auth import MessageResponse
from app.dependencies import get_current_user

router = APIRouter()


@router.get("/me", response_model=UserWithAuthMethods)
async def get_current_user_profile(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get current user profile with auth methods
    """
    # Reload user with auth methods
    user = db.query(User).options(
        joinedload(User.auth_methods)
    ).filter(User.user_id == current_user.user_id).first()
    
    return UserWithAuthMethods.model_validate(user)


@router.put("/me", response_model=UserResponse)
async def update_current_user_profile(
    user_update: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update current user profile
    """
    # Update only provided fields
    update_data = user_update.model_dump(exclude_unset=True)
    
    for field, value in update_data.items():
        setattr(current_user, field, value)
    
    db.commit()
    db.refresh(current_user)
    
    return UserResponse.model_validate(current_user)


@router.delete("/me", response_model=MessageResponse)
async def delete_current_user_account(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Delete current user account
    This will cascade delete all auth methods, plans, and logs
    """
    db.delete(current_user)
    db.commit()
    
    return MessageResponse(message="Account deleted successfully")


@router.get("/{user_id}", response_model=UserResponse)
async def get_user_by_id(
    user_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get user by ID (only self or admin)
    For now, users can only access their own profile
    """
    if user_id != current_user.user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this user"
        )
    
    user = db.query(User).filter(User.user_id == user_id).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return UserResponse.model_validate(user)

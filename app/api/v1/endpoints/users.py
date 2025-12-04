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
    Get current user profile with auth methods and goals
    """
    from app.models.user_equipment import UserHomeEquipment, UserGymEquipment
    
    # Reload user with auth methods, goals, and equipment
    user = db.query(User).options(
        joinedload(User.auth_methods),
        joinedload(User.workout_goal),
        joinedload(User.nutrition_goal),
        joinedload(User.home_equipment_rel).joinedload(UserHomeEquipment.equipment),
        joinedload(User.gym_equipment_rel).joinedload(UserGymEquipment.equipment)
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
    from app.models.user_equipment import UserHomeEquipment, UserGymEquipment
    
    # Update only provided fields
    update_data = user_update.model_dump(exclude_unset=True)
    
    # Handle home_equipment separately
    home_equipment_ids = update_data.pop('home_equipment', None)
    # Handle gym_equipment separately
    gym_equipment_ids = update_data.pop('gym_equipment', None)
    
    # Update regular fields
    for field, value in update_data.items():
        setattr(current_user, field, value)
    
    # Update home equipment if provided
    if home_equipment_ids is not None:
        # Delete existing equipment
        db.query(UserHomeEquipment).filter(
            UserHomeEquipment.user_id == current_user.user_id
        ).delete()
        
        # Insert new equipment
        if home_equipment_ids:
            for equipment_id in home_equipment_ids:
                new_equipment = UserHomeEquipment(
                    user_id=current_user.user_id,
                    equipment_id=equipment_id
                )
                db.add(new_equipment)
    
    # Update gym equipment if provided
    if gym_equipment_ids is not None:
        # Delete existing equipment
        db.query(UserGymEquipment).filter(
            UserGymEquipment.user_id == current_user.user_id
        ).delete()
        
        # Insert new equipment
        if gym_equipment_ids:
            for equipment_id in gym_equipment_ids:
                new_equipment = UserGymEquipment(
                    user_id=current_user.user_id,
                    equipment_id=equipment_id
                )
                db.add(new_equipment)
    
    db.commit()
    db.refresh(current_user)
    
    # Reload with equipment to include in response
    user = db.query(User).options(
        joinedload(User.home_equipment_rel).joinedload(UserHomeEquipment.equipment),
        joinedload(User.gym_equipment_rel).joinedload(UserGymEquipment.equipment)
    ).filter(User.user_id == current_user.user_id).first()
    
    return UserResponse.model_validate(user)


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

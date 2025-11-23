"""
Goals endpoints - Workout and Nutrition goals
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from app.database.session import get_db
from app.models.workout_goal import WorkoutGoal
from app.models.nutrition_goal import NutritionGoal
from app.schemas.goal import WorkoutGoalResponse, NutritionGoalResponse

router = APIRouter()


# =============== Workout Goals ===============
@router.get("/workout", response_model=List[WorkoutGoalResponse])
async def get_workout_goals(
    focus: Optional[str] = Query(None, description="Filter by focus area: performance_enhancement, body_recomposition, efficiency, rebuilding_rehab"),
    db: Session = Depends(get_db)
):
    """
    Get all workout goals, optionally filtered by focus area.
    Returns 20 total goals (5 per focus area).
    """
    query = db.query(WorkoutGoal)
    
    if focus:
        # Validate focus value
        valid_focus = ['performance_enhancement', 'body_recomposition', 'efficiency', 'rebuilding_rehab']
        if focus not in valid_focus:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid focus. Must be one of: {', '.join(valid_focus)}"
            )
        query = query.filter(WorkoutGoal.focus == focus)
    
    goals = query.order_by(WorkoutGoal.focus, WorkoutGoal.goal_key).all()
    return goals


@router.get("/workout/{goal_id}", response_model=WorkoutGoalResponse)
async def get_workout_goal_by_id(
    goal_id: int,
    db: Session = Depends(get_db)
):
    """
    Get a specific workout goal by ID
    """
    goal = db.query(WorkoutGoal).filter(WorkoutGoal.workout_goal_id == goal_id).first()
    
    if not goal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workout goal not found"
        )
    
    return goal


# =============== Nutrition Goals ===============
@router.get("/nutrition", response_model=List[NutritionGoalResponse])
async def get_nutrition_goals(
    focus: Optional[str] = Query(None, description="Filter by focus area: performance_enhancement, body_recomposition, efficiency, rebuilding_rehab"),
    db: Session = Depends(get_db)
):
    """
    Get all nutrition goals, optionally filtered by focus area.
    Returns 20 total goals (5 per focus area).
    """
    query = db.query(NutritionGoal)
    
    if focus:
        # Validate focus value
        valid_focus = ['performance_enhancement', 'body_recomposition', 'efficiency', 'rebuilding_rehab']
        if focus not in valid_focus:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid focus. Must be one of: {', '.join(valid_focus)}"
            )
        query = query.filter(NutritionGoal.focus == focus)
    
    goals = query.order_by(NutritionGoal.focus, NutritionGoal.goal_key).all()
    return goals


@router.get("/nutrition/{goal_id}", response_model=NutritionGoalResponse)
async def get_nutrition_goal_by_id(
    goal_id: int,
    db: Session = Depends(get_db)
):
    """
    Get a specific nutrition goal by ID
    """
    goal = db.query(NutritionGoal).filter(NutritionGoal.nutrition_goal_id == goal_id).first()
    
    if not goal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Nutrition goal not found"
        )
    
    return goal

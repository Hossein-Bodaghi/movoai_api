"""
Workout Plan endpoints (Phase 2)
Includes mock AI generation for workout plans until AI agents are implemented
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload
from typing import List
import random

from app.database.session import get_db
from app.models.user import User
from app.models.workout_plan import WorkoutPlan, WorkoutWeek, WorkoutDay, WorkoutDayExercise
from app.models.workout_goal import WorkoutGoal
from app.schemas.workout_plan import (
    WorkoutPlanCreate,
    WorkoutPlanResponse,
    WorkoutPlanDetailResponse,
    WorkoutPlanUpdate,
    WorkoutPlanListResponse,
    WeekCompletionRequest,
    WeekCompletionResponse,
    WorkoutWeekResponse
)
from app.schemas.auth import MessageResponse
from app.dependencies import get_current_user

router = APIRouter()


# ========== Mock AI Generation Functions ==========

def generate_mock_strategy(user: User, workout_goal: WorkoutGoal, total_weeks: int) -> dict:
    """Generate mock AI strategy for workout plan"""
    return {
        "focus": workout_goal.focus if workout_goal else "general_fitness",
        "goal": workout_goal.goal_label_en if workout_goal else "General Fitness",
        "approach": "Progressive overload with periodization",
        "phases": [
            {"week": "1-2", "phase": "Foundation", "focus": "Form and technique"},
            {"week": "3-6", "phase": "Building", "focus": "Strength and endurance"},
            {"week": "7-12", "phase": "Peak", "focus": "Maximum performance"}
        ][:total_weeks//4 + 1] if total_weeks > 1 else [{"week": "1", "phase": "Intro", "focus": "Full body workout"}],
        "training_days_per_week": user.fitness_days or 3,
        "session_duration": "45-60 minutes",
        "notes": "This is a mock strategy. Real AI will generate personalized strategy based on user profile."
    }


def generate_mock_expectations(total_weeks: int) -> dict:
    """Generate mock AI expectations for workout plan"""
    if total_weeks == 1:
        return {
            "strength_gain": "5-10%",
            "endurance_improvement": "Initial adaptation",
            "skill_development": "Learn proper form",
            "notes": "Mock expectations - AI will generate realistic expectations based on user fitness level"
        }
    elif total_weeks == 4:
        return {
            "strength_gain": "10-15%",
            "endurance_improvement": "Moderate improvement",
            "muscle_gain": "1-2 lbs",
            "skill_development": "Solid technique foundation",
            "notes": "Mock expectations - AI will generate realistic expectations based on user fitness level"
        }
    else:  # 12 weeks
        return {
            "strength_gain": "20-30%",
            "endurance_improvement": "Significant improvement",
            "muscle_gain": "4-8 lbs",
            "body_composition": "2-4% body fat reduction",
            "skill_development": "Advanced technique mastery",
            "notes": "Mock expectations - AI will generate realistic expectations based on user fitness level"
        }


def get_random_exercises(db: Session, count: int, user_location: str = None) -> List[int]:
    """Get random exercise IDs from database for mock generation"""
    # This is a simple mock - real AI will use semantic search and user preferences
    from sqlalchemy import text
    
    query = text("""
        SELECT e.exercise_id 
        FROM exercise e
        JOIN difficulty d ON e.difficulty_id = d.difficulty_id
        WHERE d.name_en IN ('Beginner', 'Intermediate')
        ORDER BY RANDOM()
        LIMIT :count
    """)
    
    result = db.execute(query, {"count": count})
    return [row[0] for row in result.fetchall()]


def generate_mock_workout_week(
    db: Session, 
    plan: WorkoutPlan, 
    week_number: int,
    user: User
) -> WorkoutWeek:
    """Generate a mock workout week with exercises"""
    
    week = WorkoutWeek(
        plan_id=plan.plan_id,
        week_number=week_number,
        title=f"Week {week_number}: Building Phase",
        description=f"Mock week {week_number} - Focus on compound movements and progressive overload"
    )
    db.add(week)
    db.flush()  # Get week_id
    
    # Generate workout days based on user's fitness_days
    training_days = user.fitness_days or 3
    day_names = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    
    for i in range(training_days):
        day = WorkoutDay(
            week_id=week.week_id,
            day_name=day_names[i],
            focus=["Upper Body", "Lower Body", "Full Body", "Push", "Pull", "Legs"][i % 6],
            warmup="5-10 minutes dynamic stretching and light cardio",
            cooldown="5-10 minutes static stretching and foam rolling"
        )
        db.add(day)
        db.flush()  # Get day_id
        
        # Add 4-6 exercises per day
        exercise_count = random.randint(4, 6)
        exercise_ids = get_random_exercises(db, exercise_count, user.training_location)
        
        for order, exercise_id in enumerate(exercise_ids, start=1):
            exercise = WorkoutDayExercise(
                day_id=day.day_id,
                exercise_id=exercise_id,
                sets=f"{random.randint(3, 4)}",
                reps=f"{random.randint(8, 12)}",
                tempo="2-0-2-0" if order <= 2 else "1-0-1-0",  # Slower tempo for compound movements
                rest=f"{random.randint(60, 90)} seconds",
                notes="Mock exercise - AI will generate optimal sets/reps/tempo based on user level",
                exercise_order=order
            )
            db.add(exercise)
    
    return week


# ========== API Endpoints ==========

@router.post("", response_model=WorkoutPlanDetailResponse, status_code=status.HTTP_201_CREATED)
async def create_workout_plan(
    plan_data: WorkoutPlanCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Create a new workout plan with AI-generated content.
    Currently uses mock AI generation - will be replaced with real AI agents.
    """
    
    # Validate total_weeks
    if plan_data.total_weeks not in [1, 4, 12]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="total_weeks must be 1, 4, or 12"
        )
    
    # Get workout goal if provided
    workout_goal = None
    if plan_data.workout_goal_id:
        workout_goal = db.query(WorkoutGoal).filter(
            WorkoutGoal.workout_goal_id == plan_data.workout_goal_id
        ).first()
        if not workout_goal:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Workout goal not found"
            )
    
    # Generate mock AI content
    strategy = generate_mock_strategy(current_user, workout_goal, plan_data.total_weeks)
    expectations = generate_mock_expectations(plan_data.total_weeks)
    
    # Create workout plan
    workout_plan = WorkoutPlan(
        user_id=current_user.user_id,
        workout_goal_id=plan_data.workout_goal_id,
        name=plan_data.name,
        total_weeks=plan_data.total_weeks,
        current_week=1,
        completed_weeks=[],
        strategy=strategy,
        expectations=expectations
    )
    db.add(workout_plan)
    db.flush()  # Get plan_id
    
    # Generate workout weeks with mock AI
    for week_num in range(1, plan_data.total_weeks + 1):
        generate_mock_workout_week(db, workout_plan, week_num, current_user)
    
    db.commit()
    
    # Reload with all relationships
    plan = db.query(WorkoutPlan).options(
        joinedload(WorkoutPlan.weeks).joinedload(WorkoutWeek.days).joinedload(WorkoutDay.exercises).joinedload(WorkoutDayExercise.exercise)
    ).filter(WorkoutPlan.plan_id == workout_plan.plan_id).first()
    
    return WorkoutPlanDetailResponse.model_validate(plan)


@router.get("", response_model=WorkoutPlanListResponse)
async def get_user_workout_plans(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get all workout plans for the current user
    """
    plans = db.query(WorkoutPlan).filter(
        WorkoutPlan.user_id == current_user.user_id
    ).order_by(WorkoutPlan.created_at.desc()).all()
    
    return WorkoutPlanListResponse(
        plans=[WorkoutPlanResponse.model_validate(p) for p in plans],
        total=len(plans)
    )


@router.get("/{plan_id}", response_model=WorkoutPlanDetailResponse)
async def get_workout_plan(
    plan_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get a specific workout plan with all details
    """
    plan = db.query(WorkoutPlan).options(
        joinedload(WorkoutPlan.weeks).joinedload(WorkoutWeek.days).joinedload(WorkoutDay.exercises).joinedload(WorkoutDayExercise.exercise)
    ).filter(
        WorkoutPlan.plan_id == plan_id,
        WorkoutPlan.user_id == current_user.user_id
    ).first()
    
    if not plan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workout plan not found"
        )
    
    return WorkoutPlanDetailResponse.model_validate(plan)


@router.get("/{plan_id}/week/{week_number}", response_model=WorkoutWeekResponse)
async def get_workout_week(
    plan_id: int,
    week_number: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get a specific week from a workout plan
    """
    # Verify plan ownership
    plan = db.query(WorkoutPlan).filter(
        WorkoutPlan.plan_id == plan_id,
        WorkoutPlan.user_id == current_user.user_id
    ).first()
    
    if not plan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workout plan not found"
        )
    
    # Get the week
    week = db.query(WorkoutWeek).options(
        joinedload(WorkoutWeek.days).joinedload(WorkoutDay.exercises).joinedload(WorkoutDayExercise.exercise)
    ).filter(
        WorkoutWeek.plan_id == plan_id,
        WorkoutWeek.week_number == week_number
    ).first()
    
    if not week:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Week not found"
        )
    
    return WorkoutWeekResponse.model_validate(week)


@router.put("/{plan_id}", response_model=WorkoutPlanResponse)
async def update_workout_plan(
    plan_id: int,
    plan_update: WorkoutPlanUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update a workout plan (name, current_week)
    """
    plan = db.query(WorkoutPlan).filter(
        WorkoutPlan.plan_id == plan_id,
        WorkoutPlan.user_id == current_user.user_id
    ).first()
    
    if not plan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workout plan not found"
        )
    
    # Update only provided fields
    update_data = plan_update.model_dump(exclude_unset=True)
    
    for field, value in update_data.items():
        setattr(plan, field, value)
    
    db.commit()
    db.refresh(plan)
    
    return WorkoutPlanResponse.model_validate(plan)


@router.post("/{plan_id}/complete-week", response_model=WeekCompletionResponse)
async def complete_workout_week(
    plan_id: int,
    completion: WeekCompletionRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Mark a week as completed and advance to the next week
    """
    plan = db.query(WorkoutPlan).filter(
        WorkoutPlan.plan_id == plan_id,
        WorkoutPlan.user_id == current_user.user_id
    ).first()
    
    if not plan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workout plan not found"
        )
    
    # Validate week number
    if completion.week_number < 1 or completion.week_number > plan.total_weeks:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid week number. Must be between 1 and {plan.total_weeks}"
        )
    
    # Add to completed weeks if not already completed
    if completion.week_number not in plan.completed_weeks:
        plan.completed_weeks = plan.completed_weeks + [completion.week_number]
    
    # Advance current_week if completing the current week
    if completion.week_number == plan.current_week and plan.current_week < plan.total_weeks:
        plan.current_week += 1
    
    db.commit()
    db.refresh(plan)
    
    return WeekCompletionResponse(
        plan_id=plan.plan_id,
        week_number=completion.week_number,
        current_week=plan.current_week,
        completed_weeks=plan.completed_weeks,
        message=f"Week {completion.week_number} marked as completed"
    )


@router.delete("/{plan_id}", response_model=MessageResponse)
async def delete_workout_plan(
    plan_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Delete a workout plan (cascades to all weeks, days, and exercises)
    """
    plan = db.query(WorkoutPlan).filter(
        WorkoutPlan.plan_id == plan_id,
        WorkoutPlan.user_id == current_user.user_id
    ).first()
    
    if not plan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workout plan not found"
        )
    
    db.delete(plan)
    db.commit()
    
    return MessageResponse(message="Workout plan deleted successfully")

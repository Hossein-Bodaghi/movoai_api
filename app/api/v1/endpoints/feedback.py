"""
Feedback endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from typing import Optional

from app.database.session import get_db
from app.models.user import User
from app.models.feedback import Feedback, FeedbackQuestion
from app.models.workout_plan import WorkoutWeek, WorkoutDay, WorkoutDayExercise
from app.models.nutrition_plan import NutritionWeek, NutritionDay, Meal
from app.models.exercise import Exercise
from app.schemas.feedback import (
    FeedbackCreate,
    FeedbackDetail,
    FeedbackSummary,
    FeedbackListResponse,
    FeedbackQuestionDetail,
    FeedbackQuestionListResponse
)
from app.schemas.auth import MessageResponse
from app.dependencies import get_current_user

router = APIRouter()


@router.post("", response_model=FeedbackDetail, status_code=status.HTTP_201_CREATED)
async def submit_feedback(
    feedback_data: FeedbackCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Submit feedback for a workout or nutrition week
    
    - **week_table**: Either 'workout_weeks' or 'nutrition_weeks'
    - **week_id**: ID of the specific week
    - **responses**: Array of question responses with question_id, answer, and optional text_response
    """
    # Verify the week exists and belongs to user
    if feedback_data.week_table == 'workout_weeks':
        week = db.query(WorkoutWeek).join(
            WorkoutWeek.workout_plan
        ).filter(
            WorkoutWeek.week_id == feedback_data.week_id,
            WorkoutWeek.workout_plan.has(user_id=current_user.user_id)
        ).first()
        
        if not week:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Workout week not found or does not belong to you"
            )
    
    elif feedback_data.week_table == 'nutrition_weeks':
        week = db.query(NutritionWeek).join(
            NutritionWeek.nutrition_plan
        ).filter(
            NutritionWeek.week_id == feedback_data.week_id,
            NutritionWeek.nutrition_plan.has(user_id=current_user.user_id)
        ).first()
        
        if not week:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Nutrition week not found or does not belong to you"
            )
    
    # Check if feedback already exists for this week
    existing_feedback = db.query(Feedback).filter(
        Feedback.user_id == current_user.user_id,
        Feedback.week_table == feedback_data.week_table,
        Feedback.week_id == feedback_data.week_id
    ).first()
    
    if existing_feedback:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Feedback already submitted for this week"
        )
    
    # Create feedback
    new_feedback = Feedback(
        user_id=current_user.user_id,
        week_table=feedback_data.week_table,
        week_id=feedback_data.week_id,
        responses=feedback_data.responses
    )
    
    db.add(new_feedback)
    db.commit()
    db.refresh(new_feedback)
    
    return FeedbackDetail.model_validate(new_feedback)


@router.get("", response_model=FeedbackListResponse)
async def list_feedback(
    week_table: Optional[str] = Query(None, description="Filter by week_table: workout_weeks or nutrition_weeks"),
    week_id: Optional[int] = Query(None, description="Filter by specific week_id"),
    limit: int = Query(50, ge=1, le=100, description="Number of results to return"),
    offset: int = Query(0, ge=0, description="Number of results to skip"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    List all feedback submissions by current user
    
    Optional filters:
    - **week_table**: Filter by workout_weeks or nutrition_weeks
    - **week_id**: Filter by specific week
    """
    query = db.query(Feedback).filter(Feedback.user_id == current_user.user_id)
    
    if week_table:
        if week_table not in ['workout_weeks', 'nutrition_weeks']:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="week_table must be 'workout_weeks' or 'nutrition_weeks'"
            )
        query = query.filter(Feedback.week_table == week_table)
    
    if week_id:
        query = query.filter(Feedback.week_id == week_id)
    
    # Get total count
    total = query.count()
    
    # Get paginated results
    feedback_list = query.order_by(desc(Feedback.submitted_at)).offset(offset).limit(limit).all()
    
    # Convert to summary format
    summaries = [
        FeedbackSummary(
            feedback_id=f.feedback_id,
            user_id=f.user_id,
            week_table=f.week_table,
            week_id=f.week_id,
            submitted_at=f.submitted_at,
            questions_answered=len(f.responses) if isinstance(f.responses, list) else 0
        )
        for f in feedback_list
    ]
    
    return FeedbackListResponse(feedback=summaries, total=total)


@router.get("/{feedback_id}", response_model=FeedbackDetail)
async def get_feedback(
    feedback_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get detailed feedback by ID
    
    Returns full feedback including all question responses
    """
    feedback = db.query(Feedback).filter(
        Feedback.feedback_id == feedback_id,
        Feedback.user_id == current_user.user_id
    ).first()
    
    if not feedback:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Feedback not found"
        )
    
    return FeedbackDetail.model_validate(feedback)


@router.put("/{feedback_id}", response_model=FeedbackDetail)
async def update_feedback(
    feedback_id: int,
    feedback_data: FeedbackCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update existing feedback
    
    Allows user to modify their feedback responses before final submission
    """
    feedback = db.query(Feedback).filter(
        Feedback.feedback_id == feedback_id,
        Feedback.user_id == current_user.user_id
    ).first()
    
    if not feedback:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Feedback not found"
        )
    
    # Update responses
    feedback.responses = feedback_data.responses
    
    db.commit()
    db.refresh(feedback)
    
    return FeedbackDetail.model_validate(feedback)


@router.delete("/{feedback_id}", response_model=MessageResponse)
async def delete_feedback(
    feedback_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Delete feedback submission
    """
    feedback = db.query(Feedback).filter(
        Feedback.feedback_id == feedback_id,
        Feedback.user_id == current_user.user_id
    ).first()
    
    if not feedback:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Feedback not found"
        )
    
    db.delete(feedback)
    db.commit()
    
    return MessageResponse(message="Feedback deleted successfully")


# ========== Feedback Questions Endpoints ==========

@router.get("/questions", response_model=FeedbackQuestionListResponse)
async def list_feedback_questions(
    week_table: str = Query(..., description="Filter by week_table: workout_weeks or nutrition_weeks"),
    week_number: int = Query(..., description="Filter by specific week_number (1-12)"),
    focus: str = Query(..., description="User's fitness focus"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    List feedback questions for a specific week
    
    Required params:
    - **week_table**: 'workout_weeks' or 'nutrition_weeks'
    - **week_number**: Week number (1-12)
    - **focus**: User's fitness focus (performance_enhancement, body_recomposition, efficiency, rebuilding_rehab)
    """
    # Validate week_table
    if week_table not in ['workout_weeks', 'nutrition_weeks']:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="week_table must be 'workout_weeks' or 'nutrition_weeks'"
        )
    
    # Validate week_number range
    if week_number < 1 or week_number > 12:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="week_number must be between 1 and 12"
        )
    
    # Validate focus
    valid_focus_values = ['performance_enhancement', 'body_recomposition', 'efficiency', 'rebuilding_rehab']
    if focus not in valid_focus_values:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"focus must be one of: {', '.join(valid_focus_values)}"
        )
    
    # Build query for questions
    query = db.query(FeedbackQuestion).filter(
        FeedbackQuestion.week_table == week_table,
        FeedbackQuestion.week_number == week_number,
        FeedbackQuestion.focus == focus
    )
    
    # Get questions ordered by question_order
    questions = query.order_by(FeedbackQuestion.question_order).all()
    
    return FeedbackQuestionListResponse(
        questions=[FeedbackQuestionDetail.model_validate(q) for q in questions],
        total=len(questions)
    )


@router.get("/questions/{question_id}", response_model=FeedbackQuestionDetail)
async def get_feedback_question(
    question_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get specific feedback question by ID
    """
    question = db.query(FeedbackQuestion).filter(
        FeedbackQuestion.question_id == question_id
    ).first()
    
    if not question:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Question not found"
        )
    
    return FeedbackQuestionDetail.model_validate(question)


@router.get("/questions/week/{week_table}/{week_number}/options", response_model=dict)
async def get_dynamic_options(
    week_table: str,
    week_number: int,
    option_type: str = Query(..., description="Type of options: 'exercises' or 'meals'"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get dynamic options (exercises or meals) for a specific week number
    
    Used when question has dynamic_options field set to 'exercises' or 'meals'
    """
    # Validate inputs
    if week_table not in ['workout_weeks', 'nutrition_weeks']:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="week_table must be 'workout_weeks' or 'nutrition_weeks'"
        )
    
    if option_type not in ['exercises', 'meals']:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="option_type must be 'exercises' or 'meals'"
        )
    
    # Validate week_number range
    if week_number < 1 or week_number > 12:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="week_number must be between 1 and 12"
        )
    
    options = []
    
    if week_table == 'workout_weeks' and option_type == 'exercises':
        # Get all exercises for this workout week
        week = db.query(WorkoutWeek).join(
            WorkoutWeek.workout_plan
        ).filter(
            WorkoutWeek.week_number == week_number,
            WorkoutWeek.workout_plan.has(user_id=current_user.user_id)
        ).first()
        
        if not week:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Workout week not found"
            )
        
        # Get unique exercises from all days in this week
        exercise_ids = set()
        for day in week.days:
            for workout_exercise in day.exercises:
                exercise_ids.add(workout_exercise.exercise_id)
        
        # Fetch exercise details
        exercises = db.query(Exercise).filter(Exercise.exercise_id.in_(exercise_ids)).all()
        
        options = [
            {"label": ex.name_fa or ex.name_en, "value": str(ex.exercise_id)}
            for ex in exercises
        ]
    
    elif week_table == 'nutrition_weeks' and option_type == 'meals':
        # Get all meals for this nutrition week
        week = db.query(NutritionWeek).join(
            NutritionWeek.nutrition_plan
        ).filter(
            NutritionWeek.week_number == week_number,
            NutritionWeek.nutrition_plan.has(user_id=current_user.user_id)
        ).first()
        
        if not week:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Nutrition week not found"
            )
        
        # Get unique meals from all days in this week
        meal_names = set()
        for day in week.days:
            for meal in day.meals:
                meal_names.add(meal.name)
        
        options = [
            {"label": name, "value": name}
            for name in sorted(meal_names)
        ]
    
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid combination: {week_table} with {option_type}"
        )
    
    return {"options": options, "total": len(options)}

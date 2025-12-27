"""
Workout Plan endpoints (Phase 2)
Uses AvalAI API to generate personalized workout plans in Farsi
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload
from typing import List
import random

from app.database.session import get_db
from ai.workout_generator_farsi import generate_farsi_workout_plan
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

def generate_mock_strategy(user: User, workout_goal: WorkoutGoal, total_weeks: int) -> str:
    """Generate mock AI strategy for workout plan"""
    return "این برنامه تمرینی بر اساس اطلاعات پروفایل شما طراحی شده است. رویکرد این برنامه ترکیبی از تمرینات قدرتی و هوازی است که به صورت پیشرونده شدت پیدا می‌کند. در هفته‌های اول، تمرکز بر ساختن پایه و تکنیک صحیح است. از هفته پنجم به بعد، حجم و شدت تمرینات افزایش می‌یابد. برنامه شامل روزهای ریکاوری فعال برای جلوگیری از اورترینینگ می‌باشد."


def generate_mock_expectations(total_weeks: int) -> str:
    """Generate mock AI expectations for workout plan"""
    return "در پایان این برنامه، انتظار می‌رود که افزایش ۵-۸ کیلوگرم عضله خالص داشته باشید. همچنین قدرت شما در حرکات اصلی مانند اسکوات، بنچ پرس و ددلیفت به طور قابل توجهی افزایش خواهد یافت. در ۴ هفته اول تغییرات ظاهری محسوس نخواهد بود، اما از هفته ۵ به بعد تفاوت‌ها مشهود می‌شوند."


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
    """Generate a mock workout week with exercises using Persian data"""
    
    # Persian week data
    workout_week_data = [
        {"week": 1, "title": "ساختن پایه و آشنایی با تمرینات", "description": "در هفته اول، تمرکز ما بر روی یادگیری فرم صحیح حرکات و آماده‌سازی بدن برای تمرینات سنگین‌تر است. **تمرکز تمرین:** حرکات پایه‌ای با وزن متوسط برای ایجاد پایه عضلانی قوی. **تمرکز تغذیه:** تنظیم کالری و ماکروها بر اساس هدف شما."},
        {"week": 2, "title": "افزایش حجم و شدت تمرینات", "description": "در هفته دوم، حجم تمرینات را افزایش می‌دهیم تا عضلات بیشتر تحریک شوند. **تمرکز تمرین:** افزایش تعداد ست‌ها و کاهش زمان استراحت بین ست‌ها. **تمرکز تغذیه:** افزایش پروتئین برای بهبود عضلات."},
        {"week": 3, "title": "افزایش شدت و مقاومت در برابر استرس", "description": "در فاز نهایی، ما شدت را به سیستم اضافه می‌کنیم تا بدن شما را به یک ماشین چربی‌سوز کارآمد تبدیل کنیم. **تمرکز تمرین:** معرفی پروتکل‌های متابولیک شدیدتر. **تمرکز تغذیه:** بهینه‌سازی خواب و مدیریت استرس."},
        {"week": 4, "title": "ریکاوری فعال و بازسازی عضلانی", "description": "هفته چهارم زمان استراحت فعال است. **تمرکز تمرین:** کاهش شدت و تمرکز بر حرکات کششی و موبیلیتی. **تمرکز تغذیه:** تامین ریز مغذی‌ها و هیدراتاسیون."},
        {"week": 5, "title": "معرفی برنامه تفکیکی پیشرفته", "description": "با ورود به هفته پنجم، برنامه تفکیکی را شروع می‌کنیم. **تمرکز تمرین:** تمرینات جداگانه برای هر گروه عضلانی. **تمرکز تغذیه:** تایمینگ وعده‌ها بر اساس زمان تمرین."},
        {"week": 6, "title": "افزایش حجم و تحریک عمیق عضلانی", "description": "هفته ششم با افزایش حجم تمرینات همراه است. **تمرکز تمرین:** افزایش تعداد ست‌ها و تکرارها. **تمرکز تغذیه:** افزایش کالری برای رشد عضلانی."},
        {"week": 7, "title": "ادغام تمرینات هوازی و قدرتی", "description": "ترکیب تمرینات هوازی و مقاومتی. **تمرکز تمرین:** سرکیت ترینینگ. **تمرکز تغذیه:** مدیریت کربوهیدرات‌ها."},
        {"week": 8, "title": "تمرکز بر قدرت و حداکثر توان", "description": "هفته هشتم بر افزایش قدرت متمرکز است. **تمرکز تمرین:** کاهش تکرارها و افزایش وزنه. **تمرکز تغذیه:** افزایش کراتین."},
        {"week": 9, "title": "مرحله استقامت و ظرفیت کاری", "description": "تمرکز بر بهبود استقامت عضلانی. **تمرکز تمرین:** افزایش تکرارها. **تمرکز تغذیه:** هیدراتاسیون."},
        {"week": 10, "title": "آمادگی برای هفته اوج", "description": "آماده‌سازی برای بهترین عملکرد. **تمرکز تمرین:** تمرینات با شدت متوسط. **تمرکز تغذیه:** بهینه‌سازی گلیکوژن."},
        {"week": 11, "title": "هفته اوج و حداکثر عملکرد", "description": "رسیدن به اوج آمادگی جسمانی. **تمرکز تمرین:** شدت بالا و حجم متوسط. **تمرکز تغذیه:** رژیم متعادل."},
        {"week": 12, "title": "تثبیت نتایج و برنامه‌ریزی آینده", "description": "هفته نهایی برای تثبیت دستاوردها. **تمرکز تمرین:** حفظ سطح فعلی. **تمرکز تغذیه:** ایجاد عادات پایدار."}
    ]
    
    week_data = workout_week_data[week_number - 1] if week_number <= len(workout_week_data) else workout_week_data[0]
    
    week = WorkoutWeek(
        plan_id=plan.plan_id,
        week_number=week_number,
        title=week_data["title"],
        description=week_data["description"]
    )
    db.add(week)
    db.flush()  # Get week_id
    
    # Generate workout days based on user's fitness_days
    training_days = user.fitness_days or 3
    day_names = ["شنبه", "یکشنبه", "دوشنبه", "سه‌شنبه", "چهارشنبه", "پنج‌شنبه", "جمعه"]
    
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
    Create a new workout plan with AI-generated content using AvalAI API.
    Generates personalized workout plans in Farsi based on user profile.
    """
    
    # Validate total_weeks (currently only supporting 1 week plans)
    if plan_data.total_weeks != 1:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Currently only 1-week plans are supported"
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
    
    # Get user's equipment IDs
    equipment_ids = []
    if current_user.training_location == 'home':
        equipment_ids = current_user.home_equipment or [1]  # 1 = Bodyweight
    elif current_user.training_location == 'gym':
        equipment_ids = current_user.gym_equipment or [1, 2, 3]  # Common gym equipment
    else:
        equipment_ids = [1]  # Bodyweight only for outdoor
    
    # Prepare user profile for AI generator
    user_profile = {
        'user_id': current_user.user_id,
        'age': current_user.age,
        'weight': float(current_user.weight) if current_user.weight else 70,
        'height': float(current_user.height) if current_user.height else 170,
        'gender': current_user.gender or 'male',
        'workout_goal_id': plan_data.workout_goal_id,
        'physical_fitness': current_user.physical_fitness or 'beginner',
        'fitness_days': current_user.fitness_days or 3,
        'workout_limitations': current_user.workout_limitations or 'بدون محدودیت',
        'specialized_sport': current_user.specialized_sport or 'ندارد',
        'training_location': current_user.training_location or 'home',
        'equipment_ids': equipment_ids
    }
    
    # Generate AI workout plan
    try:
        ai_plan = generate_farsi_workout_plan(db, user_profile)
    except Exception as e:
        print(f"Error generating AI plan: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate workout plan: {str(e)}"
        )
    
    # Create workout plan
    workout_plan = WorkoutPlan(
        user_id=current_user.user_id,
        workout_goal_id=plan_data.workout_goal_id,
        name=plan_data.name,
        total_weeks=plan_data.total_weeks,
        current_week=1,
        completed_weeks=[],
        strategy=ai_plan.get('strategy', ''),
        expectations=ai_plan.get('expectations', '')
    )
    db.add(workout_plan)
    db.flush()  # Get plan_id
    
    # Create workout week
    week = WorkoutWeek(
        plan_id=workout_plan.plan_id,
        week_number=1,
        title="هفته اول",
        description="برنامه تمرینی هفته اول"
    )
    db.add(week)
    db.flush()
    
    # Create workout days from AI plan
    for day_data in ai_plan.get('days', []):
        day = WorkoutDay(
            week_id=week.week_id,
            day_name=day_data.get('day_name', 'شنبه'),
            focus=day_data.get('focus', ''),
            warmup=day_data.get('warmup', '5-10 دقیقه کشش پویا'),
            cooldown=day_data.get('cooldown', '5-10 دقیقه کشش ایستا')
        )
        db.add(day)
        db.flush()
        
        # Add exercises for this day
        for exercise_data in day_data.get('exercises', []):
            exercise_id = exercise_data.get('exercise_id')
            
            # Validate exercise_id is present and not None
            if not exercise_id:
                print(f"⚠️ Warning: Skipping exercise without exercise_id in day {day_data.get('day_name')}")
                continue
            
            exercise = WorkoutDayExercise(
                day_id=day.day_id,
                exercise_id=exercise_id,
                sets=exercise_data.get('sets', '3'),
                reps=exercise_data.get('reps', '10-12'),
                rest=exercise_data.get('rest', '60 ثانیه'),
                exercise_order=exercise_data.get('exercise_order', 1)
            )
            db.add(exercise)
    
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

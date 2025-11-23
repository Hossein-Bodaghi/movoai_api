"""
Nutrition Plan endpoints (Phase 3)
Includes mock AI generation for nutrition plans until AI agents are implemented
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload
from typing import List
import random

from app.database.session import get_db
from app.models.user import User
from app.models.nutrition_plan import NutritionPlan, NutritionWeek, NutritionDay, Meal
from app.models.nutrition_goal import NutritionGoal
from app.schemas.nutrition_plan import (
    NutritionPlanCreate,
    NutritionPlanResponse,
    NutritionPlanDetailResponse,
    NutritionPlanUpdate,
    NutritionPlanListResponse,
    NutritionWeekCompletionRequest,
    NutritionWeekCompletionResponse,
    NutritionWeekResponse
)
from app.schemas.auth import MessageResponse
from app.dependencies import get_current_user

router = APIRouter()


# ========== Mock AI Generation Functions ==========

def generate_mock_nutrition_strategy(user: User, nutrition_goal: NutritionGoal, total_weeks: int) -> dict:
    """Generate mock AI strategy for nutrition plan"""
    return {
        "focus": nutrition_goal.focus if nutrition_goal else "balanced_nutrition",
        "goal": nutrition_goal.goal_label_en if nutrition_goal else "Balanced Nutrition",
        "approach": "Flexible dieting with macro tracking",
        "calorie_target": 2000 + (user.weight or 70) * 10 - (user.age or 30) * 5,
        "macro_split": {
            "protein": "30%",
            "carbs": "40%",
            "fats": "30%"
        },
        "meal_frequency": "3 main meals + 1 snack",
        "hydration": "8-10 glasses of water daily",
        "notes": "This is a mock strategy. Real AI will generate personalized nutrition strategy based on user profile."
    }


def generate_mock_nutrition_expectations(total_weeks: int) -> dict:
    """Generate mock AI expectations for nutrition plan"""
    if total_weeks == 1:
        return {
            "weight_change": "Minimal (adaptation phase)",
            "energy_levels": "Initial improvements",
            "habit_formation": "Introduction to meal structure",
            "notes": "Mock expectations - AI will generate realistic expectations based on user goals"
        }
    elif total_weeks == 4:
        return {
            "weight_change": "2-4 lbs (depending on goal)",
            "energy_levels": "Significant improvement",
            "habit_formation": "Solid meal prep routine",
            "body_composition": "Initial changes visible",
            "notes": "Mock expectations - AI will generate realistic expectations based on user goals"
        }
    else:  # 12 weeks
        return {
            "weight_change": "8-16 lbs (depending on goal)",
            "energy_levels": "Optimal and consistent",
            "habit_formation": "Sustainable lifestyle changes",
            "body_composition": "Significant transformation",
            "metabolic_adaptation": "Improved insulin sensitivity",
            "notes": "Mock expectations - AI will generate realistic expectations based on user goals"
        }


def generate_mock_meals(meal_type: str, day_number: int, base_calories: int) -> dict:
    """Generate mock meal data"""
    meals_database = {
        "breakfast": [
            {"name": "Greek Yogurt Parfait", "desc": "Greek yogurt with berries, granola, and honey"},
            {"name": "Protein Pancakes", "desc": "Whole grain pancakes with protein powder, topped with fruits"},
            {"name": "Avocado Toast", "desc": "Whole grain toast with avocado, eggs, and tomatoes"},
            {"name": "Oatmeal Bowl", "desc": "Steel-cut oats with banana, nuts, and cinnamon"},
            {"name": "Scrambled Eggs", "desc": "Eggs with vegetables, whole grain toast, and avocado"}
        ],
        "lunch": [
            {"name": "Grilled Chicken Salad", "desc": "Mixed greens with grilled chicken, quinoa, and vinaigrette"},
            {"name": "Turkey Wrap", "desc": "Whole wheat wrap with turkey, vegetables, and hummus"},
            {"name": "Salmon Bowl", "desc": "Grilled salmon with brown rice and roasted vegetables"},
            {"name": "Chicken Stir-Fry", "desc": "Lean chicken with mixed vegetables and brown rice"},
            {"name": "Mediterranean Bowl", "desc": "Chickpeas, quinoa, feta, vegetables with tahini dressing"}
        ],
        "dinner": [
            {"name": "Grilled Steak", "desc": "Lean steak with sweet potato and steamed broccoli"},
            {"name": "Baked Salmon", "desc": "Herb-crusted salmon with asparagus and quinoa"},
            {"name": "Chicken Breast", "desc": "Grilled chicken with roasted vegetables and brown rice"},
            {"name": "Turkey Meatballs", "desc": "Lean turkey meatballs with marinara and zucchini noodles"},
            {"name": "Shrimp Bowl", "desc": "Garlic shrimp with cauliflower rice and mixed vegetables"}
        ],
        "snacks": [
            {"name": "Protein Shake", "desc": "Whey protein with almond milk and banana"},
            {"name": "Mixed Nuts", "desc": "Almonds, walnuts, and cashews (1 oz)"},
            {"name": "Apple with Nut Butter", "desc": "Sliced apple with natural almond butter"},
            {"name": "Greek Yogurt", "desc": "Plain Greek yogurt with berries"},
            {"name": "Protein Bar", "desc": "High-protein, low-sugar nutrition bar"}
        ]
    }
    
    meal = random.choice(meals_database[meal_type])
    
    # Calculate calories and macros based on meal type
    calorie_split = {"breakfast": 0.25, "lunch": 0.35, "dinner": 0.30, "snacks": 0.10}
    calories = int(base_calories * calorie_split[meal_type])
    
    # Rough macro calculation (protein: 4 cal/g, carbs: 4 cal/g, fats: 9 cal/g)
    protein = round(calories * 0.30 / 4, 1)
    carbs = round(calories * 0.40 / 4, 1)
    fats = round(calories * 0.30 / 9, 1)
    
    return {
        "name": meal["name"],
        "description": meal["desc"] + " (Mock meal - AI will generate based on user preferences)",
        "calories": calories,
        "protein": protein,
        "carbs": carbs,
        "fats": fats
    }


def generate_mock_nutrition_week(
    db: Session, 
    plan: NutritionPlan, 
    week_number: int,
    user: User
) -> NutritionWeek:
    """Generate a mock nutrition week with meals"""
    
    week = NutritionWeek(
        plan_id=plan.plan_id,
        week_number=week_number,
        title=f"Week {week_number}: Balanced Nutrition",
        description=f"Mock week {week_number} - Focus on whole foods and macro balance"
    )
    db.add(week)
    db.flush()  # Get week_id
    
    # Calculate daily calorie target
    base_calories = 2000 + int((user.weight or 70) * 10) - int((user.age or 30) * 5)
    
    # Generate 7 days
    day_names = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    
    for day_name in day_names:
        day = NutritionDay(
            week_id=week.week_id,
            day_name=day_name,
            daily_calories=base_calories
        )
        db.add(day)
        db.flush()  # Get day_id
        
        # Add 4 meals per day (breakfast, lunch, dinner, snacks)
        for meal_type in ["breakfast", "lunch", "dinner", "snacks"]:
            meal_data = generate_mock_meals(
                meal_type, 
                day_names.index(day_name) + 1,
                base_calories
            )
            
            meal = Meal(
                day_id=day.day_id,
                meal_type=meal_type,
                name=meal_data["name"],
                description=meal_data["description"],
                calories=meal_data["calories"],
                protein=meal_data["protein"],
                carbs=meal_data["carbs"],
                fats=meal_data["fats"]
            )
            db.add(meal)
    
    return week


# ========== API Endpoints ==========

@router.post("", response_model=NutritionPlanDetailResponse, status_code=status.HTTP_201_CREATED)
async def create_nutrition_plan(
    plan_data: NutritionPlanCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Create a new nutrition plan with AI-generated content.
    Currently uses mock AI generation - will be replaced with real AI agents.
    """
    
    # Validate total_weeks
    if plan_data.total_weeks not in [1, 4, 12]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="total_weeks must be 1, 4, or 12"
        )
    
    # Get nutrition goal if provided
    nutrition_goal = None
    if plan_data.nutrition_goal_id:
        nutrition_goal = db.query(NutritionGoal).filter(
            NutritionGoal.nutrition_goal_id == plan_data.nutrition_goal_id
        ).first()
        if not nutrition_goal:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Nutrition goal not found"
            )
    
    # Generate mock AI content
    strategy = generate_mock_nutrition_strategy(current_user, nutrition_goal, plan_data.total_weeks)
    expectations = generate_mock_nutrition_expectations(plan_data.total_weeks)
    
    # Create nutrition plan
    nutrition_plan = NutritionPlan(
        user_id=current_user.user_id,
        nutrition_goal_id=plan_data.nutrition_goal_id,
        name=plan_data.name,
        total_weeks=plan_data.total_weeks,
        current_week=1,
        completed_weeks=[],
        strategy=strategy,
        expectations=expectations
    )
    db.add(nutrition_plan)
    db.flush()  # Get plan_id
    
    # Generate nutrition weeks with mock AI
    for week_num in range(1, plan_data.total_weeks + 1):
        generate_mock_nutrition_week(db, nutrition_plan, week_num, current_user)
    
    db.commit()
    
    # Reload with all relationships
    plan = db.query(NutritionPlan).options(
        joinedload(NutritionPlan.weeks).joinedload(NutritionWeek.days).joinedload(NutritionDay.meals)
    ).filter(NutritionPlan.plan_id == nutrition_plan.plan_id).first()
    
    return NutritionPlanDetailResponse.model_validate(plan)


@router.get("", response_model=NutritionPlanListResponse)
async def get_user_nutrition_plans(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get all nutrition plans for the current user
    """
    plans = db.query(NutritionPlan).filter(
        NutritionPlan.user_id == current_user.user_id
    ).order_by(NutritionPlan.created_at.desc()).all()
    
    return NutritionPlanListResponse(
        plans=[NutritionPlanResponse.model_validate(p) for p in plans],
        total=len(plans)
    )


@router.get("/{plan_id}", response_model=NutritionPlanDetailResponse)
async def get_nutrition_plan(
    plan_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get a specific nutrition plan with all details
    """
    plan = db.query(NutritionPlan).options(
        joinedload(NutritionPlan.weeks).joinedload(NutritionWeek.days).joinedload(NutritionDay.meals)
    ).filter(
        NutritionPlan.plan_id == plan_id,
        NutritionPlan.user_id == current_user.user_id
    ).first()
    
    if not plan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Nutrition plan not found"
        )
    
    return NutritionPlanDetailResponse.model_validate(plan)


@router.get("/{plan_id}/week/{week_number}", response_model=NutritionWeekResponse)
async def get_nutrition_week(
    plan_id: int,
    week_number: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get a specific week from a nutrition plan
    """
    # Verify plan ownership
    plan = db.query(NutritionPlan).filter(
        NutritionPlan.plan_id == plan_id,
        NutritionPlan.user_id == current_user.user_id
    ).first()
    
    if not plan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Nutrition plan not found"
        )
    
    # Get the week
    week = db.query(NutritionWeek).options(
        joinedload(NutritionWeek.days).joinedload(NutritionDay.meals)
    ).filter(
        NutritionWeek.plan_id == plan_id,
        NutritionWeek.week_number == week_number
    ).first()
    
    if not week:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Week not found"
        )
    
    return NutritionWeekResponse.model_validate(week)


@router.put("/{plan_id}", response_model=NutritionPlanResponse)
async def update_nutrition_plan(
    plan_id: int,
    plan_update: NutritionPlanUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update a nutrition plan (name, current_week)
    """
    plan = db.query(NutritionPlan).filter(
        NutritionPlan.plan_id == plan_id,
        NutritionPlan.user_id == current_user.user_id
    ).first()
    
    if not plan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Nutrition plan not found"
        )
    
    # Update only provided fields
    update_data = plan_update.model_dump(exclude_unset=True)
    
    for field, value in update_data.items():
        setattr(plan, field, value)
    
    db.commit()
    db.refresh(plan)
    
    return NutritionPlanResponse.model_validate(plan)


@router.post("/{plan_id}/complete-week", response_model=NutritionWeekCompletionResponse)
async def complete_nutrition_week(
    plan_id: int,
    completion: NutritionWeekCompletionRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Mark a week as completed and advance to the next week
    """
    plan = db.query(NutritionPlan).filter(
        NutritionPlan.plan_id == plan_id,
        NutritionPlan.user_id == current_user.user_id
    ).first()
    
    if not plan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Nutrition plan not found"
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
    
    return NutritionWeekCompletionResponse(
        plan_id=plan.plan_id,
        week_number=completion.week_number,
        current_week=plan.current_week,
        completed_weeks=plan.completed_weeks,
        message=f"Week {completion.week_number} marked as completed"
    )


@router.delete("/{plan_id}", response_model=MessageResponse)
async def delete_nutrition_plan(
    plan_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Delete a nutrition plan (cascades to all weeks, days, and meals)
    """
    plan = db.query(NutritionPlan).filter(
        NutritionPlan.plan_id == plan_id,
        NutritionPlan.user_id == current_user.user_id
    ).first()
    
    if not plan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Nutrition plan not found"
        )
    
    db.delete(plan)
    db.commit()
    
    return MessageResponse(message="Nutrition plan deleted successfully")

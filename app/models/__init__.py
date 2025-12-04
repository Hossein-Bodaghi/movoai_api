"""
Import all models here for Alembic to detect them
"""
from app.models.user import User
from app.models.auth_method import UserAuthMethod
from app.models.verification_code import VerificationCode
from app.models.workout_goal import WorkoutGoal
from app.models.nutrition_goal import NutritionGoal
from app.models.exercise import Exercise
from app.models.workout_plan import WorkoutPlan, WorkoutWeek, WorkoutDay, WorkoutDayExercise
from app.models.nutrition_plan import NutritionPlan, NutritionWeek, NutritionDay, Meal
from app.models.user_equipment import UserHomeEquipment, UserGymEquipment

__all__ = [
    "User",
    "UserAuthMethod",
    "VerificationCode",
    "WorkoutGoal",
    "NutritionGoal",
    "Exercise",
    "WorkoutPlan",
    "WorkoutWeek",
    "WorkoutDay",
    "WorkoutDayExercise",
    "NutritionPlan",
    "NutritionWeek",
    "NutritionDay",
    "Meal",
    "UserHomeEquipment",
    "UserGymEquipment",
]

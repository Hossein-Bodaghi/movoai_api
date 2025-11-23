"""
Import all models here for Alembic to detect them
"""
from app.models.user import User
from app.models.auth_method import UserAuthMethod
from app.models.verification_code import VerificationCode
from app.models.workout_goal import WorkoutGoal
from app.models.nutrition_goal import NutritionGoal

__all__ = [
    "User",
    "UserAuthMethod",
    "VerificationCode",
    "WorkoutGoal",
    "NutritionGoal",
]

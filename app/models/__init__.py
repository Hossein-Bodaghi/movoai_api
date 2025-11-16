"""
Import all models here for Alembic to detect them
"""
from app.models.user import User
from app.models.auth_method import UserAuthMethod
from app.models.verification_code import VerificationCode
from app.models.workout import (
    WorkoutPlan,
    Exercise,
    PlanExercise,
    UserPlan,
    UserWorkoutLog
)

__all__ = [
    "User",
    "UserAuthMethod",
    "VerificationCode",
    "WorkoutPlan",
    "Exercise",
    "PlanExercise",
    "UserPlan",
    "UserWorkoutLog",
]

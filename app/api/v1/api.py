"""
API v1 Router
"""
from fastapi import APIRouter

from app.api.v1.endpoints import auth, users, goals, workout_plans, nutrition_plans

api_router = APIRouter()

# Include all endpoint routers
api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(users.router, prefix="/users", tags=["Users"])
api_router.include_router(goals.router, prefix="/goals", tags=["Goals"])
api_router.include_router(workout_plans.router, prefix="/workout-plans", tags=["Workout Plans"])
api_router.include_router(nutrition_plans.router, prefix="/nutrition-plans", tags=["Nutrition Plans"])

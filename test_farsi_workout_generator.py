"""
Test script for Farsi Workout Generator with AvalAI API
Tests the integration with user profile and database
"""
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from sqlalchemy.orm import Session
from app.database.session import SessionLocal
from ai.workout_generator_farsi import generate_farsi_workout_plan
import json


def test_workout_generator():
    """Test the Farsi workout plan generator"""
    
    # Create a test user profile
    test_profile = {
        "user_id": "test_farsi_001",
        "age": 28,
        "weight": 75,
        "height": 175,
        "gender": "male",
        "workout_goal_id": 1,  # Assuming 1 exists in workout_goals table
        "physical_fitness": "intermediate",
        "fitness_days": 4,
        "workout_limitations": "بدون محدودیت",
        "specialized_sport": "ندارد",
        "training_location": "gym",
        "equipment_ids": [1, 2, 3, 4, 5, 6]  # Bodyweight, Dumbbells, Barbell, Kettlebell, Cables, Machine
    }
    
    print("=" * 80)
    print("🏋️  MOVOKIO FARSI WORKOUT PLAN GENERATOR TEST")
    print("=" * 80)
    print(f"\n📋 اطلاعات کاربر:")
    print(f"   شناسه: {test_profile['user_id']}")
    print(f"   سن: {test_profile['age']} سال")
    print(f"   وزن: {test_profile['weight']} کیلوگرم")
    print(f"   قد: {test_profile['height']} سانتی‌متر")
    print(f"   سطح آمادگی: {test_profile['physical_fitness']}")
    print(f"   روزهای تمرین: {test_profile['fitness_days']}")
    print(f"   محل تمرین: {test_profile['training_location']}")
    print("\n" + "-" * 80 + "\n")
    
    # Create database session
    db = SessionLocal()
    
    try:
        # Generate workout plan
        result = generate_farsi_workout_plan(db, test_profile)
        
        # Save to file
        output_file = "test_farsi_workout_plan_output.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        
        print("\n" + "=" * 80)
        print("📊 خلاصه برنامه")
        print("=" * 80)
        
        print("\n🎯 استراتژی:")
        print(result.get('strategy', 'N/A'))
        
        print("\n📈 انتظارات:")
        print(result.get('expectations', 'N/A'))
        
        print(f"\n📅 تعداد روزهای تمرین: {len(result.get('days', []))}")
        
        for day in result.get('days', []):
            print(f"\n   {day.get('day_name', 'نامشخص')}: {day.get('focus', 'نامشخص')}")
            print(f"      تعداد تمرینات: {len(day.get('exercises', []))}")
            print(f"      گرم کردن: {day.get('warmup', 'نامشخص')[:50]}...")
            print(f"      سرد کردن: {day.get('cooldown', 'نامشخص')[:50]}...")
        
        print(f"\n✅ برنامه کامل در فایل ذخیره شد: {output_file}")
        print("=" * 80)
        
    except Exception as e:
        print(f"\n❌ خطا: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()


if __name__ == "__main__":
    test_workout_generator()

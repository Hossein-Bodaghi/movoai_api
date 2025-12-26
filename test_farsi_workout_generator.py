"""
Test script for Two-Agent Workout System with AvalAI API
Tests both Strategist Agent (12-week strategy) and Plan Generator Agent (weekly plans)
"""
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from sqlalchemy.orm import Session
from app.database.session import SessionLocal
from ai.workout_strategist import generate_workout_strategy
from ai.workout_generator_farsi import generate_farsi_workout_plan
import json


def test_strategist_agent():
    """Test the Strategist Agent (12-week strategy generation)"""
    
    # Create a test user profile
    test_profile = {
        "user_id": "test_strategist_001",
        "age": 28,
        "weight": 75,
        "height": 175,
        "gender": "male",
        "workout_goal_id": 2,  # Build muscle
        "physical_fitness": "intermediate",
        "fitness_days": 4,
        "workout_limitations": "بدون محدودیت",
        "specialized_sport": "ندارد",
        "training_location": "gym",
        "equipment_ids": [1, 2, 3, 5]  # Bodyweight, Dumbbells, Barbell, Cables
    }
    
    print("=" * 80)
    print("🎯 PHASE 1: STRATEGIST AGENT TEST")
    print("=" * 80)
    print(f"\n📋 اطلاعات کاربر:")
    print(f"   شناسه: {test_profile['user_id']}")
    print(f"   سن: {test_profile['age']} سال")
    print(f"   وزن: {test_profile['weight']} کیلوگرم")
    print(f"   سطح آمادگی: {test_profile['physical_fitness']}")
    print(f"   هدف: ساخت عضله")
    print(f"   روزهای تمرین: {test_profile['fitness_days']}")
    print("\n" + "-" * 80 + "\n")
    
    try:
        # Generate 12-week strategy
        print("🤖 در حال تولید استراتژی ۱۲ هفته‌ای...")
        strategy = generate_workout_strategy(test_profile)
        
        # Save to file
        output_file = "test_strategy_output.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(strategy, f, ensure_ascii=False, indent=2)
        
        print("\n" + "=" * 80)
        print("📊 خلاصه استراتژی")
        print("=" * 80)
        
        print("\n🔹 DETAILED STRATEGY (برای هوش مصنوعی برنامه‌ساز):")
        print(f"   طول: {len(strategy['detailed_strategy'])} کاراکتر")
        print(f"   پیش‌نمایش: {strategy['detailed_strategy'][:300]}...")
        
        print("\n🔹 USER SUMMARY (برای نمایش به کاربر):")
        print(f"   {strategy['user_summary']}")
        
        print("\n🔹 EXPECTATIONS (انتظارات):")
        print(f"   {strategy['expectations']}")
        
        print(f"\n✅ استراتژی کامل در فایل ذخیره شد: {output_file}")
        print("=" * 80)
        
        return strategy
        
    except Exception as e:
        print(f"\n❌ خطا: {e}")
        import traceback
        traceback.print_exc()
        return None


def test_plan_generator(strategy_data):
    """Test the Plan Generator Agent (weekly plan generation)"""
    
    if not strategy_data:
        print("\n⚠️  استراتژی موجود نیست. ابتدا تست Strategist Agent را اجرا کنید.")
        return
    
    # Create a test user profile
    test_profile = {
        "user_id": "test_generator_001",
        "age": 28,
        "weight": 75,
        "height": 175,
        "gender": "male",
        "workout_goal_id": 2,
        "physical_fitness": "intermediate",
        "fitness_days": 4,
        "workout_limitations": "بدون محدودیت",
        "specialized_sport": "ندارد",
        "training_location": "gym",
        "equipment_ids": [1, 2, 3, 5]
    }
    
    print("\n\n" + "=" * 80)
    print("📅 PHASE 2: PLAN GENERATOR AGENT TEST")
    print("=" * 80)
    print(f"\n📋 تولید برنامه تمرینی هفته ۱:")
    print(f"   بر اساس استراتژی ۱۲ هفته‌ای")
    print(f"   روزهای تمرین: {test_profile['fitness_days']}")
    print("\n" + "-" * 80 + "\n")
    
    # Create database session
    db = SessionLocal()
    
    try:
        # Generate week 1 plan
        print("🤖 در حال تولید برنامه هفته اول...")
        
        # NOTE: This will use the OLD generate_farsi_workout_plan for now
        # After refactoring, it should accept:
        # - db
        # - user_profile
        # - detailed_strategy (from strategist)
        # - week_number (1)
        # - previous_week_plan (None for week 1)
        # - feedback (None for week 1)
        
        result = generate_farsi_workout_plan(db, test_profile)
        
        # Save to file
        output_file = "test_week1_plan_output.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        
        print("\n" + "=" * 80)
        print("📊 خلاصه برنامه هفته ۱")
        print("=" * 80)
        
        # Note: After refactoring, this should show week_note
        print("\n🗒️  یادداشت هفته:")
        print(f"   {result.get('week_note', 'در نسخه فعلی موجود نیست')}")
        
        print("\n🎯 استراتژی کلی:")
        print(f"   {result.get('strategy', 'N/A')[:200]}...")
        
        print(f"\n📅 تعداد روزهای تمرین: {len(result.get('days', []))}")
        
        for day in result.get('days', []):
            print(f"\n   {day.get('day_name', 'نامشخص')}: {day.get('focus', 'نامشخص')}")
            print(f"      تعداد تمرینات: {len(day.get('exercises', []))}")
            
            # Show first exercise details (note: tempo/notes should be removed after refactoring)
            if day.get('exercises'):
                ex = day['exercises'][0]
                print(f"      نمونه تمرین:")
                print(f"        - ست: {ex.get('sets', 'N/A')}")
                print(f"        - تکرار: {ex.get('reps', 'N/A')}")
                print(f"        - استراحت: {ex.get('rest', 'N/A')}")
                # These should be removed in new architecture:
                if 'tempo' in ex:
                    print(f"        - تمپو: {ex.get('tempo', 'N/A')} [باید حذف شود]")
                if 'notes' in ex:
                    print(f"        - یادداشت: {ex.get('notes', 'N/A')[:30]}... [باید حذف شود]")
        
        print(f"\n✅ برنامه کامل در فایل ذخیره شد: {output_file}")
        print("=" * 80)
        
        # Show refactoring notes
        print("\n" + "=" * 80)
        print("📝 یادداشت‌های بازسازی (Refactoring Notes)")
        print("=" * 80)
        print("\n⚠️  نسخه فعلی از تابع قدیمی استفاده می‌کند.")
        print("\n✨ پس از بازسازی کامل:")
        print("   1. تابع باید detailed_strategy را دریافت کند")
        print("   2. تابع باید week_number را دریافت کند")
        print("   3. تابع باید previous_week_plan و feedback را پشتیبانی کند")
        print("   4. خروجی باید شامل week_note باشد")
        print("   5. تمرینات نباید tempo و notes داشته باشند")
        print("=" * 80)
        
    except Exception as e:
        print(f"\n❌ خطا: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()


def test_complete_workflow():
    """Test the complete two-agent workflow"""
    
    print("\n" + "🏋️  MOVOKIO TWO-AGENT WORKOUT SYSTEM TEST" + "\n")
    print("این تست هر دو عامل هوش مصنوعی را آزمایش می‌کند:")
    print("  1. Strategist Agent: تولید استراتژی ۱۲ هفته‌ای")
    print("  2. Plan Generator Agent: تولید برنامه هفتگی")
    print("\n" + "=" * 80 + "\n")
    
    # Test Phase 1: Strategist
    strategy = test_strategist_agent()
    
    # Test Phase 2: Plan Generator
    test_plan_generator(strategy)
    
    print("\n\n" + "=" * 80)
    print("✅ تست کامل شد!")
    print("=" * 80)
    print("\nفایل‌های خروجی:")
    print("  - test_strategy_output.json (استراتژی ۱۲ هفته‌ای)")
    print("  - test_week1_plan_output.json (برنامه هفته ۱)")
    print("=" * 80 + "\n")


if __name__ == "__main__":
    test_complete_workflow()

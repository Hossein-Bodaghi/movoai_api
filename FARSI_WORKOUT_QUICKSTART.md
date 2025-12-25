# Quick Start: Farsi Workout Generator

## Setup

1. **Install dependencies** (if not already installed):
```bash
pip install -r requirements.txt
```

2. **Configure environment variables** in `.env`:
```bash
# AvalAI API Key (required)
x-goog-api-key=your_avalai_api_key_here

# Database URL (required)
DATABASE_URL=postgresql://postgres:926121008@localhost:5432/workout_db

# Other existing config...
```

3. **Verify database connection**:
```bash
# Test database connection
python -c "from app.database.session import SessionLocal; db = SessionLocal(); print('✅ Database connected'); db.close()"
```

## Usage

### Option 1: Via API Endpoint

1. **Start the server**:
```bash
uvicorn app.main:app --reload
```

2. **Create a workout plan**:
```bash
curl -X POST "http://localhost:8000/api/v1/workout-plans" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "برنامه تمرینی من",
    "total_weeks": 1,
    "workout_goal_id": 1
  }'
```

### Option 2: Run Test Script

```bash
python test_farsi_workout_generator.py
```

This will:
- Create a test user profile
- Generate a workout plan using AvalAI
- Save output to `test_farsi_workout_plan_output.json`
- Display summary in console

### Option 3: Direct Python Usage

```python
from sqlalchemy.orm import Session
from app.database.session import SessionLocal
from ai.workout_generator_farsi import generate_farsi_workout_plan

# User profile
user_profile = {
    'user_id': 'test_user',
    'age': 28,
    'weight': 75,
    'height': 175,
    'gender': 'male',
    'workout_goal_id': 1,
    'physical_fitness': 'intermediate',
    'fitness_days': 4,
    'workout_limitations': 'بدون محدودیت',
    'specialized_sport': 'ندارد',
    'training_location': 'gym',
    'equipment_ids': [1, 2, 3, 4, 5, 6]
}

# Generate
db = SessionLocal()
plan = generate_farsi_workout_plan(db, user_profile)
db.close()

print(plan['strategy'])
print(plan['expectations'])
```

## Expected Output

The generator returns a structured plan with:

```json
{
  "strategy": "استراتژی کلی برنامه (2-3 پاراگراف فارسی)",
  "expectations": "انتظارات و نتایج (2-3 پاراگراف فارسی)",
  "days": [
    {
      "day_name": "شنبه",
      "focus": "تمرین تمام بدن",
      "warmup": "5-10 دقیقه کشش پویا و حرکات آماده‌سازی",
      "cooldown": "5-10 دقیقه کشش ایستا و فوم رولر",
      "exercises": [
        {
          "exercise_id": 123,
          "sets": "3",
          "reps": "10-12",
          "tempo": "2-0-2-0",
          "rest": "60 ثانیه",
          "notes": "یادداشت‌های اضافی",
          "exercise_order": 1
        }
      ]
    }
  ]
}
```

## Troubleshooting

### ❌ "x-goog-api-key not found"
→ Add API key to `.env` file

### ❌ "Failed to connect to database"
→ Check DATABASE_URL in `.env`
→ Ensure PostgreSQL is running
→ Verify database `workout_db` exists

### ❌ "No exercises found"
→ Check equipment IDs exist in database
→ Verify muscle groups match database values

### ❌ "AvalAI API timeout"
→ Check internet connection
→ Verify API key is valid
→ Try again (automatic retry on failure)

## What Gets Generated?

For a user with:
- **Fitness level**: Intermediate
- **Training days**: 4 days/week
- **Location**: Gym
- **Equipment**: Dumbbells, Barbell, Cables, Machines

You'll get:
1. ✅ **Strategy** - Overall training approach in Farsi
2. ✅ **Expectations** - What results to expect
3. ✅ **4 daily workouts** with:
   - Day name (شنبه، یکشنبه، etc.)
   - Focus area (سینه، پشت، پاها، etc.)
   - Warmup routine
   - 4-6 main exercises with sets/reps/tempo/rest
   - Cooldown routine

## Testing Checklist

- [ ] Environment variables configured
- [ ] Database connection works
- [ ] Test script runs successfully
- [ ] API endpoint returns 201 Created
- [ ] Output JSON contains Farsi text
- [ ] Exercise IDs are valid
- [ ] Sets/reps/rest are specified

## Next Steps

1. ✅ Generator is working
2. 🔄 Test with different user profiles
3. 🔄 Verify exercise variety
4. 🔄 Check Farsi text quality
5. 🔄 Test error handling
6. 🔄 Deploy to production

## Documentation

See `FARSI_WORKOUT_GENERATOR_DOCS.md` for comprehensive documentation.

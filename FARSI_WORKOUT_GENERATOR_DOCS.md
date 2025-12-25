# Farsi Workout Plan Generator Documentation

## Overview

The Farsi Workout Plan Generator is an AI-powered system that creates personalized workout plans in Farsi (Persian) using the AvalAI API and the workout_db PostgreSQL database. It generates comprehensive weekly workout plans based on user profiles, fitness goals, available equipment, and physical limitations.

## Architecture

### Components

1. **`ai/workout_generator_farsi.py`** - Main AI generator module
   - `FarsiExerciseSearchEngine` - SQL-based exercise search engine
   - `FarsiWorkoutPlanGenerator` - AvalAI-powered plan generator
   - `generate_farsi_workout_plan()` - Main API function

2. **`app/api/v1/endpoints/workout_plans.py`** - REST API endpoint
   - Integrated with the Farsi generator
   - Handles user authentication and data validation
   - Creates database records for workout plans

### Data Flow

```
User Profile → Exercise Search (SQL) → AvalAI API → Structured Plan → Database
```

## Features

### 1. User Profile Analysis
The generator considers:
- **Physical attributes**: Age, weight, height, gender
- **Fitness level**: Beginner, Intermediate, Advanced, Expert
- **Training schedule**: 1-7 days per week
- **Equipment availability**: Home, gym, or outdoor equipment
- **Goals**: Strength, muscle building, weight loss, endurance, etc.
- **Limitations**: Physical restrictions or injuries
- **Specialized sports**: Sport-specific training needs

### 2. Exercise Database Integration
- Uses PostgreSQL `workout_db` with 1000+ exercises
- Filters exercises by:
  - Difficulty level (matched to user's fitness level)
  - Muscle groups (based on training split)
  - Equipment availability (user's equipment only)
  - Exercise style (warmup, main, cooldown, cardio, stretches)

### 3. AvalAI API Integration
- **Model**: Gemini 2.5 Pro
- **Language**: All prompts and responses in Farsi
- **Output**: Structured JSON with:
  - Overall strategy (استراتژی)
  - Expected results (انتظارات)
  - Daily workout plans with exercises, sets, reps, tempo, rest

### 4. Weekly Training Splits
Automatically generates optimal splits based on training frequency:

- **1-3 days**: Full body workouts
- **4 days**: Upper/Lower split
- **5 days**: Push/Pull/Legs + Shoulders/Arms + Core
- **6-7 days**: Body part split with optional active recovery

### 5. Farsi Language Support
- All exercise names in Farsi
- All instructions in Farsi
- All workout descriptions in Farsi
- Persian day names (شنبه، یکشنبه، etc.)

## Usage

### API Endpoint

**POST** `/api/v1/workout-plans`

```json
{
  "name": "برنامه تمرینی من",
  "total_weeks": 1,
  "workout_goal_id": 1
}
```

**Response:**
```json
{
  "plan_id": 123,
  "user_id": 456,
  "name": "برنامه تمرینی من",
  "total_weeks": 1,
  "current_week": 1,
  "strategy": "این برنامه تمرینی بر اساس اطلاعات پروفایل شما...",
  "expectations": "در پایان این برنامه، انتظار می‌رود که...",
  "weeks": [
    {
      "week_number": 1,
      "title": "هفته اول",
      "days": [
        {
          "day_name": "شنبه",
          "focus": "تمرین تمام بدن",
          "warmup": "5-10 دقیقه کشش پویا",
          "cooldown": "5-10 دقیقه کشش ایستا",
          "exercises": [
            {
              "exercise_id": 789,
              "sets": "3",
              "reps": "10-12",
              "tempo": "2-0-2-0",
              "rest": "60 ثانیه",
              "notes": "تمرین اسکوات",
              "exercise_order": 1,
              "exercise": {
                "name_fa": "اسکوات با وزن بدن",
                "instructions_fa": ["..."],
                "difficulty": {"name_fa": "مبتدی"}
              }
            }
          ]
        }
      ]
    }
  ]
}
```

### Python Function Call

```python
from sqlalchemy.orm import Session
from ai.workout_generator_farsi import generate_farsi_workout_plan

# Prepare user profile
user_profile = {
    'user_id': 'user_123',
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

# Generate plan
db = SessionLocal()
workout_plan = generate_farsi_workout_plan(db, user_profile)
db.close()
```

## Configuration

### Environment Variables

Required in `.env` file:

```bash
# AvalAI API
x-goog-api-key=your_avalai_api_key_here

# Database
DATABASE_URL=postgresql://user:password@localhost:5432/workout_db
```

### Database Tables Used

1. **exercise** - Exercise library
2. **difficulty** - Difficulty levels
3. **equipment** - Equipment types
4. **muscle** - Muscle groups
5. **exercise_equipment** - Exercise-equipment relationships
6. **exercise_muscle** - Exercise-muscle relationships
7. **workout_goals** - Workout goals/objectives
8. **users** - User profiles
9. **user_home_equipment** - User's home equipment
10. **user_gym_equipment** - User's gym equipment

## Testing

Run the test script:

```bash
python test_farsi_workout_generator.py
```

This will:
1. Create a test user profile
2. Generate a workout plan using AvalAI
3. Save the output to `test_farsi_workout_plan_output.json`
4. Display a summary in the console

## Error Handling

### Fallback Mechanism
If AvalAI API fails:
1. The system automatically generates a simple fallback plan
2. Uses basic exercise selection from database
3. Applies standard sets/reps/rest recommendations
4. Still saves a valid workout plan

### Retry Logic
- AvalAI API calls retry up to 3 times on failure
- 60-second timeout per request
- Handles network errors gracefully

## Performance

- **Exercise search**: <100ms (SQL queries)
- **AvalAI API call**: 5-15 seconds (depends on network/API)
- **Total generation time**: 6-20 seconds per plan
- **Database writes**: <500ms

## Limitations

1. **Currently supports 1-week plans only** (can be extended to 4 or 12 weeks)
2. **Requires active internet** for AvalAI API
3. **Requires valid API key** in environment
4. **Equipment must be predefined** in database
5. **Muscle groups must match** database enum values

## Future Enhancements

1. Multi-week plan support (4, 12 weeks)
2. Progressive overload tracking
3. Exercise substitution suggestions
4. Video/image links for exercises
5. Workout history analysis
6. Real-time difficulty adjustment
7. Integration with nutrition plans
8. Mobile app support

## Troubleshooting

### Issue: "x-goog-api-key not found"
**Solution**: Add the API key to your `.env` file

### Issue: "No exercises found"
**Solution**: Check equipment IDs match database, verify muscle group names

### Issue: "AvalAI API timeout"
**Solution**: Check internet connection, verify API key is valid

### Issue: "Invalid response from AvalAI"
**Solution**: System will use fallback plan, check API logs for details

## Code Examples

### Custom Exercise Selection

```python
from ai.workout_generator_farsi import FarsiExerciseSearchEngine

search_engine = FarsiExerciseSearchEngine()
exercises = search_engine.search_exercises(
    db=db,
    difficulty='Intermediate',
    muscle_groups=['Chest', 'Shoulders'],
    equipment_ids=[1, 2, 3],
    limit=20
)
```

### Direct AvalAI API Call

```python
generator = FarsiWorkoutPlanGenerator(search_engine)
response = generator._call_avalai_api(
    system_instructions="شما یک مربی تناسب اندام هستید...",
    user_message="برنامه تمرینی برای من ایجاد کن"
)
```

## License

This module is part of the MovoAI API project.

## Support

For issues or questions, contact the development team.

# AI Architecture Refactoring Summary

## Overview
Transitioning from single-agent to two-agent system for workout plan generation.

## Changes Required

### 1. Database Models (`app/models/workout_plan.py`)

**WorkoutPlan Model:**
- ADD: `detailed_strategy` (Text) - Technical 12-week strategy for Plan Generator AI
- KEEP: `strategy` (Text) - Renamed purpose: User-friendly summary from Strategist
- KEEP: `expectations` (Text) - Realistic outcomes from Strategist

**WorkoutWeek Model:**
- ADD: `week_note` (Text) - Description of the week's goal and focus

**WorkoutDayExercise Model:**
- REMOVE: `tempo` (String) - No longer needed per requirements
- REMOVE: `notes` (Text) - No longer needed per requirements
- KEEP: `sets`, `reps`, `rest`, `exercise_order`

### 2. Pydantic Schemas (`app/schemas/workout_plan.py`)

**WorkoutPlanCreate:**
- No changes (still accepts name, total_weeks, workout_goal_id)

**WorkoutPlanResponse:**
- ADD: `detailed_strategy: Optional[str]` (hidden from users, for internal use)
- KEEP: `strategy: Optional[str]` (user summary)
- KEEP: `expectations: Optional[str]`

**WorkoutWeekResponse:**
- ADD: `week_note: Optional[str]`

**WorkoutDayExerciseResponse:**
- REMOVE: `tempo: Optional[str]`
- REMOVE: `notes: Optional[str]`

### 3. AI Modules

**NEW: `ai/workout_strategist.py`** ✅ CREATED
- Class: `FarsiWorkoutStrategist`
- Method: `generate_strategy(user_profile) -> Dict`
- Outputs:
  - `detailed_strategy`: For Plan Generator (technical, 200+ chars)
  - `user_summary`: For user display (50-500 chars)
  - `expectations`: Realistic outcomes (50-500 chars)

**MODIFY: `ai/workout_generator_farsi.py`**
- Class: `FarsiWorkoutPlanGenerator`
- Method signature CHANGE:
  ```python
  def generate_weekly_plan(
      db: Session,
      user_profile: Dict,
      detailed_strategy: str,
      week_number: int,
      previous_week_plan: Optional[Dict] = None,
      feedback: Optional[str] = None
  ) -> Dict
  ```
- Output structure CHANGE:
  ```python
  {
    "week_note": "توضیح هدف این هفته...",
    "days": [
      {
        "day_name": "شنبه",
        "focus": "سینه و شانه",
        "warmup": "گرم کردن...",
        "cooldown": "سرد کردن...",
        "exercises": [
          {
            "exercise_id": 123,
            "sets": "3",
            "reps": "10-12",
            "rest": "60 ثانیه",
            "exercise_order": 1
            # NO tempo
            # NO notes
          }
        ]
      }
    ]
  }
  ```

### 4. API Endpoint (`app/api/v1/endpoints/workout_plans.py`)

**POST /api/v1/workout-plans (create_workout_plan)**
- CHANGE workflow:
  1. Validate user input
  2. Check if plan exists and has `detailed_strategy`
     - If NO: Call `workout_strategist.generate_strategy()`
     - Save `detailed_strategy`, `strategy` (user_summary), `expectations`
  3. Call `workout_generator_farsi.generate_weekly_plan()` for week 1
     - Pass `detailed_strategy`, `week_number=1`
     - No previous plan/feedback
  4. Create WorkoutWeek with `week_note`
  5. Create WorkoutDays
  6. Create WorkoutDayExercises (without tempo/notes)

**NEW: POST /api/v1/workout-plans/{plan_id}/generate-next-week**
- Generate next week for existing plan
- Workflow:
  1. Get existing WorkoutPlan (has detailed_strategy)
  2. Get previous week's data
  3. Get user feedback (optional)
  4. Call `workout_generator_farsi.generate_weekly_plan()`
     - Pass `detailed_strategy`, `week_number`, `previous_week_plan`, `feedback`
  5. Create new WorkoutWeek with `week_note`
  6. Create WorkoutDays and WorkoutDayExercises

### 5. Migration Required

**Alembic Migration:**
```python
# Add columns
op.add_column('workout_plan', sa.Column('detailed_strategy', sa.Text(), nullable=True))
op.add_column('workout_week', sa.Column('week_note', sa.Text(), nullable=True))

# Drop columns
op.drop_column('workout_day_exercise', 'tempo')
op.drop_column('workout_day_exercise', 'notes')
```

## Implementation Order

1. ✅ Update ARCHITECTURE_DIAGRAM.md
2. ✅ Create ai/workout_strategist.py
3. ⏳ Update database models
4. ⏳ Create Alembic migration
5. ⏳ Update Pydantic schemas
6. ⏳ Modify ai/workout_generator_farsi.py
7. ⏳ Update workout_plans.py endpoint
8. ⏳ Test complete flow

## Testing Strategy

1. Test Strategist Agent standalone
2. Test Plan Generator with mock strategy
3. Test complete API flow
4. Test week progression with feedback
5. Verify database changes applied correctly

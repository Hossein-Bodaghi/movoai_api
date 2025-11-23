# Quick Start Guide: Testing Phase 2 & 3 APIs

## Prerequisites

1. **Database Setup**: Ensure PostgreSQL is running with the complete schema
2. **Authentication**: Have a valid JWT token (use `/api/v1/auth/login` or `/api/v1/auth/telegram`)
3. **User Profile**: Ensure your user has fitness profile data (age, weight, height, fitness_days)

## 🚀 Quick Test Flow

### Step 1: Get Available Goals

```bash
# Get workout goals
curl http://localhost:8000/api/v1/goals/workout

# Get nutrition goals
curl http://localhost:8000/api/v1/goals/nutrition
```

### Step 2: Create Your First Workout Plan

```bash
curl -X POST http://localhost:8000/api/v1/workout-plans \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test 1-Week Plan",
    "workout_goal_id": 1,
    "total_weeks": 1
  }'
```

**Response includes**:
- Complete plan details
- All weeks (1 week in this case)
- All workout days (based on your fitness_days)
- All exercises with sets/reps/tempo/rest
- Mock AI strategy and expectations

### Step 3: Create Your First Nutrition Plan

```bash
curl -X POST http://localhost:8000/api/v1/nutrition-plans \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test 1-Week Meal Plan",
    "nutrition_goal_id": 1,
    "total_weeks": 1
  }'
```

**Response includes**:
- Complete plan details
- All weeks (1 week)
- 7 days of meals
- 4 meals per day (breakfast, lunch, dinner, snacks)
- Calories and macros for each meal
- Mock AI strategy and expectations

### Step 4: View Your Plans

```bash
# List all workout plans
curl http://localhost:8000/api/v1/workout-plans \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"

# List all nutrition plans
curl http://localhost:8000/api/v1/nutrition-plans \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

### Step 5: Get Specific Week

```bash
# Get week 1 of workout plan (replace {plan_id} with actual ID)
curl http://localhost:8000/api/v1/workout-plans/{plan_id}/week/1 \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"

# Get week 1 of nutrition plan
curl http://localhost:8000/api/v1/nutrition-plans/{plan_id}/week/1 \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

### Step 6: Track Progress

```bash
# Mark workout week as completed
curl -X POST http://localhost:8000/api/v1/workout-plans/{plan_id}/complete-week \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"week_number": 1}'

# Mark nutrition week as completed
curl -X POST http://localhost:8000/api/v1/nutrition-plans/{plan_id}/complete-week \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"week_number": 1}'
```

---

## 📋 Test Scenarios

### Scenario 1: Create a 12-Week Progressive Plan

```bash
curl -X POST http://localhost:8000/api/v1/workout-plans \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "12-Week Strength Building",
    "workout_goal_id": 2,
    "total_weeks": 12
  }'
```

This will generate:
- 12 weeks of workouts
- ~336 workout day exercises (12 weeks × 4 days × 7 exercises)
- Progressive strategy with Foundation → Building → Peak phases

### Scenario 2: Create a 4-Week Nutrition Plan

```bash
curl -X POST http://localhost:8000/api/v1/nutrition-plans \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "4-Week Clean Eating",
    "nutrition_goal_id": 5,
    "total_weeks": 4
  }'
```

This will generate:
- 4 weeks of meal plans
- 112 meals (4 weeks × 7 days × 4 meals)
- Calorie targets based on your profile

### Scenario 3: Update Plan Name

```bash
curl -X PUT http://localhost:8000/api/v1/workout-plans/{plan_id} \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "My Updated Plan Name"
  }'
```

### Scenario 4: Delete Plan

```bash
curl -X DELETE http://localhost:8000/api/v1/workout-plans/{plan_id} \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

---

## 🧪 Python Test Script

Save this as `test_plans.py`:

```python
import requests

BASE_URL = "http://localhost:8000/api/v1"
TOKEN = "YOUR_JWT_TOKEN"

headers = {
    "Authorization": f"Bearer {TOKEN}",
    "Content-Type": "application/json"
}

# Create workout plan
workout_plan = {
    "name": "Test Workout Plan",
    "workout_goal_id": 1,
    "total_weeks": 1
}

response = requests.post(f"{BASE_URL}/workout-plans", json=workout_plan, headers=headers)
print(f"Workout Plan Created: {response.status_code}")
workout_plan_id = response.json()["plan_id"]

# Create nutrition plan
nutrition_plan = {
    "name": "Test Nutrition Plan",
    "nutrition_goal_id": 1,
    "total_weeks": 1
}

response = requests.post(f"{BASE_URL}/nutrition-plans", json=nutrition_plan, headers=headers)
print(f"Nutrition Plan Created: {response.status_code}")
nutrition_plan_id = response.json()["plan_id"]

# Get workout week 1
response = requests.get(f"{BASE_URL}/workout-plans/{workout_plan_id}/week/1", headers=headers)
print(f"Workout Week 1: {len(response.json()['days'])} days")

# Get nutrition week 1
response = requests.get(f"{BASE_URL}/nutrition-plans/{nutrition_plan_id}/week/1", headers=headers)
print(f"Nutrition Week 1: {len(response.json()['days'])} days")

# Complete weeks
requests.post(f"{BASE_URL}/workout-plans/{workout_plan_id}/complete-week", 
              json={"week_number": 1}, headers=headers)
print("Workout week 1 completed")

requests.post(f"{BASE_URL}/nutrition-plans/{nutrition_plan_id}/complete-week", 
              json={"week_number": 1}, headers=headers)
print("Nutrition week 1 completed")
```

Run with: `python test_plans.py`

---

## 🔍 What to Check

### Workout Plan Response Structure

```json
{
  "plan_id": 1,
  "user_id": 123,
  "name": "My Workout Plan",
  "workout_goal_id": 1,
  "total_weeks": 1,
  "current_week": 1,
  "completed_weeks": [],
  "strategy": {
    "focus": "performance_enhancement",
    "approach": "Progressive overload with periodization",
    "training_days_per_week": 3,
    "notes": "Mock strategy..."
  },
  "expectations": {
    "strength_gain": "5-10%",
    "notes": "Mock expectations..."
  },
  "weeks": [
    {
      "week_id": 1,
      "week_number": 1,
      "title": "Week 1: Building Phase",
      "days": [
        {
          "day_id": 1,
          "day_name": "Monday",
          "focus": "Upper Body",
          "warmup": "5-10 minutes...",
          "exercises": [
            {
              "workout_day_exercise_id": 1,
              "exercise_id": 42,
              "sets": "4",
              "reps": "10",
              "tempo": "2-0-2-0",
              "rest": "75 seconds",
              "exercise_order": 1,
              "exercise": {
                "exercise_id": 42,
                "name_en": "Bench Press",
                "name_fa": "..."
              }
            }
          ]
        }
      ]
    }
  ]
}
```

### Nutrition Plan Response Structure

```json
{
  "plan_id": 1,
  "user_id": 123,
  "name": "My Nutrition Plan",
  "nutrition_goal_id": 1,
  "total_weeks": 1,
  "current_week": 1,
  "completed_weeks": [],
  "strategy": {
    "calorie_target": 2450,
    "macro_split": {
      "protein": "30%",
      "carbs": "40%",
      "fats": "30%"
    }
  },
  "weeks": [
    {
      "week_id": 1,
      "week_number": 1,
      "title": "Week 1: Balanced Nutrition",
      "days": [
        {
          "day_id": 1,
          "day_name": "Monday",
          "daily_calories": 2450,
          "meals": [
            {
              "meal_id": 1,
              "meal_type": "breakfast",
              "name": "Greek Yogurt Parfait",
              "description": "Greek yogurt with berries...",
              "calories": 613,
              "protein": 45.9,
              "carbs": 61.3,
              "fats": 20.4
            }
          ]
        }
      ]
    }
  ]
}
```

---

## ⚠️ Common Issues

### Issue 1: No exercises in workout days
**Cause**: No exercises in the database  
**Solution**: Ensure the exercise table is populated from your CSV data

### Issue 2: Calories seem wrong
**Cause**: User profile missing weight/age  
**Solution**: Update user profile with complete data

### Issue 3: "Workout goal not found"
**Cause**: Invalid workout_goal_id  
**Solution**: First call `/api/v1/goals/workout` to get valid IDs

### Issue 4: 401 Unauthorized
**Cause**: Invalid or expired JWT token  
**Solution**: Login again to get a fresh token

---

## 📊 Database Verification

After creating plans, verify in PostgreSQL:

```sql
-- Check workout plans
SELECT 
    wp.plan_id, 
    wp.name,
    wp.total_weeks,
    COUNT(DISTINCT ww.week_id) as week_count,
    COUNT(DISTINCT wd.day_id) as day_count,
    COUNT(wde.workout_day_exercise_id) as exercise_count
FROM workout_plans wp
LEFT JOIN workout_weeks ww ON wp.plan_id = ww.plan_id
LEFT JOIN workout_days wd ON ww.week_id = wd.week_id
LEFT JOIN workout_day_exercises wde ON wd.day_id = wde.day_id
GROUP BY wp.plan_id;

-- Check nutrition plans
SELECT 
    np.plan_id,
    np.name,
    np.total_weeks,
    COUNT(DISTINCT nw.week_id) as week_count,
    COUNT(DISTINCT nd.day_id) as day_count,
    COUNT(m.meal_id) as meal_count
FROM nutrition_plans np
LEFT JOIN nutrition_weeks nw ON np.plan_id = nw.plan_id
LEFT JOIN nutrition_days nd ON nw.week_id = nd.week_id
LEFT JOIN meals m ON nd.day_id = m.day_id
GROUP BY np.plan_id;
```

---

## ✅ Success Criteria

- ✅ Can create 1, 4, and 12-week plans
- ✅ All weeks/days/exercises are generated
- ✅ Exercise references are valid (exist in database)
- ✅ Macros add up correctly
- ✅ Progress tracking works (complete-week endpoint)
- ✅ Can fetch specific weeks
- ✅ Cascade deletion works
- ✅ Only owner can access their plans

---

## 🔄 Next Steps

Once real AI agents are implemented:

1. Replace mock functions in `workout_plans.py`:
   - `generate_mock_strategy()`
   - `generate_mock_expectations()`
   - `get_random_exercises()`
   - `generate_mock_workout_week()`

2. Replace mock functions in `nutrition_plans.py`:
   - `generate_mock_nutrition_strategy()`
   - `generate_mock_nutrition_expectations()`
   - `generate_mock_meals()`
   - `generate_mock_nutrition_week()`

All functions are clearly marked with "Mock" in their names and docstrings.

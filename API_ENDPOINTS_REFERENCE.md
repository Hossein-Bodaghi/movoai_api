# API Endpoints Reference

Complete reference for Phase 2 (Workout Plans) and Phase 3 (Nutrition Plans) APIs.

---

## 🏋️ Workout Plans API

### POST /api/v1/workout-plans
Create a new workout plan with AI-generated content.

**Authentication**: Required (JWT Bearer Token)

**Request Body**:
| Field | Type | Required | Description | Constraints |
|-------|------|----------|-------------|-------------|
| name | string | Yes | Plan name | Max 255 chars |
| workout_goal_id | integer | No | Workout goal ID | Must exist in workout_goals |
| total_weeks | integer | Yes | Duration in weeks | Must be 1, 4, or 12 |

**Example Request**:
```json
{
  "name": "12-Week Strength Building Program",
  "workout_goal_id": 3,
  "total_weeks": 12
}
```

**Success Response** (201 Created):
```json
{
  "plan_id": 1,
  "user_id": 123,
  "name": "12-Week Strength Building Program",
  "workout_goal_id": 3,
  "total_weeks": 12,
  "current_week": 1,
  "completed_weeks": [],
  "strategy": {
    "focus": "performance_enhancement",
    "goal": "Build Explosive Power",
    "approach": "Progressive overload with periodization",
    "training_days_per_week": 4,
    "session_duration": "45-60 minutes"
  },
  "expectations": {
    "strength_gain": "20-30%",
    "muscle_gain": "4-8 lbs",
    "body_composition": "2-4% body fat reduction"
  },
  "weeks": [...],
  "created_at": "2025-11-23T10:00:00Z",
  "updated_at": "2025-11-23T10:00:00Z"
}
```

**Error Responses**:
- 400 Bad Request: Invalid total_weeks or workout_goal_id
- 401 Unauthorized: Missing or invalid token
- 404 Not Found: Workout goal not found

---

### GET /api/v1/workout-plans
Get all workout plans for the authenticated user.

**Authentication**: Required

**Success Response** (200 OK):
```json
{
  "plans": [
    {
      "plan_id": 1,
      "user_id": 123,
      "name": "Strength Program",
      "workout_goal_id": 3,
      "total_weeks": 12,
      "current_week": 3,
      "completed_weeks": [1, 2],
      "strategy": {...},
      "expectations": {...},
      "created_at": "2025-11-23T10:00:00Z",
      "updated_at": "2025-11-23T10:00:00Z"
    }
  ],
  "total": 1
}
```

---

### GET /api/v1/workout-plans/{plan_id}
Get detailed workout plan including all weeks, days, and exercises.

**Authentication**: Required

**Path Parameters**:
| Parameter | Type | Description |
|-----------|------|-------------|
| plan_id | integer | Workout plan ID |

**Success Response** (200 OK):
```json
{
  "plan_id": 1,
  "name": "Strength Program",
  "weeks": [
    {
      "week_id": 1,
      "week_number": 1,
      "title": "Week 1: Foundation",
      "description": "Focus on form and technique",
      "days": [
        {
          "day_id": 1,
          "day_name": "Monday",
          "focus": "Upper Body",
          "warmup": "5-10 minutes dynamic stretching",
          "cooldown": "5-10 minutes static stretching",
          "exercises": [
            {
              "workout_day_exercise_id": 1,
              "exercise_id": 42,
              "sets": "4",
              "reps": "10",
              "tempo": "2-0-2-0",
              "rest": "75 seconds",
              "notes": "Focus on form",
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

**Error Responses**:
- 404 Not Found: Plan not found or doesn't belong to user

---

### GET /api/v1/workout-plans/{plan_id}/week/{week_number}
Get a specific week from a workout plan.

**Authentication**: Required

**Path Parameters**:
| Parameter | Type | Description |
|-----------|------|-------------|
| plan_id | integer | Workout plan ID |
| week_number | integer | Week number (1-12) |

**Success Response** (200 OK):
```json
{
  "week_id": 1,
  "plan_id": 1,
  "week_number": 1,
  "title": "Week 1: Foundation",
  "description": "...",
  "days": [...]
}
```

---

### PUT /api/v1/workout-plans/{plan_id}
Update workout plan details.

**Authentication**: Required

**Path Parameters**:
| Parameter | Type | Description |
|-----------|------|-------------|
| plan_id | integer | Workout plan ID |

**Request Body**:
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| name | string | No | New plan name |
| current_week | integer | No | Current week number |

**Example Request**:
```json
{
  "name": "Updated Program Name",
  "current_week": 4
}
```

**Success Response** (200 OK): Returns updated plan (without weeks)

---

### POST /api/v1/workout-plans/{plan_id}/complete-week
Mark a week as completed and advance progress.

**Authentication**: Required

**Path Parameters**:
| Parameter | Type | Description |
|-----------|------|-------------|
| plan_id | integer | Workout plan ID |

**Request Body**:
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| week_number | integer | Yes | Week to mark complete |

**Example Request**:
```json
{
  "week_number": 2
}
```

**Success Response** (200 OK):
```json
{
  "plan_id": 1,
  "week_number": 2,
  "current_week": 3,
  "completed_weeks": [1, 2],
  "message": "Week 2 marked as completed"
}
```

---

### DELETE /api/v1/workout-plans/{plan_id}
Delete a workout plan and all related data.

**Authentication**: Required

**Path Parameters**:
| Parameter | Type | Description |
|-----------|------|-------------|
| plan_id | integer | Workout plan ID |

**Success Response** (200 OK):
```json
{
  "message": "Workout plan deleted successfully"
}
```

---

## 🥗 Nutrition Plans API

### POST /api/v1/nutrition-plans
Create a new nutrition plan with AI-generated content.

**Authentication**: Required

**Request Body**:
| Field | Type | Required | Description | Constraints |
|-------|------|----------|-------------|-------------|
| name | string | Yes | Plan name | Max 255 chars |
| nutrition_goal_id | integer | No | Nutrition goal ID | Must exist in nutrition_goals |
| total_weeks | integer | Yes | Duration in weeks | Must be 1, 4, or 12 |

**Example Request**:
```json
{
  "name": "4-Week Clean Eating Plan",
  "nutrition_goal_id": 5,
  "total_weeks": 4
}
```

**Success Response** (201 Created):
```json
{
  "plan_id": 1,
  "user_id": 123,
  "name": "4-Week Clean Eating Plan",
  "nutrition_goal_id": 5,
  "total_weeks": 4,
  "current_week": 1,
  "completed_weeks": [],
  "strategy": {
    "focus": "body_recomposition",
    "calorie_target": 2450,
    "macro_split": {
      "protein": "30%",
      "carbs": "40%",
      "fats": "30%"
    },
    "meal_frequency": "3 main meals + 1 snack"
  },
  "expectations": {
    "weight_change": "2-4 lbs",
    "energy_levels": "Significant improvement"
  },
  "weeks": [...],
  "created_at": "2025-11-23T10:00:00Z",
  "updated_at": "2025-11-23T10:00:00Z"
}
```

---

### GET /api/v1/nutrition-plans
Get all nutrition plans for the authenticated user.

**Authentication**: Required

**Success Response** (200 OK):
```json
{
  "plans": [
    {
      "plan_id": 1,
      "user_id": 123,
      "name": "Clean Eating Plan",
      "nutrition_goal_id": 5,
      "total_weeks": 4,
      "current_week": 2,
      "completed_weeks": [1],
      "strategy": {...},
      "expectations": {...},
      "created_at": "2025-11-23T10:00:00Z",
      "updated_at": "2025-11-23T10:00:00Z"
    }
  ],
  "total": 1
}
```

---

### GET /api/v1/nutrition-plans/{plan_id}
Get detailed nutrition plan including all weeks, days, and meals.

**Authentication**: Required

**Path Parameters**:
| Parameter | Type | Description |
|-----------|------|-------------|
| plan_id | integer | Nutrition plan ID |

**Success Response** (200 OK):
```json
{
  "plan_id": 1,
  "name": "Clean Eating Plan",
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
              "description": "Greek yogurt with berries, granola, and honey",
              "calories": 613,
              "protein": 45.9,
              "carbs": 61.3,
              "fats": 20.4
            },
            {
              "meal_id": 2,
              "meal_type": "lunch",
              "name": "Grilled Chicken Salad",
              "calories": 857,
              "protein": 64.3,
              "carbs": 85.7,
              "fats": 28.6
            }
          ]
        }
      ]
    }
  ]
}
```

---

### GET /api/v1/nutrition-plans/{plan_id}/week/{week_number}
Get a specific week from a nutrition plan.

**Authentication**: Required

**Path Parameters**:
| Parameter | Type | Description |
|-----------|------|-------------|
| plan_id | integer | Nutrition plan ID |
| week_number | integer | Week number (1-12) |

**Success Response** (200 OK):
```json
{
  "week_id": 1,
  "plan_id": 1,
  "week_number": 1,
  "title": "Week 1: Balanced Nutrition",
  "days": [...]
}
```

---

### PUT /api/v1/nutrition-plans/{plan_id}
Update nutrition plan details.

**Authentication**: Required

**Path Parameters**:
| Parameter | Type | Description |
|-----------|------|-------------|
| plan_id | integer | Nutrition plan ID |

**Request Body**:
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| name | string | No | New plan name |
| current_week | integer | No | Current week number |

**Example Request**:
```json
{
  "name": "Updated Meal Plan"
}
```

---

### POST /api/v1/nutrition-plans/{plan_id}/complete-week
Mark a week as completed and advance progress.

**Authentication**: Required

**Path Parameters**:
| Parameter | Type | Description |
|-----------|------|-------------|
| plan_id | integer | Nutrition plan ID |

**Request Body**:
```json
{
  "week_number": 1
}
```

**Success Response** (200 OK):
```json
{
  "plan_id": 1,
  "week_number": 1,
  "current_week": 2,
  "completed_weeks": [1],
  "message": "Week 1 marked as completed"
}
```

---

### DELETE /api/v1/nutrition-plans/{plan_id}
Delete a nutrition plan and all related data.

**Authentication**: Required

**Path Parameters**:
| Parameter | Type | Description |
|-----------|------|-------------|
| plan_id | integer | Nutrition plan ID |

**Success Response** (200 OK):
```json
{
  "message": "Nutrition plan deleted successfully"
}
```

---

## 🔐 Authentication

All endpoints require JWT Bearer Token authentication:

```
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

Get token from:
- `POST /api/v1/auth/login` (email/password)
- `POST /api/v1/auth/telegram` (Telegram auth)

---

## 📊 Response Codes

| Code | Description |
|------|-------------|
| 200 | OK - Request succeeded |
| 201 | Created - Resource created successfully |
| 400 | Bad Request - Invalid input data |
| 401 | Unauthorized - Missing or invalid token |
| 403 | Forbidden - Not authorized to access resource |
| 404 | Not Found - Resource doesn't exist |
| 500 | Internal Server Error - Server error |

---

## 🎯 Data Models

### Workout Plan
- `plan_id`: Unique identifier
- `user_id`: Owner user ID
- `name`: Plan name
- `workout_goal_id`: Optional goal reference
- `total_weeks`: 1, 4, or 12
- `current_week`: Current week (1-12)
- `completed_weeks`: Array of completed week numbers
- `strategy`: JSONB AI-generated strategy
- `expectations`: JSONB AI-generated expectations
- `created_at`, `updated_at`: Timestamps

### Workout Week
- `week_id`: Unique identifier
- `plan_id`: Parent plan
- `week_number`: 1-12
- `title`: Week title
- `description`: Week description

### Workout Day
- `day_id`: Unique identifier
- `week_id`: Parent week
- `day_name`: Day of week
- `focus`: Training focus
- `warmup`: Warmup routine
- `cooldown`: Cooldown routine

### Workout Day Exercise
- `workout_day_exercise_id`: Unique identifier
- `day_id`: Parent day
- `exercise_id`: Reference to exercise table
- `sets`: Number of sets
- `reps`: Number of reps
- `tempo`: Tempo (e.g., "2-0-2-0")
- `rest`: Rest period
- `notes`: Additional notes
- `exercise_order`: Order in workout

### Nutrition Plan
- Similar structure to Workout Plan
- `nutrition_goal_id` instead of `workout_goal_id`

### Nutrition Week
- Similar structure to Workout Week

### Nutrition Day
- `day_id`: Unique identifier
- `week_id`: Parent week
- `day_name`: Day of week
- `daily_calories`: Target calories

### Meal
- `meal_id`: Unique identifier
- `day_id`: Parent day
- `meal_type`: breakfast, lunch, dinner, snacks
- `name`: Meal name
- `description`: Meal description
- `calories`: Meal calories
- `protein`, `carbs`, `fats`: Macronutrients (grams)

---

## 📚 Additional Resources

- **Full Implementation Guide**: `PHASE2_PHASE3_API_IMPLEMENTATION.md`
- **Testing Guide**: `TESTING_GUIDE.md`
- **Database Schema**: `workout_db_schema.sql`
- **Database Documentation**: `database_explanation.md`

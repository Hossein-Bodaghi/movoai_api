# Frontend Integration Guide

## Authentication

MovoAI uses **Telegram-only authentication** with two flows:

1. **Automatic Login** - User opens app from Telegram → Auto-authenticated
2. **Token Login** - User visits website → Gets token from `@MovoKioBot` → Enters token → Authenticated

---

## Implementation

### Flow 1: Automatic Login (from Telegram)

```javascript
// Include: <script src="https://telegram.org/js/telegram-web-app.js"></script>

if (window.Telegram?.WebApp) {
  const response = await fetch('https://movokio.com/api/v1/auth/telegram/auto-login', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({ init_data: window.Telegram.WebApp.initData })
  });
  
  const data = await response.json();
  localStorage.setItem('access_token', data.access_token);
  localStorage.setItem('refresh_token', data.refresh_token);
}
```

### Flow 2: Token Login (from web)

User gets token from `@MovoKioBot` by sending `/login`, then:

```javascript
const response = await fetch('https://movokio.com/api/v1/auth/telegram/verify-token', {
  method: 'POST',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify({ token: userToken.toUpperCase() })
});

const data = await response.json();
localStorage.setItem('access_token', data.access_token);
localStorage.setItem('refresh_token', data.refresh_token);
```

---

## Making API Calls

All requests need `Authorization: Bearer {access_token}` header:

```javascript
const response = await fetch('https://movokio.com/api/v1/users/me', {
  headers: { 'Authorization': `Bearer ${localStorage.getItem('access_token')}` }
});
```

### Token Refresh (access token expires in 15min)

```javascript
const response = await fetch('https://movokio.com/api/v1/auth/refresh', {
  method: 'POST',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify({ refresh_token: localStorage.getItem('refresh_token') })
});

const data = await response.json();
localStorage.setItem('access_token', data.access_token);
localStorage.setItem('refresh_token', data.refresh_token);
```

---

## User Endpoints

### Get Profile
```javascript
GET /api/v1/users/me
// Returns full user profile with workout_goal and nutrition_goal details
```

### Update Profile
```javascript
PUT /api/v1/users/me
Body: {
  "age": 25, "weight": 70, "height": 175, "gender": "male",
  "focus": "performance_enhancement", "physical_fitness": "intermediate", "fitness_days": 5,
  "workout_goal_id": 1, "nutrition_goal_id": 5,
  "sport": "running", "sport_days": 3, "specialized_sport": "marathon",
  "training_location": "gym", "workout_limitations": "knee injury",
  "dietary_restrictions": "lactose intolerant", "cooking_time": "30_60", "cooking_skill": "intermediate",
  "kitchen_appliances": "oven,microwave", "food_preferences": "chicken,rice", "forbidden_ingredients": "dairy,nuts"
}
// All fields optional
```

### Delete Account
```javascript
DELETE /api/v1/users/me
```

---

## Goal Endpoints

### List Workout Goals
```javascript
GET /api/v1/goals/workout?focus=performance_enhancement
// Returns: [{ workout_goal_id, focus, goal_key, goal_label_en, goal_label_fa, description_en, description_fa }]
// focus filter optional: performance_enhancement, body_recomposition, efficiency, rebuilding_rehab
```

### List Nutrition Goals
```javascript
GET /api/v1/goals/nutrition?focus=body_recomposition
// Returns: [{ nutrition_goal_id, focus, goal_key, goal_label_en, goal_label_fa, description_en, description_fa }]
```

### Get Specific Goal
```javascript
GET /api/v1/goals/workout/{id}
GET /api/v1/goals/nutrition/{id}
```

---

---

## Workout Plans

### Create Plan
```javascript
POST /api/v1/workout-plans
Body: { "name": "12-Week Program", "workout_goal_id": 1, "total_weeks": 12 }
// total_weeks: 1, 4, or 12
// Returns: Complete plan with all weeks/days/exercises + AI strategy/expectations
```

### List Plans
```javascript
GET /api/v1/workout-plans
// Returns: { plans: [...], total: 5 }
```

### Get Plan Details
```javascript
GET /api/v1/workout-plans/{plan_id}
// Returns: Full nested structure (weeks → days → exercises)
```

### Get Specific Week
```javascript
GET /api/v1/workout-plans/{plan_id}/week/{week_number}
// Returns: Single week with all workout days
```

### Update Plan
```javascript
PUT /api/v1/workout-plans/{plan_id}
Body: { "name": "New Name", "current_week": 3 }
```

### Complete Week
```javascript
POST /api/v1/workout-plans/{plan_id}/complete-week
Body: { "week_number": 2 }
// Marks week complete, advances current_week
```

### Delete Plan
```javascript
DELETE /api/v1/workout-plans/{plan_id}
```

---

## Nutrition Plans

### Create Plan
```javascript
POST /api/v1/nutrition-plans
Body: { "name": "4-Week Clean Eating", "nutrition_goal_id": 5, "total_weeks": 4 }
// Returns: Complete plan with all weeks/days/meals + AI strategy/expectations
```

### List Plans
```javascript
GET /api/v1/nutrition-plans
```

### Get Plan Details
```javascript
GET /api/v1/nutrition-plans/{plan_id}
// Returns: Full nested structure (weeks → days → meals with macros)
```

### Get Specific Week
```javascript
GET /api/v1/nutrition-plans/{plan_id}/week/{week_number}
// Returns: 7 days × 4 meals with calories/protein/carbs/fats
```

### Update Plan
```javascript
PUT /api/v1/nutrition-plans/{plan_id}
Body: { "name": "New Name", "current_week": 2 }
```

### Complete Week
```javascript
POST /api/v1/nutrition-plans/{plan_id}/complete-week
Body: { "week_number": 1 }
```

### Delete Plan
```javascript
DELETE /api/v1/nutrition-plans/{plan_id}
```

---

## Response Examples

### Workout Plan
```javascript
{
  "plan_id": 1, "name": "Strength Program", "total_weeks": 12, "current_week": 1,
  "completed_weeks": [], "strategy": {...}, "expectations": {...},
  "weeks": [{
    "week_number": 1, "title": "Week 1: Foundation",
    "days": [{
      "day_name": "Monday", "focus": "Upper Body",
      "exercises": [{
        "exercise_id": 42, "sets": "4", "reps": "10", "tempo": "2-0-2-0",
        "rest": "75 seconds", "exercise_order": 1,
        "exercise": { "name_en": "Bench Press", "name_fa": "..." }
      }]
    }]
  }]
}
```

### Nutrition Plan
```javascript
{
  "plan_id": 1, "name": "Clean Eating", "total_weeks": 4,
  "strategy": { "calorie_target": 2450, "macro_split": {...} },
  "weeks": [{
    "week_number": 1,
    "days": [{
      "day_name": "Monday", "daily_calories": 2450,
      "meals": [{
        "meal_type": "breakfast", "name": "Greek Yogurt Parfait",
        "calories": 613, "protein": 45.9, "carbs": 61.3, "fats": 20.4
      }]
    }]
  }]
}
```

---

## Key Points

- **Tokens**: Access (15min), Refresh (30 days), Login (5min, single-use)
- **Rate limits**: 3 login codes/hour, 3 verification attempts/token
- **Error 401**: Refresh token, then retry
- **Bot**: `@MovoKioBot` - user sends `/login` to get code
- **Plans**: Create once, AI generates all content (weeks/days/exercises/meals)
- **Progress**: Track via `current_week` and `completed_weeks[]`

See `examples/telegram_login.html` for working example.

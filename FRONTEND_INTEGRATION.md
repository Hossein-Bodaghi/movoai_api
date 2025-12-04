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
// Returns full user profile with workout_goal, nutrition_goal, and home_equipment details
// home_equipment is an array of equipment objects: [{ equipment_id, name_en, name_fa }]
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
  "home_equipment": [1, 5, 8, 12],  // Array of equipment IDs user has at home
  "dietary_restrictions": "lactose intolerant", "cooking_time": "30_60", "cooking_skill": "intermediate",
  "kitchen_appliances": "oven,microwave", "food_preferences": "chicken,rice", "forbidden_ingredients": "dairy,nuts"
}
// All fields optional
// home_equipment: Pass array of equipment_id integers
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
Body: { "name": "برنامه تمرینی شخصی", "workout_goal_id": 1, "total_weeks": 12 }
// total_weeks: 1, 4, or 12
// Returns: Complete plan with all weeks/days/exercises
// strategy & expectations are plain text strings (Persian)
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
Body: { "name": "برنامه غذایی شخصی", "nutrition_goal_id": 5, "total_weeks": 4 }
// total_weeks: 1, 4, or 12
// Returns: Complete plan with all weeks/days/meals
// strategy & expectations are plain text strings (Persian)
// Week titles/descriptions are in Persian
// Day names are in Persian (شنبه, یکشنبه, دوشنبه, etc.)
// Meals are in Persian with calorie info (protein/carbs/fats are null)
```

### List Plans
```javascript
GET /api/v1/nutrition-plans
```

### Get Plan Details
```javascript
GET /api/v1/nutrition-plans/{plan_id}
// Returns: Full nested structure (weeks → days → meals)
// Note: protein/carbs/fats are null in current implementation
```

### Get Specific Week
```javascript
GET /api/v1/nutrition-plans/{plan_id}/week/{week_number}
// Returns: 7 days (Persian names) × 4 meals (breakfast/lunch/dinner/snacks)
// Each meal has: name, description, calories (protein/carbs/fats are null)
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
  "plan_id": 1, "name": "برنامه تمرینی شخصی", "total_weeks": 12, "current_week": 1,
  "completed_weeks": [],
  "strategy": "این برنامه تمرینی بر اساس اطلاعات پروفایل شما طراحی شده است. رویکرد این برنامه ترکیبی از تمرینات قدرتی و هوازی است که به صورت پیشرونده شدت پیدا می‌کند...",
  "expectations": "در پایان این برنامه، انتظار می‌رود که افزایش ۵-۸ کیلوگرم عضله خالص داشته باشید. همچنین قدرت شما در حرکات اصلی مانند اسکوات، بنچ پرس و ددلیفت به طور قابل توجهی افزایش خواهد یافت...",
  "weeks": [{
    "week_number": 1,
    "title": "ساختن پایه و آشنایی با تمرینات",
    "description": "در هفته اول، تمرکز ما بر روی یادگیری فرم صحیح حرکات و آماده‌سازی بدن برای تمرینات سنگین‌تر است...",
    "days": [{
      "day_name": "شنبه",
      "focus": "سینه و سه‌سر",
      "exercises": [{
        "exercise_id": 42, "sets": "4", "reps": "10", "tempo": "2-0-2-0",
        "rest": "75 ثانیه", "exercise_order": 1,
        "exercise": {
          "name_en": "Bench Press",
          "name_fa": "پرس سینه با بار آزاد",
          "difficulty": { "difficulty_id": 2, "name_fa": "متوسط" },
          "instructions_fa": ["مرحله 1: روی نیمکت دراز بکشید", "مرحله 2: هالتر را بگیرید"],
          "male_urls": ["https://example.com/video1.mp4"],
          "male_image_urls": ["https://example.com/image1.jpg"],
          "equipment": [{ "equipment_id": 5, "name_fa": "هالتر" }],
          "muscles": [
            { "muscle_id": 12, "name_fa": "سینه" },
            { "muscle_id": 8, "name_fa": "سه سر بازو" }
          ]
        }
      }]
    }]
  }]
}
```

### Nutrition Plan
```javascript
{
  "plan_id": 1, "name": "برنامه غذایی شخصی", "total_weeks": 4,
  "strategy": "این برنامه غذایی بر اساس نیازهای کالری و اهداف شما طراحی شده است. استراتژی این برنامه تنظیم ماکروها به صورت متعادل و استفاده از منابع غذایی تمیز است...",
  "expectations": "با پیروی از این برنامه غذایی، انتظار می‌رود در ۱۲ هفته بین ۶ تا ۱۰ کیلوگرم کاهش وزن داشته باشید (بسته به وزن اولیه). افزایش انرژی و بهبود کیفیت خواب از هفته اول محسوس خواهد بود...",
  "weeks": [{
    "week_number": 1,
    "title": "شروع سفر تغذیه سالم",
    "description": "هفته اول درباره عادت کردن به برنامه جدید است. **تمرکز غذایی:** آشنایی با اندازه پورشن‌ها و تنظیم کالری روزانه...",
    "days": [{
      "day_name": "شنبه",
      "daily_calories": 2050,
      "meals": [{
        "meal_type": "breakfast",
        "name": "املت گوجه و قارچ",
        "description": "سه عدد تخم‌مرغ را با گوجه فرنگی خرد شده و قارچ تفت داده شده مخلوط کرده و در تابه بپزید...",
        "calories": 450,
        "protein": null,
        "carbs": null,
        "fats": null
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
- **Language**: All mock data is in Persian (Farsi)
  - Workout: Persian day names (شنبه-جمعه), week titles/descriptions
  - Nutrition: Persian day names, meal names, Persian week titles/descriptions
  - Strategy & Expectations: Plain text strings (not objects with title/description)
- **Exercise Data**: Each exercise includes:
  - `name_fa`: Persian name
  - `difficulty`: Object with `name_fa` (difficulty in Persian)
  - `instructions_fa`: Array of instruction steps in Persian
  - `male_urls`: Array of video URLs for male demonstration
  - `male_image_urls`: Array of image URLs for male demonstration
  - `equipment`: Array of equipment objects with `name_fa`
  - `muscles`: Array of muscle objects with `name_fa`

See `examples/telegram_login.html` for working example.

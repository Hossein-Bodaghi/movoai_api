# Farsi Workout Generator - Two-Agent System Architecture

## System Overview
This system uses two specialized AI agents:
1. **Strategist Agent**: Creates comprehensive 12-week training strategy (runs once)
2. **Plan Generator Agent**: Builds weekly workout plans based on strategy + feedback (runs weekly)

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         USER REQUEST                                     │
│                 POST /api/v1/workout-plans                              │
│          { name, total_weeks=12, workout_goal_id }                      │
└─────────────────────────────┬───────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                 WORKOUT PLANS ENDPOINT                                   │
│           app/api/v1/endpoints/workout_plans.py                         │
│                                                                          │
│  1. Authenticate user                                                    │
│  2. Fetch user profile from database                                    │
│  3. Get equipment IDs (home/gym based on location)                      │
│  4. Prepare user profile dictionary                                     │
│  5. Check if plan has strategy (if not, call Strategist Agent)          │
│  6. Call Plan Generator for next week                                   │
└─────────────────────────────┬───────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                    PHASE 1: STRATEGIST AGENT                             │
│                  ai/workout_strategist.py                               │
│                 (Runs ONCE at plan creation)                            │
│                                                                          │
│  Input: User Profile                                                     │
│  ┌────────────────────────────────────────────────────┐                │
│  │ - Age, Weight, Height, Gender                      │                │
│  │ - Fitness Level (beginner/intermediate/advanced)   │                │
│  │ - Workout Goal (build_muscle/lose_weight/etc)      │                │
│  │ - Training Days per Week (3-6)                     │                │
│  │ - Available Equipment                              │                │
│  │ - Limitations, Specialized Sport                   │                │
│  └────────────────────────────────────────────────────┘                │
│                              │                                           │
│                              ▼                                           │
│  ┌────────────────────────────────────────────────────┐                │
│  │  AVALAI API Call (Gemini 2.5 Pro)                  │                │
│  │                                                    │                │
│  │  System Prompt:                                    │                │
│  │  "شما یک استراتژیست حرفه‌ای تناسب اندام هستید"     │                │
│  │  "برای ۱۲ هفته آینده استراتژی ایجاد کنید"         │                │
│  │                                                    │                │
│  │  User Prompt:                                      │                │
│  │  "پروفایل کاربر: [user details]"                  │                │
│  │  "استراتژی ۱۲ هفته‌ای با ۳ خروجی تولید کنید:"     │                │
│  │    1. detailed_strategy (for AI generator)        │                │
│  │    2. user_summary (concise for user)             │                │
│  │    3. expectations (realistic outcomes)           │                │
│  └────────────────────────────────────────────────────┘                │
│                              │                                           │
│                              ▼                                           │
│  Output (JSON):                                                          │
│  ┌────────────────────────────────────────────────────┐                │
│  │ {                                                  │                │
│  │   "detailed_strategy": "هفته ۱-۳: فاز آشنایی..."  │                │
│  │       (Technical details for Plan Generator)       │                │
│  │                                                    │                │
│  │   "user_summary": "برنامه شما ۳ فاز دارد..."       │                │
│  │       (User-friendly explanation)                  │                │
│  │                                                    │                │
│  │   "expectations": "در ۱۲ هفته انتظار دارید..."    │                │
│  │       (Realistic outcomes & milestones)            │                │
│  │ }                                                  │                │
│  └────────────────────────────────────────────────────┘                │
│                              │                                           │
│                              │ Save to WorkoutPlan table                │
│                              ▼                                           │
│  ┌────────────────────────────────────────────────────┐                │
│  │ Database: workout_plan                             │                │
│  │  - detailed_strategy (TEXT) → for generator       │                │
│  │  - strategy (TEXT) → user_summary                 │                │
│  │  - expectations (TEXT) → expectations             │                │
│  └────────────────────────────────────────────────────┘                │
└─────────────────────────────┬───────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                  PHASE 2: PLAN GENERATOR AGENT                           │
│              ai/workout_generator_farsi.py                              │
│              (Runs WEEKLY for next week plan)                           │
│                                                                          │
│  Input:                                                                  │
│  ┌────────────────────────────────────────────────────┐                │
│  │ 1. User Profile                                    │                │
│  │ 2. Detailed Strategy (from Strategist)             │                │
│  │ 3. Current Week Number (1-12)                      │                │
│  │ 4. Previous Week Plan + Feedback (if week > 1)    │                │
│  └────────────────────────────────────────────────────┘                │
│                              │                                           │
│                              ▼                                           │
│  ┌────────────────────────────────────────────────────┐                │
│  │  1. FarsiExerciseSearchEngine                      │                │
│  │     - Map fitness level → difficulty               │                │
│  │     - Get weekly split from strategy               │                │
│  │     - Search exercises for each day                │                │
│  └────────────────────────────────────────────────────┘                │
│                              │                                           │
│                              ▼                                           │
│  ┌────────────────────────────────────────────────────┐                │
│  │  SQL QUERIES TO workout_db                         │                │
│  │                                                    │                │
│  │  SELECT exercises WHERE:                           │                │
│  │    - difficulty = user's fitness level             │                │
│  │    - equipment IN user's equipment list            │                │
│  │    - muscle_groups = target muscles for day        │                │
│  │                                                    │                │
│  │  Returns: exercise_id, name_fa, instructions_fa   │                │
│  └────────────────────────────────────────────────────┘                │
│                              │                                           │
│                              ▼                                           │
│  ┌────────────────────────────────────────────────────┐                │
│  │  2. AVALAI API Call (Gemini 2.5 Pro)               │                │
│  │                                                    │                │
│  │  System Prompt:                                    │                │
│  │  "شما یک برنامه‌ریز تمرینی هفتگی هستید"            │                │
│  │                                                    │                │
│  │  User Prompt:                                      │                │
│  │  "استراتژی کلی: [detailed_strategy]"              │                │
│  │  "هفته فعلی: [week_number]/12"                    │                │
│  │  "هفته قبل: [previous_week_plan]"                 │                │
│  │  "بازخورد: [feedback]"                            │                │
│  │  "تمرینات موجود: [exercises]"                     │                │
│  │                                                    │                │
│  │  "برای هفته [N] برنامه تولید کنید با:"            │                │
│  │    - week_note (توضیح هدف هفته)                   │                │
│  │    - exercises (بدون tempo و notes)               │                │
│  └────────────────────────────────────────────────────┘                │
│                              │                                           │
│                              ▼                                           │
│  Output (JSON):                                                          │
│  ┌────────────────────────────────────────────────────┐                │
│  │ {                                                  │                │
│  │   "week_note": "این هفته روی قدرت پایه..."         │                │
│  │   "days": [                                        │                │
│  │     {                                              │                │
│  │       "day_name": "شنبه",                          │                │
│  │       "focus": "سینه و شانه",                      │                │
│  │       "warmup": "۵-۱۰ دقیقه کشش پویا",             │                │
│  │       "cooldown": "۵ دقیقه کشش ایستا",             │                │
│  │       "exercises": [                               │                │
│  │         {                                          │                │
│  │           "exercise_id": 123,                      │                │
│  │           "sets": "3",                             │                │
│  │           "reps": "10-12",                         │                │
│  │           "rest": "60 ثانیه",                      │                │
│  │           "exercise_order": 1                      │                │
│  │         }                                          │                │
│  │       ]                                            │                │
│  │     }                                              │                │
│  │   ]                                                │                │
│  │ }                                                  │                │
│  └────────────────────────────────────────────────────┘                │
└─────────────────────────────┬───────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                    DATABASE PERSISTENCE                                  │
│                         workout_db                                       │
│                                                                          │
│  Create/Update records:                                                 │
│  ┌────────────────────────────────────────────────────────┐            │
│  │  WorkoutPlan                                           │            │
│  │    ├── detailed_strategy (Technical, for AI)          │            │
│  │    ├── strategy (User-friendly summary)               │            │
│  │    └── expectations (Realistic outcomes)              │            │
│  │         │                                             │            │
│  │         └── WorkoutWeek (week_number=N)               │            │
│  │              ├── week_note (هدف این هفته...)          │            │
│  │              │                                         │            │
│  │              └── WorkoutDay (شنبه)                    │            │
│  │                   ├── focus                           │            │
│  │                   ├── warmup                          │            │
│  │                   ├── cooldown                        │            │
│  │                   │                                   │            │
│  │                   └── WorkoutDayExercise              │            │
│  │                        ├── exercise_id                │            │
│  │                        ├── sets                       │            │
│  │                        ├── reps                       │            │
│  │                        ├── rest                       │            │
│  │                        └── exercise_order             │            │
│  │                           (NO tempo, NO notes)        │            │
│  └────────────────────────────────────────────────────────┘            │
└─────────────────────────────┬───────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                         RESPONSE TO USER                                 │
│                                                                          │
│  {                                                                       │
│    "plan_id": 123,                                                       │
│    "name": "برنامه تمرینی من",                                          │
│    "total_weeks": 12,                                                    │
│    "current_week": 1,                                                    │
│    "strategy": "برنامه شما شامل ۳ فاز است...",                          │
│    "expectations": "در ۱۲ هفته انتظار دارید...",                        │
│    "weeks": [                                                            │
│      {                                                                   │
│        "week_number": 1,                                                 │
│        "week_note": "این هفته روی ساختن پایه...",                       │
│        "days": [                                                         │
│          {                                                               │
│            "day_name": "شنبه",                                           │
│            "focus": "سینه و شانه",                                       │
│            "exercises": [                                                │
│              {                                                           │
│                "exercise_id": 123,                                       │
│                "sets": "3",                                              │
│                "reps": "10-12",                                          │
│                "rest": "60 ثانیه"                                        │
│              }                                                           │
│            ]                                                             │
│          }                                                               │
│        ]                                                                 │
│      }                                                                   │
│    ]                                                                     │
│  }                                                                       │
└─────────────────────────────────────────────────────────────────────────┘


═══════════════════════════════════════════════════════════════════════════
                              DATA FLOW EXAMPLE
═══════════════════════════════════════════════════════════════════════════

═══════ STEP 1: STRATEGIST AGENT (Runs Once) ═══════

User Profile Input:
  - Age: 28
  - Weight: 75 kg
  - Height: 175 cm
  - Gender: Male
  - Fitness: intermediate
  - Training: 4 days/week
  - Location: gym
  - Equipment: [Dumbbells, Barbell, Cables]
  - Goal: build_muscle
  - Limitations: None

     ↓

Strategist Agent Analyzes:
  - Current fitness level
  - Goal requirements (muscle building needs 12 weeks minimum)
  - Progressive overload requirements
  - Recovery needs

     ↓

Strategist Agent Outputs:

1. detailed_strategy (for Plan Generator AI):
   "هفته ۱-۳: فاز آشنایی و ساختن پایه
    - تمرکز: حرکات کامپوند پایه (اسکوات، بنچ، ددلیفت، روئینگ)
    - شدت: ۶۵-۷۰٪ 1RM
    - حجم: ۳ ست × ۸-۱۲ تکرار
    - تفکیک: Upper/Lower Split
    
    هفته ۴-۸: فاز هایپرتروفی
    - افزایش حجم تمرینات
    - معرفی تمرینات ایزوله
    - شدت: ۷۰-۷۵٪ 1RM
    - حجم: ۴ ست × ۸-۱۲ تکرار
    - تفکیک: Push/Pull/Legs
    
    هفته ۹-۱۲: فاز قدرت و تثبیت
    - تمرکز بر قدرت
    - شدت: ۷۵-۸۰٪ 1RM
    - حجم: ۴ ست × ۶-۸ تکرار
    - حفظ تفکیک Push/Pull/Legs"

2. user_summary (shown to user):
   "برنامه شما به ۳ فاز تقسیم شده است. در ۴ هفته اول، 
    پایه‌های اصلی را یاد می‌گیرید. هفته‌های ۵-۸ روی رشد 
    عضلانی تمرکز دارند. و هفته‌های ۹-۱۲ قدرت شما را 
    به حداکثر می‌رسانند."

3. expectations (realistic outcomes):
   "در پایان این برنامه ۱۲ هفته‌ای:
    - افزایش ۳-۵ کیلوگرم عضله خالص
    - افزایش ۲۰-۳۰٪ قدرت در حرکات اصلی
    - بهبود قابل توجه در فرم و تکنیک
    - تغییرات ظاهری از هفته ۶ به بعد
    - افزایش استقامت عضلانی"

     ↓

Saved to Database (WorkoutPlan):
  - detailed_strategy: [full technical strategy]
  - strategy: [user_summary]
  - expectations: [realistic expectations]


═══════ STEP 2: PLAN GENERATOR (Week 1) ═══════

Inputs to Plan Generator:
  - User Profile (same as above)
  - detailed_strategy (from Strategist)
  - week_number: 1
  - previous_week_plan: null (first week)
  - feedback: null (first week)

     ↓

Plan Generator Analyzes Strategy:
  "Week 1 is in Phase 1 (آشنایی و ساختن پایه)
   Focus: Compound movements
   Split: Upper/Lower for 4 days
   Intensity: 65-70% 1RM
   Volume: 3 sets × 8-12 reps"

     ↓

Weekly Split for Week 1:
  - Day 1 (شنبه): Upper Body - Push Focus
  - Day 2 (یکشنبه): Lower Body - Quads & Glutes
  - Day 3 (دوشنبه): Upper Body - Pull Focus
  - Day 4 (چهارشنبه): Lower Body - Hamstrings & Glutes

     ↓

Exercise Search (for Day 1 - Upper Push):
  - Search DB for: difficulty=Novice, muscle_groups=['Chest','Shoulders']
  - Equipment: Dumbbells, Barbell, Cables
  - Found: 35 exercises

     ↓

AvalAI Plan Generator Selects (Day 1):
  - 5 main exercises (bench press, shoulder press, incline flies, etc.)
  - Sets: 3 per exercise
  - Reps: 8-12 (progressive)
  - Rest: 90 seconds
  - NO tempo, NO exercise notes

     ↓

Week 1 Generated Output:
  {
    "week_note": "این هفته اول برنامه شماست. تمرکز اصلی بر یادگیری 
                  فرم صحیح حرکات پایه و آماده‌سازی بدن برای تمرینات 
                  سنگین‌تر است. وزنه‌ها را سبک انتخاب کنید.",
    "days": [4 workout days with exercises]
  }

     ↓

Database Records Created (Week 1):
  - 1 WorkoutWeek (week_number=1, week_note=...)
  - 4 WorkoutDays
  - ~20 WorkoutDayExercises (5 exercises × 4 days)
    - Each has: exercise_id, sets, reps, rest, exercise_order
    - NO tempo field, NO notes field


═══════ STEP 3: PLAN GENERATOR (Week 2+) ═══════

After user completes Week 1 and provides feedback...

Inputs to Plan Generator:
  - User Profile
  - detailed_strategy (same)
  - week_number: 2
  - previous_week_plan: [Week 1 exercises, sets, reps]
  - feedback: "تمرینات سینه خیلی راحت بود، می‌توانم وزن بیشتری بزنم"

     ↓

Plan Generator Analyzes:
  - Still in Phase 1 (weeks 1-4)
  - User feedback indicates ready for progression
  - Increase weight/intensity slightly
  - Maintain form focus

     ↓

Week 2 Adjustments:
  - Same exercises (for consistency in Phase 1)
  - Suggested weight increase: +2.5kg chest exercises
  - Reps: 8-12 (same range)
  - Sets: 3 (same)

     ↓

Week 2 Generated with Feedback Integration:
  {
    "week_note": "هفته دوم: بر اساس پیشرفت شما، وزنه‌های تمرینات 
                  سینه را کمی افزایش دهید. همچنان فرم را رعایت کنید.",
    "days": [adjusted workout days]
  }


═══════ WEEKLY PROGRESSION EXAMPLE ═══════

Week 1: Learn form, 3×8-12, light weight
Week 2: Same exercises, slightly heavier
Week 3: Same exercises, add 1 rep or weight
Week 4: Deload week (reduce intensity)

Week 5: NEW SPLIT (Push/Pull/Legs), new exercises
Week 6: Volume increase (4 sets)
Week 7-8: Continue hypertrophy focus

Week 9: Strength focus begins (4×6-8)
Week 10-11: Peak strength
Week 12: Deload + assessment


═══════════════════════════════════════════════════════════════════════════
                           ERROR HANDLING FLOW
═══════════════════════════════════════════════════════════════════════════

══════ STRATEGIST AGENT ERROR HANDLING ══════

AvalAI API Call (Strategist)
     │
     ├──[Success]──► Parse JSON ──► Validate 3 outputs ──► Return
     │
     ├──[Timeout]──► Retry (attempt 2/3)
     │                    │
     │                    ├──[Success]──► Parse JSON ──► Return
     │                    └──[Fail]──► Retry (attempt 3/3)
     │                                     │
     │                                     └──[Fail]──► Fallback Strategy
     │
     └──[Invalid Response]──► Try parse markdown JSON
                                    │
                                    ├──[Success]──► Return
                                    └──[Fail]──► Fallback Strategy

Fallback Strategy (if AI fails):
  {
    "detailed_strategy": "برنامه ۱۲ هفته‌ای استاندارد برای [goal]
                          هفته ۱-۴: فاز پایه‌سازی
                          هفته ۵-۸: فاز رشد
                          هفته ۹-۱۲: فاز قدرت",
    "user_summary": "برنامه شما شامل ۳ فاز است که به تدریج 
                     پیشرفت می‌کند.",
    "expectations": "با رعایت برنامه، در ۱۲ هفته پیشرفت 
                     قابل توجهی خواهید داشت."
  }


══════ PLAN GENERATOR ERROR HANDLING ══════

AvalAI API Call (Plan Generator)
     │
     ├──[Success]──► Parse JSON ──► Validate week structure ──► Return
     │
     ├──[Timeout]──► Retry (attempt 2/3)
     │                    │
     │                    ├──[Success]──► Parse JSON ──► Return
     │                    └──[Fail]──► Retry (attempt 3/3)
     │                                     │
     │                                     └──[Fail]──► Fallback Week Plan
     │
     └──[Invalid Response]──► Try parse markdown JSON
                                    │
                                    ├──[Success]──► Return
                                    └──[Fail]──► Fallback Week Plan

Fallback Week Plan (if AI fails):
  {
    "week_note": "برنامه تمرینی هفته [N]",
    "days": [
      {
        "day_name": "شنبه",
        "focus": "تمرین کامل بدن",
        "warmup": "۵-۱۰ دقیقه کشش پویا و کاردیو سبک",
        "cooldown": "۵-۱۰ دقیقه کشش ایستا",
        "exercises": [
          // All exercises from search results
          // Standard: 3 sets, 10-12 reps, 60s rest
        ]
      }
    ]
  }


══════ VALIDATION RULES ══════

Strategist Output Validation:
  ✓ Must have 3 fields: detailed_strategy, user_summary, expectations
  ✓ detailed_strategy: minimum 200 characters (detailed enough)
  ✓ user_summary: 50-500 characters (concise)
  ✓ expectations: 50-500 characters (realistic)
  ✗ Reject if any field is missing or too short

Plan Generator Output Validation:
  ✓ Must have week_note (50+ characters)
  ✓ Must have days array with [fitness_days] elements
  ✓ Each day must have: day_name, focus, warmup, cooldown, exercises
  ✓ Each exercise must have: exercise_id, sets, reps, rest, exercise_order
  ✗ Reject if tempo or notes fields exist (removed in new design)
  ✗ Reject if exercise_id not in database


══════ FEEDBACK INTEGRATION FLOW ══════

User Completes Week → Provides Feedback
     │
     ├── "خیلی سخت بود" 
     │    → Next week: Reduce intensity/volume
     │
     ├── "خیلی راحت بود"
     │    → Next week: Increase weight/volume
     │
     ├── "درد زانو دارم"
     │    → Next week: Avoid knee-intensive exercises
     │
     └── "عالی بود"
          → Next week: Maintain progression as planned


══════ DATABASE TRANSACTION SAFETY ══════

Transaction Flow:
  BEGIN TRANSACTION
    1. Create/Update WorkoutPlan (with strategy fields)
    2. Create WorkoutWeek (with week_note)
    3. Create WorkoutDays
    4. Create WorkoutDayExercises
  COMMIT (if all succeed)
  ROLLBACK (if any step fails)

Ensures:
  - No partial plans in database
  - Consistent state
  - Easy recovery from failures
```

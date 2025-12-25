# Farsi Workout Generator - System Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         USER REQUEST                                     │
│                 POST /api/v1/workout-plans                              │
│          { name, total_weeks, workout_goal_id }                         │
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
└─────────────────────────────┬───────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────────────┐
│            FARSI WORKOUT PLAN GENERATOR                                  │
│              ai/workout_generator_farsi.py                              │
│                                                                          │
│  ┌────────────────────────────────────────────────────────┐            │
│  │  1. FarsiExerciseSearchEngine                          │            │
│  │     - Map fitness level → difficulty                   │            │
│  │     - Generate weekly split (based on training days)   │            │
│  │     - Search exercises for each day                    │            │
│  └────────────────────────────────────────────────────────┘            │
│                              │                                           │
│                              ▼                                           │
│  ┌────────────────────────────────────────────────────────┐            │
│  │  SQL QUERIES TO workout_db                             │            │
│  │                                                        │            │
│  │  SELECT exercises WHERE:                               │            │
│  │    - difficulty = user's fitness level                 │            │
│  │    - equipment IN user's equipment list                │            │
│  │    - muscle_groups = target muscles for day            │            │
│  │    - style = warmup/main/cooldown                      │            │
│  │                                                        │            │
│  │  Returns: exercise_id, name_fa, instructions_fa       │            │
│  └────────────────────────────────────────────────────────┘            │
│                              │                                           │
│                              ▼                                           │
│  ┌────────────────────────────────────────────────────────┐            │
│  │  2. FarsiWorkoutPlanGenerator                          │            │
│  │     - Organize exercises by day                        │            │
│  │     - Prepare Farsi prompts for AvalAI                 │            │
│  │     - Call AvalAI API                                  │            │
│  └────────────────────────────────────────────────────────┘            │
└─────────────────────────────┬───────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                      AVALAI GEMINI API                                   │
│              https://api.avalai.ir/v1beta/models/                       │
│                    gemini-2.5-pro:generateContent                       │
│                                                                          │
│  Input:                                                                  │
│  ┌──────────────────────────────────────────────────────┐              │
│  │ System: شما یک مربی تناسب اندام حرفه‌ای هستید...     │              │
│  │                                                      │              │
│  │ User: لطفاً برنامه تمرینی تولید کنید:                │              │
│  │   - اطلاعات کاربر: سن، وزن، قد، سطح...              │              │
│  │   - تمرینات موجود: [exercises from DB]              │              │
│  │   - فرمت خروجی: JSON                                │              │
│  └──────────────────────────────────────────────────────┘              │
│                              │                                           │
│                              ▼                                           │
│  Output (JSON):                                                          │
│  ┌──────────────────────────────────────────────────────┐              │
│  │ {                                                    │              │
│  │   "strategy": "استراتژی به فارسی...",              │              │
│  │   "expectations": "انتظارات به فارسی...",           │              │
│  │   "days": [                                          │              │
│  │     {                                                │              │
│  │       "day_name": "شنبه",                            │              │
│  │       "focus": "تمرین تمام بدن",                     │              │
│  │       "warmup": "...",                               │              │
│  │       "cooldown": "...",                             │              │
│  │       "exercises": [                                 │              │
│  │         {                                            │              │
│  │           "exercise_id": 123,                        │              │
│  │           "sets": "3",                               │              │
│  │           "reps": "10-12",                           │              │
│  │           "tempo": "2-0-2-0",                        │              │
│  │           "rest": "60 ثانیه",                        │              │
│  │           "notes": "...",                            │              │
│  │           "exercise_order": 1                        │              │
│  │         }                                            │              │
│  │       ]                                              │              │
│  │     }                                                │              │
│  │   ]                                                  │              │
│  │ }                                                    │              │
│  └──────────────────────────────────────────────────────┘              │
└─────────────────────────────┬───────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                    DATABASE PERSISTENCE                                  │
│                         workout_db                                       │
│                                                                          │
│  Create records:                                                         │
│  ┌────────────────────────────────────────────────────────┐            │
│  │  WorkoutPlan                                           │            │
│  │    ├── strategy (from AI)                             │            │
│  │    └── expectations (from AI)                         │            │
│  │         │                                             │            │
│  │         └── WorkoutWeek (week_number=1)               │            │
│  │              │                                         │            │
│  │              └── WorkoutDay (شنبه)                    │            │
│  │                   ├── focus (from AI)                 │            │
│  │                   ├── warmup (from AI)                │            │
│  │                   ├── cooldown (from AI)              │            │
│  │                   │                                   │            │
│  │                   └── WorkoutDayExercise              │            │
│  │                        ├── exercise_id (from AI)      │            │
│  │                        ├── sets (from AI)             │            │
│  │                        ├── reps (from AI)             │            │
│  │                        ├── tempo (from AI)            │            │
│  │                        ├── rest (from AI)             │            │
│  │                        └── notes (from AI)            │            │
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
│    "strategy": "استراتژی کلی...",                                       │
│    "expectations": "انتظارات...",                                       │
│    "weeks": [                                                            │
│      {                                                                   │
│        "week_number": 1,                                                 │
│        "days": [                                                         │
│          {                                                               │
│            "day_name": "شنبه",                                           │
│            "exercises": [...]                                            │
│          }                                                               │
│        ]                                                                 │
│      }                                                                   │
│    ]                                                                     │
│  }                                                                       │
└─────────────────────────────────────────────────────────────────────────┘


═══════════════════════════════════════════════════════════════════════════
                              DATA FLOW EXAMPLE
═══════════════════════════════════════════════════════════════════════════

User Profile:
  - Age: 28
  - Weight: 75 kg
  - Height: 175 cm
  - Fitness: intermediate
  - Training: 4 days/week
  - Location: gym
  - Equipment: [Dumbbells, Barbell, Cables]

     ↓

Weekly Split Generated:
  - Day 1 (شنبه): Upper Push (Chest, Shoulders)
  - Day 2 (یکشنبه): Lower (Legs, Glutes)
  - Day 3 (دوشنبه): Upper Pull (Back, Arms)
  - Day 4 (چهارشنبه): Full Body

     ↓

Exercise Search (for Day 1):
  - Warmup: 10 stretching exercises (difficulty=Novice)
  - Main: 30 chest/shoulder exercises (difficulty=Novice, equipment=[2,3,5])
  - Cooldown: 10 stretching exercises

     ↓

AvalAI Selection (for Day 1):
  - Warmup: 2-3 exercises
  - Main: 5 exercises (bench press, shoulder press, flies, etc.)
  - Cooldown: 2-3 exercises
  - Sets: 3-4
  - Reps: 8-12
  - Tempo: 2-0-2-0
  - Rest: 60-90 seconds

     ↓

Database Records Created:
  - 1 WorkoutPlan
  - 1 WorkoutWeek
  - 4 WorkoutDays
  - ~20 WorkoutDayExercises (5 exercises × 4 days)


═══════════════════════════════════════════════════════════════════════════
                           ERROR HANDLING FLOW
═══════════════════════════════════════════════════════════════════════════

AvalAI API Call
     │
     ├──[Success]──► Parse JSON ──► Return structured plan
     │
     ├──[Timeout]──► Retry (attempt 2/3)
     │                    │
     │                    ├──[Success]──► Parse JSON ──► Return
     │                    └──[Fail]──► Retry (attempt 3/3)
     │                                     │
     │                                     └──[Fail]──► Fallback Plan
     │
     └──[Invalid Response]──► Try parse markdown JSON
                                    │
                                    ├──[Success]──► Return
                                    └──[Fail]──► Fallback Plan

Fallback Plan:
  - Basic strategy text in Farsi
  - Generic expectations
  - All exercises from search results
  - Standard sets: 3
  - Standard reps: 10-12
  - Standard rest: 60 seconds
```

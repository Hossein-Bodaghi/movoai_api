# Workout Database (workout_db)

A comprehensive PostgreSQL relational database designed to power AI-driven fitness applications with complete user management, workout/nutrition plan generation, and feedback collection capabilities.

## Overview

The `workout_db` combines a normalized exercise corpus with a complete fitness application backend. Built on a star/snowflake schema for the exercise data, it integrates user management, multi-week plan structures, credit systems, and feedback mechanisms to enable end-to-end AI-powered fitness coaching.

## Architecture

The database consists of two major subsystems:

1. **Exercise Knowledge Base**: Normalized exercise corpus with semantic search capabilities
2. **Application Backend**: User management, plan generation, and feedback collection

### Database Components (35 Tables Total)

#### Exercise Knowledge Base (17 tables)
- **1 Fact Table**: `exercise` (central entity)
- **9 Dimension Tables**: Lookup tables for categories
- **7 Junction Tables**: Many-to-many relationship resolvers

#### User Management & Goals (6 tables)
- **2 Goal Tables**: `workout_goals`, `nutrition_goals` (40 goals total)
- **4 User Tables**: `users`, `user_home_equipment`, `user_sessions`, `credit_transactions`

#### Workout Plan System (4 tables)
- **Plan Structure**: `workout_plans`, `workout_weeks`
- **Daily Structure**: `workout_days`, `workout_day_exercises`

#### Nutrition Plan System (4 tables)
- **Plan Structure**: `nutrition_plans`, `nutrition_weeks`
- **Daily Structure**: `nutrition_days`, `meals`

#### Feedback System (2 tables)
- **Questions & Responses**: `feedback_questions`, `feedback`

#### Vector Search (2 tables)
- **Embeddings**: `langchain_pg_collection`, `langchain_pg_embedding`

## Complete Schema Structure

### 1. Exercise Knowledge Base (Original Core)

#### Fact Table: `exercise`
The central table containing core exercise information.

| Column | Type | Description |
|--------|------|-------------|
| `exercise_id` | INT (PK) | Unique identifier from source CSV |
| `name_en` | TEXT | English exercise name |
| `name_fa` | TEXT | Farsi exercise name |
| `difficulty_id` | INT (FK) | Direct link to difficulty table |
| `style_id` | INT (FK) | Direct link to style table |
| `instructions_en` | TEXT[] | PostgreSQL array of English instruction steps |
| `instructions_fa` | TEXT[] | PostgreSQL array of Farsi instruction steps |
| `male_urls` | TEXT[] | Array of video URLs for male demonstrations |
| `female_urls` | TEXT[] | Array of video URLs for female demonstrations |
| `male_image_urls` | TEXT[] | Array of image URLs for male demonstrations |
| `female_image_urls` | TEXT[] | Array of image URLs for female demonstrations |
| `page_url` | TEXT | Source URL for the exercise |

#### Dimension Tables
Standardized lookup tables for exercise attributes:
- `difficulty`, `muscle`, `equipment`, `goal`, `training_phase`, `mechanics`, `force_pattern`, `position`, `style`

#### Junction Tables
Many-to-many relationships:
- `exercise_muscle`, `exercise_equipment`, `exercise_goal`, `exercise_training_phase`, `exercise_mechanics`, `exercise_force_pattern`, `exercise_position`

### 2. User Management & Goals (Phase 1)

#### `workout_goals` & `nutrition_goals`
Reference tables with 20 goals each (5 per focus area):
- **Focus Areas**: `performance_enhancement`, `body_recomposition`, `efficiency`, `rebuilding_rehab`
- **Attributes**: `goal_key` (unique), `goal_label_en`, `goal_label_fa`, `description`

#### `users`
Complete user profiles with:
- **Authentication**
- **Demographics**: age, weight, height, gender
- **Fitness Profile**: focus, physical_fitness, fitness_days, workout_goal_id, nutrition_goal_id
- **Training**: training_location (home/gym), workout_limitations
- **Nutrition**: dietary_restrictions, cooking_time, cooking_skill, kitchen_appliances[], food_preferences[], forbidden_ingredients[]
- **Credits**: credits, referral_code, has_used_referral

#### `user_home_equipment`
Junction table linking users to available equipment (references `equipment` table)

#### `user_sessions`
JWT authentication sessions with expiration tracking

#### `credit_transactions`
Audit trail for all credit operations:
- **Types**: `purchase`, `usage`, `referral`, `bonus`
- **Auto-trigger**: Updates user credits on insert

### 3. Workout Plan System (Phase 2)

#### `workout_plans`
Main workout plans with:
- **User Link**: `user_id` (FK to users, CASCADE delete)
- **Goal**: `workout_goal_id` (FK to workout_goals)
- **Duration**: `total_weeks` (1, 4, or 12 weeks)
- **Progress**: `current_week`, `completed_weeks[]` (array)
- **AI Content**: `strategy` (JSONB), `expectations` (JSONB)

#### `workout_weeks`
Weekly breakdowns within plans (unique per plan)

#### `workout_days`
Daily workouts with: `day_name`, `focus`, `warmup`, `cooldown`

#### `workout_day_exercises` ⭐ **Junction Table**
Links workout days to exercises with AI-generated parameters:
- **Exercise Reference**: `exercise_id` (FK to exercise table)
- **AI Parameters**: `sets`, `reps`, `tempo`, `rest`, `notes`, `exercise_order`
- **Ensures**: Data integrity via foreign key to exercise corpus

### 4. Nutrition Plan System (Phase 3)

#### `nutrition_plans`
Main nutrition plans (parallel structure to workout_plans):
- **User Link**: `user_id` (FK to users)
- **Goal**: `nutrition_goal_id` (FK to nutrition_goals)
- **Duration**: `total_weeks` (1, 4, or 12)
- **Progress**: `current_week`, `completed_weeks[]`
- **AI Content**: `strategy` (JSONB), `expectations` (JSONB)

#### `nutrition_weeks`
Weekly breakdowns within nutrition plans

#### `nutrition_days`
Daily meal plans with: `day_name`, `daily_calories`

#### `meals`
Individual meals (4 types: breakfast, lunch, dinner, snacks):
- **Macros**: `calories`, `protein`, `carbs`, `fats`
- **Details**: `name`, `description`

### 5. Feedback System (Phase 4)

#### `feedback_questions`
AI-generated questions with polymorphic week references:
- **Week Reference**: `week_table` ('workout_weeks' OR 'nutrition_weeks'), `week_id`
- **Question Types**: `radio`, `multi-select`
- **Options**: Static (JSONB) or dynamic ('exercises', 'meals')

#### `feedback`
User responses stored as JSONB:
- **Structure**: Array of `{question_id, answer, text_response}`
- **Week Reference**: Polymorphic (workout_weeks OR nutrition_weeks)

## Querying Guidelines

### Best Practices

1. **Use JOINs, not LIKE**: Filter using dimension tables, not text searches on exercise names
2. **Start with exercise table**: Begin queries from the central `exercise` table
3. **Join through junctions**: Use junction tables to connect to dimensions for many-to-many relationships
4. **Direct joins for one-to-many**: Use direct foreign key joins (like `difficulty_id`)

### Example Query

**Scenario**: Find all 'Intermediate' exercises for 'Strength' that target the 'Lats', use 'Dumbbells', and are 'Bodyweight' style

```sql
SELECT
    e.exercise_id,
    e.name_en,
    e.instructions_en,
    e.male_urls,
    s.name_en AS style_name
FROM
    exercise AS e
JOIN
    difficulty AS d ON e.difficulty_id = d.difficulty_id
JOIN
    style AS s ON e.style_id = s.style_id
JOIN
    exercise_goal AS eg ON e.exercise_id = eg.exercise_id
JOIN
    goal AS g ON eg.goal_id = g.goal_id
JOIN
    exercise_muscle AS em ON e.exercise_id = em.exercise_id
JOIN
    muscle AS m ON em.muscle_id = m.muscle_id
JOIN
    exercise_equipment AS ee ON e.exercise_id = ee.exercise_id
JOIN
    equipment AS eq ON ee.equipment_id = eq.equipment_id
WHERE
    d.name_en = 'Intermediate'
    AND g.name_en = 'Strength'
    AND m.name_en = 'Lats'
    AND eq.name_en = 'Dumbbell'
    AND s.name_en = 'Bodyweight';
```

## Files

- `schema.sql`: Database schema definition and table creation scripts
- `populate.py`: Data population script for migrating from CSV to PostgreSQL
- `extract.py`: Data extraction utilities
- `add_image_urls.py`: Script to populate image URLs from video URLs

## Benefits

### Exercise Corpus
- **Performance**: Normalized structure enables fast complex queries
- **Data Integrity**: Foreign key constraints prevent orphaned data
- **Scalability**: Easy to add new exercises and categories
- **Multilingual Support**: Built-in English/Farsi translation support
- **Flexibility**: Complex filtering combinations through junction tables

### Application Backend
- **User Management**: Complete authentication and profile system
- **Multi-User Support**: Each user can have multiple workout/nutrition plans
- **Progress Tracking**: Week-by-week completion tracking with arrays
- **Credit System**: Monetization-ready with referral support
- **AI Integration**: JSONB fields for flexible AI-generated content
- **Feedback Loop**: Collect user responses for plan optimization
- **Equipment Aware**: Home vs gym training with equipment tracking
- **Cascade Deletes**: Automatic cleanup of related data on user deletion
- **Polymorphic Design**: Shared feedback system for workout/nutrition
- **Audit Trail**: Complete transaction history for credits

## Vector Embeddings & Semantic Search

The database integrates with **PGVector** extension and **Google Gemini AI** to enable semantic exercise search capabilities.

### Vector Store Configuration

- **Model**: `gemini-embedding-001` (Google Generative AI)
- **Dimensions**: 3072 (default for gemini-embedding-001)
- **Task Type**: `retrieval_document` (optimized for document search)
- **Collection**: `exercise_embeddings_en` (English language)
- **Storage**: ~18 MB for 1,501 exercises

### Vectorized Exercise Attributes

Each exercise is embedded as a rich text description containing:

- Exercise name
- Style (e.g., Bodyweight, Weighted, Cardio)
- Difficulty level (Beginner, Intermediate, Advanced)
- Equipment required
- Target muscles
- Training goals
- Training phase

### Semantic Search Examples

**Natural Language Queries:**
- "beginner chest exercises" → Returns push-ups, incline push-ups, chest dips
- "advanced leg exercises with weights" → Returns barbell squats, deadlifts, lunges
- "bodyweight back training" → Returns pull-ups, inverted rows, back extensions

### Rate Limiting

Vector embedding generation uses rate limiting to stay within Google API quotas:
- **Batch Size**: 50 exercises per batch
- **Rate**: 2 batches per minute (30-second delays)
- **Total Time**: ~15 minutes for full database vectorization

### Implementation Details

The vectorization process:
1. Fetches all exercises with their specifications from PostgreSQL
2. Creates rich text descriptions for each exercise
3. Generates embeddings using Google's gemini-embedding-001
4. Stores vectors in PGVector with metadata for filtering
5. Enables similarity search based on semantic meaning

See `/langchain_ai/vectorize_exercises.py` for implementation.

## Complete Data Flow

```
User Registration & Authentication
    ↓
users (with workout_goal_id & nutrition_goal_id)
    ↓
    ├─→ user_home_equipment → equipment (from exercise DB)
    ├─→ user_sessions (JWT auth)
    ├─→ credit_transactions (purchase/usage tracking)
    │
    ├─→ workout_plans (multiple per user)
    │       ↓
    │   workout_weeks (1-12 weeks)
    │       ↓
    │   workout_days (daily workouts)
    │       ↓
    │   workout_day_exercises (junction with AI parameters)
    │       ↓
    │   exercise (references exercise corpus)
    │
    └─→ nutrition_plans (multiple per user)
            ↓
        nutrition_weeks (1-12 weeks)
            ↓
        nutrition_days (daily meals)
            ↓
        meals (breakfast/lunch/dinner/snacks with macros)

Feedback Collection (for both workout & nutrition)
    ↓
feedback_questions (polymorphic: workout_weeks OR nutrition_weeks)
    ↓
feedback (JSONB responses with text)
```

## Key Design Patterns

### 1. Polymorphic References
`feedback_questions` and `feedback` tables use a `week_table` column to reference either `workout_weeks` or `nutrition_weeks`, reducing table count while maintaining flexibility.

### 2. Junction Table with Attributes
`workout_day_exercises` properly links to the exercise corpus while storing AI-generated workout parameters (sets, reps, tempo, rest).

### 3. JSONB for AI Content
Strategy, expectations, and feedback responses use JSONB for flexible, evolving AI-generated content without schema migrations.

### 4. Progress Tracking
Plans track `current_week` and `completed_weeks[]` array for user progress through multi-week programs.

### 5. Credit System
Automatic credit updates via database triggers when transactions are inserted.

## Use Cases

### Original Exercise Corpus
- AI workout plan generation with semantic search
- Multi-criteria exercise filtering
- Natural language exercise queries
- Exercise recommendation systems

### Extended Application Features
- User registration and authentication (JWT)
- Personalized workout plan generation (1/4/12 weeks)
- Personalized nutrition plan generation (1/4/12 weeks)
- Equipment-based exercise filtering (home vs gym)
- Credit-based plan access with referral system
- Week-by-week feedback collection
- Progress tracking through multi-week programs
- Macro tracking and meal planning

## Getting Started

### Full Database Setup

1. **Create PostgreSQL Database**
   ```bash
   createdb workout_db
   ```

2. **Install PGVector Extension**
   ```sql
   CREATE EXTENSION vector;
   ```

3. **Run Schema Creation**
   ```bash
   psql -U postgres -d workout_db -f schema.sql
   ```

4. **Populate Exercise Data**
   ```bash
   python populate.py
   ```

5. **Populate Goal Tables** (Phase 1A)
   ```bash
   psql -U postgres -d workout_db -f structure/phase_1a_migration.sql
   ```

6. **Setup Vector Embeddings** (Optional)
   ```bash
   pip install langchain-google-genai langchain-community psycopg2
   export GOOGLE_API_KEY="your_api_key"
   python /langchain_ai/vectorize_exercises.py
   ```

### Database Verification

Check table count (should be 35 total):
```sql
SELECT COUNT(*) FROM information_schema.tables 
WHERE table_schema = 'public' AND table_type = 'BASE TABLE';
```

View all user plans:
```sql
SELECT u.email, 
       COUNT(DISTINCT wp.plan_id) as workout_plans,
       COUNT(DISTINCT np.plan_id) as nutrition_plans
FROM users u
LEFT JOIN workout_plans wp ON u.user_id = wp.user_id
LEFT JOIN nutrition_plans np ON u.user_id = np.user_id
GROUP BY u.user_id, u.email;
```

## Production Considerations

### Security
- User passwords stored as `password_hash` (bcrypt recommended)
- JWT tokens in `user_sessions` with expiration
- CASCADE deletes protect data integrity

### Performance
- Indexes on all foreign keys
- JSONB indexes for AI content queries
- Composite indexes on junction tables

### Scalability
- Multi-week plans (1, 4, or 12 weeks)
- Unlimited plans per user
- Polymorphic feedback reduces table count
- Array fields for flexible data storage

### Maintenance
- Trigger-based credit updates
- Automatic timestamp updates on user records
- Transaction audit trail for debugging

---

*This database is a production-ready backend for AI-powered fitness applications with complete user management, workout/nutrition plan generation, semantic exercise search, and feedback collection capabilities.*
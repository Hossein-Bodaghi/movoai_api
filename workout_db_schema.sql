-- 1. All lookup tables (our categories)
-- 0. DROP ALL TABLES (in reverse order of creation)
-- This makes the schema re-runnable for testing

-- Phase 4: Feedback System
DROP TABLE IF EXISTS feedback CASCADE;
DROP TABLE IF EXISTS feedback_questions CASCADE;

-- Phase 3: Nutrition Plans
DROP TABLE IF EXISTS meals CASCADE;
DROP TABLE IF EXISTS nutrition_days CASCADE;
DROP TABLE IF EXISTS nutrition_weeks CASCADE;
DROP TABLE IF EXISTS nutrition_plans CASCADE;

-- Phase 2: Workout Plans
DROP TABLE IF EXISTS workout_day_exercises CASCADE;
DROP TABLE IF EXISTS workout_days CASCADE;
DROP TABLE IF EXISTS workout_weeks CASCADE;
DROP TABLE IF EXISTS workout_plans CASCADE;

-- Phase 1: User Management & Goals
DROP TABLE IF EXISTS credit_transactions CASCADE;
DROP TABLE IF EXISTS user_sessions CASCADE;
DROP TABLE IF EXISTS user_home_equipment CASCADE;
DROP TABLE IF EXISTS users CASCADE;
DROP TABLE IF EXISTS nutrition_goals CASCADE;
DROP TABLE IF EXISTS workout_goals CASCADE;

-- Original Exercise Database
DROP TABLE IF EXISTS exercise_position CASCADE;
DROP TABLE IF EXISTS exercise_force_pattern CASCADE;
DROP TABLE IF EXISTS exercise_mechanics CASCADE;
DROP TABLE IF EXISTS exercise_training_phase CASCADE;
DROP TABLE IF EXISTS exercise_goal CASCADE;
DROP TABLE IF EXISTS exercise_equipment CASCADE;
DROP TABLE IF EXISTS exercise_muscle CASCADE;
DROP TABLE IF EXISTS exercise CASCADE;
DROP TABLE IF EXISTS position CASCADE;
DROP TABLE IF EXISTS force_pattern CASCADE;
DROP TABLE IF EXISTS mechanics CASCADE;
DROP TABLE IF EXISTS training_phase CASCADE;
DROP TABLE IF EXISTS goal CASCADE;
DROP TABLE IF EXISTS equipment CASCADE;
DROP TABLE IF EXISTS muscle CASCADE;
DROP TABLE IF EXISTS style CASCADE;
DROP TABLE IF EXISTS difficulty CASCADE;

-- 1. All lookup tables (our categories)
-- ... (rest of your schema.sql file) ...

CREATE TABLE difficulty (
    difficulty_id SERIAL PRIMARY KEY,
    name_en VARCHAR(100) UNIQUE NOT NULL,
    name_fa VARCHAR(100) NOT NULL
);

CREATE TABLE muscle (
    muscle_id SERIAL PRIMARY KEY,
    name_en VARCHAR(100) UNIQUE NOT NULL,
    name_fa VARCHAR(100) NOT NULL
);

CREATE TABLE equipment (
    equipment_id SERIAL PRIMARY KEY,
    name_en VARCHAR(100) UNIQUE NOT NULL,
    name_fa VARCHAR(100) NOT NULL
);

CREATE TABLE goal (
    goal_id SERIAL PRIMARY KEY,
    name_en VARCHAR(100) UNIQUE NOT NULL,
    name_fa VARCHAR(100) NOT NULL
);

CREATE TABLE training_phase (
    phase_id SERIAL PRIMARY KEY,
    name_en VARCHAR(100) UNIQUE NOT NULL,
    name_fa VARCHAR(100) NOT NULL
);

CREATE TABLE mechanics (
    mechanics_id SERIAL PRIMARY KEY,
    name_en VARCHAR(100) UNIQUE NOT NULL,
    name_fa VARCHAR(100) NOT NULL
);

CREATE TABLE force_pattern (
    pattern_id SERIAL PRIMARY KEY,
    name_en VARCHAR(100) UNIQUE NOT NULL,
    name_fa VARCHAR(100) NOT NULL
);

CREATE TABLE position (
    position_id SERIAL PRIMARY KEY,
    name_en VARCHAR(100) UNIQUE NOT NULL,
    name_fa VARCHAR(100) NOT NULL
);

CREATE TABLE style (
    style_id SERIAL PRIMARY KEY,
    name_en VARCHAR(100) UNIQUE NOT NULL,
    name_fa VARCHAR(100) NOT NULL
);

-- 2. The main exercise table

CREATE TABLE exercise (
    exercise_id INT PRIMARY KEY,         -- From your 'iden' column
    name_en TEXT NOT NULL,
    name_fa TEXT NOT NULL,
    
    -- NOTE: Difficulty is now a JSON tag, so we link it here
    difficulty_id INT REFERENCES difficulty(difficulty_id),
    
    -- Style is now a foreign key reference to the style lookup table
    style_id INT REFERENCES style(style_id),
    
    instructions_en TEXT[],
    instructions_fa TEXT[],
    
    page_url TEXT,
    
    male_urls TEXT[],
    female_urls TEXT[],
    male_image_urls TEXT[],
    female_image_urls TEXT[]
);

-- 3. All junction tables (many-to-many links)

CREATE TABLE exercise_muscle (
    exercise_id INT REFERENCES exercise(exercise_id) ON DELETE CASCADE,
    muscle_id INT REFERENCES muscle(muscle_id) ON DELETE CASCADE,
    PRIMARY KEY (exercise_id, muscle_id)
);

CREATE TABLE exercise_equipment (
    exercise_id INT REFERENCES exercise(exercise_id) ON DELETE CASCADE,
    equipment_id INT REFERENCES equipment(equipment_id) ON DELETE CASCADE,
    PRIMARY KEY (exercise_id, equipment_id)
);

CREATE TABLE exercise_goal (
    exercise_id INT REFERENCES exercise(exercise_id) ON DELETE CASCADE,
    goal_id INT REFERENCES goal(goal_id) ON DELETE CASCADE,
    PRIMARY KEY (exercise_id, goal_id)
);

CREATE TABLE exercise_training_phase (
    exercise_id INT REFERENCES exercise(exercise_id) ON DELETE CASCADE,
    phase_id INT REFERENCES training_phase(phase_id) ON DELETE CASCADE,
    PRIMARY KEY (exercise_id, phase_id)
);

CREATE TABLE exercise_mechanics (
    exercise_id INT REFERENCES exercise(exercise_id) ON DELETE CASCADE,
    mechanics_id INT REFERENCES mechanics(mechanics_id) ON DELETE CASCADE,
    PRIMARY KEY (exercise_id, mechanics_id)
);

CREATE TABLE exercise_force_pattern (
    exercise_id INT REFERENCES exercise(exercise_id) ON DELETE CASCADE,
    pattern_id INT REFERENCES force_pattern(pattern_id) ON DELETE CASCADE,
    PRIMARY KEY (exercise_id, pattern_id)
);

CREATE TABLE exercise_position (
    exercise_id INT REFERENCES exercise(exercise_id) ON DELETE CASCADE,
    position_id INT REFERENCES position(position_id) ON DELETE CASCADE,
    PRIMARY KEY (exercise_id, position_id)
);

-- =======================================================================================
-- PHASE 1: USER MANAGEMENT & GOALS (Added November 2025)
-- =======================================================================================

-- PHASE 1A: Goal Reference Tables

CREATE TABLE workout_goals (
    workout_goal_id SERIAL PRIMARY KEY,
    focus VARCHAR(50) NOT NULL CHECK (focus IN ('performance_enhancement', 'body_recomposition', 'efficiency', 'rebuilding_rehab')),
    goal_key VARCHAR(100) NOT NULL UNIQUE,
    goal_label_en VARCHAR(255) NOT NULL,
    goal_label_fa VARCHAR(255),
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_workout_goals_focus ON workout_goals(focus);
CREATE INDEX idx_workout_goals_key ON workout_goals(goal_key);
COMMENT ON TABLE workout_goals IS 'Workout plan generation goals - 5 per focus area (20 total)';

CREATE TABLE nutrition_goals (
    nutrition_goal_id SERIAL PRIMARY KEY,
    focus VARCHAR(50) NOT NULL CHECK (focus IN ('performance_enhancement', 'body_recomposition', 'efficiency', 'rebuilding_rehab')),
    goal_key VARCHAR(100) NOT NULL UNIQUE,
    goal_label_en VARCHAR(255) NOT NULL,
    goal_label_fa VARCHAR(255),
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_nutrition_goals_focus ON nutrition_goals(focus);
CREATE INDEX idx_nutrition_goals_key ON nutrition_goals(goal_key);
COMMENT ON TABLE nutrition_goals IS 'Nutrition plan generation goals - 5 per focus area (20 total)';

-- PHASE 1B: User Management Tables

CREATE TABLE users (
    user_id SERIAL PRIMARY KEY,
    
    -- Authentication
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    
    -- Demographics
    age INT,
    weight NUMERIC(5,2),
    height NUMERIC(5,2),
    gender VARCHAR(10) CHECK (gender IN ('male', 'female')),
    
    -- Fitness Profile
    focus VARCHAR(50) CHECK (focus IN ('performance_enhancement', 'body_recomposition', 'efficiency', 'rebuilding_rehab')),
    physical_fitness VARCHAR(20) CHECK (physical_fitness IN ('novice', 'beginner', 'intermediate', 'advanced')),
    fitness_days INT CHECK (fitness_days BETWEEN 1 AND 7),
    workout_goal_id INT REFERENCES workout_goals(workout_goal_id) ON DELETE SET NULL,
    nutrition_goal_id INT REFERENCES nutrition_goals(nutrition_goal_id) ON DELETE SET NULL,
    
    -- Sports
    sport VARCHAR(100),
    sport_days INT CHECK (sport_days BETWEEN 1 AND 7),
    specialized_sport VARCHAR(100),
    
    -- Workout Environment
    training_location VARCHAR(10) CHECK (training_location IN ('home', 'gym')),
    workout_limitations TEXT,
    
    -- Nutrition Profile
    dietary_restrictions TEXT,
    cooking_time VARCHAR(20) CHECK (cooking_time IN ('under_15', '15_30', '30_60', 'over_60')),
    cooking_skill VARCHAR(20) CHECK (cooking_skill IN ('beginner', 'intermediate', 'advanced')),
    kitchen_appliances TEXT[],
    food_preferences TEXT[],
    forbidden_ingredients TEXT[],
    
    -- Credits & Referrals
    credits INT DEFAULT 0 CHECK (credits >= 0),
    referral_code VARCHAR(20) UNIQUE NOT NULL,
    has_used_referral BOOLEAN DEFAULT FALSE,
    
    -- Timestamps
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_referral_code ON users(referral_code);
CREATE INDEX idx_users_created_at ON users(created_at);
COMMENT ON TABLE users IS 'User profiles with fitness/nutrition preferences';

CREATE TABLE user_home_equipment (
    user_equipment_id SERIAL PRIMARY KEY,
    user_id INT NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    equipment_id INT NOT NULL REFERENCES equipment(equipment_id) ON DELETE CASCADE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id, equipment_id)
);

CREATE INDEX idx_user_equipment_user ON user_home_equipment(user_id);
CREATE INDEX idx_user_equipment_equipment ON user_home_equipment(equipment_id);
COMMENT ON TABLE user_home_equipment IS 'User home equipment - references existing equipment table';

CREATE TABLE user_sessions (
    session_id SERIAL PRIMARY KEY,
    user_id INT NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    session_token VARCHAR(255) UNIQUE NOT NULL,
    expires_at TIMESTAMP NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_sessions_token ON user_sessions(session_token);
CREATE INDEX idx_sessions_user ON user_sessions(user_id);
CREATE INDEX idx_sessions_expires ON user_sessions(expires_at);
COMMENT ON TABLE user_sessions IS 'JWT authentication sessions';

CREATE TABLE credit_transactions (
    transaction_id SERIAL PRIMARY KEY,
    user_id INT NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    transaction_type VARCHAR(20) NOT NULL CHECK (transaction_type IN ('purchase', 'usage', 'referral', 'bonus')),
    amount INT NOT NULL,
    description TEXT,
    plan_type VARCHAR(20) CHECK (plan_type IN ('workout', 'nutrition')),
    plan_id INT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_transactions_user ON credit_transactions(user_id);
CREATE INDEX idx_transactions_created ON credit_transactions(created_at);
CREATE INDEX idx_transactions_type ON credit_transactions(transaction_type);
COMMENT ON TABLE credit_transactions IS 'Credit transaction audit trail';

-- Triggers for user management
CREATE OR REPLACE FUNCTION update_user_credits()
RETURNS TRIGGER AS $$
BEGIN
    UPDATE users SET credits = credits + NEW.amount WHERE user_id = NEW.user_id;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_update_credits
AFTER INSERT ON credit_transactions
FOR EACH ROW
EXECUTE FUNCTION update_user_credits();

CREATE OR REPLACE FUNCTION update_modified_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_users_modtime
BEFORE UPDATE ON users
FOR EACH ROW
EXECUTE FUNCTION update_modified_column();

-- =======================================================================================
-- PHASE 2: WORKOUT PLAN STRUCTURE (Added November 2025)
-- =======================================================================================

-- PHASE 2A: Workout Plans & Weeks

CREATE TABLE workout_plans (
    plan_id SERIAL PRIMARY KEY,
    user_id INT NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    workout_goal_id INT REFERENCES workout_goals(workout_goal_id) ON DELETE SET NULL,
    name VARCHAR(255) NOT NULL,
    total_weeks INT NOT NULL CHECK (total_weeks IN (1, 4, 12)),
    current_week INT DEFAULT 1 CHECK (current_week >= 1),
    completed_weeks INT[] DEFAULT ARRAY[]::INT[],
    strategy JSONB,
    expectations JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_workout_plans_user ON workout_plans(user_id);
CREATE INDEX idx_workout_plans_created ON workout_plans(created_at);

ALTER TABLE workout_plans 
ADD CONSTRAINT chk_current_week_range 
CHECK (current_week <= total_weeks);

COMMENT ON TABLE workout_plans IS 'User workout plans with progress tracking';
COMMENT ON COLUMN workout_plans.strategy IS 'AI-generated strategy JSONB';
COMMENT ON COLUMN workout_plans.expectations IS 'AI-generated expectations JSONB';

CREATE TABLE workout_weeks (
    week_id SERIAL PRIMARY KEY,
    plan_id INT NOT NULL REFERENCES workout_plans(plan_id) ON DELETE CASCADE,
    week_number INT NOT NULL CHECK (week_number >= 1 AND week_number <= 12),
    title VARCHAR(255),
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(plan_id, week_number)
);

CREATE INDEX idx_workout_weeks_plan ON workout_weeks(plan_id);
CREATE INDEX idx_workout_weeks_number ON workout_weeks(plan_id, week_number);
COMMENT ON TABLE workout_weeks IS 'Weekly structure within workout plans';

-- PHASE 2B: Workout Days & Exercises

CREATE TABLE workout_days (
    day_id SERIAL PRIMARY KEY,
    week_id INT NOT NULL REFERENCES workout_weeks(week_id) ON DELETE CASCADE,
    day_name VARCHAR(50) NOT NULL,
    focus TEXT,
    warmup TEXT,
    cooldown TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_workout_days_week ON workout_days(week_id);
COMMENT ON TABLE workout_days IS 'Daily workouts within each week';

CREATE TABLE workout_day_exercises (
    workout_day_exercise_id SERIAL PRIMARY KEY,
    day_id INT NOT NULL REFERENCES workout_days(day_id) ON DELETE CASCADE,
    exercise_id INT NOT NULL REFERENCES exercise(exercise_id) ON DELETE CASCADE,
    
    -- AI-generated attributes for this specific workout day
    sets VARCHAR(50),
    reps VARCHAR(50),
    tempo VARCHAR(50),
    rest VARCHAR(50),
    notes TEXT,
    exercise_order INT NOT NULL,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(day_id, exercise_order)
);

CREATE INDEX idx_workout_day_exercises_day ON workout_day_exercises(day_id);
CREATE INDEX idx_workout_day_exercises_exercise ON workout_day_exercises(exercise_id);
CREATE INDEX idx_workout_day_exercises_order ON workout_day_exercises(day_id, exercise_order);
COMMENT ON TABLE workout_day_exercises IS 'Junction table linking workout days to exercises with AI-generated parameters';

-- =======================================================================================
-- PHASE 3: NUTRITION PLAN STRUCTURE (Added November 2025)
-- =======================================================================================

-- PHASE 3A: Nutrition Plans & Weeks

CREATE TABLE nutrition_plans (
    plan_id SERIAL PRIMARY KEY,
    user_id INT NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    nutrition_goal_id INT REFERENCES nutrition_goals(nutrition_goal_id) ON DELETE SET NULL,
    name VARCHAR(255) NOT NULL,
    total_weeks INT NOT NULL CHECK (total_weeks IN (1, 4, 12)),
    current_week INT DEFAULT 1 CHECK (current_week >= 1),
    completed_weeks INT[] DEFAULT ARRAY[]::INT[],
    strategy JSONB,
    expectations JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_nutrition_plans_user ON nutrition_plans(user_id);
CREATE INDEX idx_nutrition_plans_created ON nutrition_plans(created_at);

ALTER TABLE nutrition_plans 
ADD CONSTRAINT chk_nutrition_current_week_range 
CHECK (current_week <= total_weeks);

COMMENT ON TABLE nutrition_plans IS 'User nutrition plans with meal structure';

CREATE TABLE nutrition_weeks (
    week_id SERIAL PRIMARY KEY,
    plan_id INT NOT NULL REFERENCES nutrition_plans(plan_id) ON DELETE CASCADE,
    week_number INT NOT NULL CHECK (week_number >= 1 AND week_number <= 12),
    title VARCHAR(255),
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(plan_id, week_number)
);

CREATE INDEX idx_nutrition_weeks_plan ON nutrition_weeks(plan_id);
CREATE INDEX idx_nutrition_weeks_number ON nutrition_weeks(plan_id, week_number);
COMMENT ON TABLE nutrition_weeks IS 'Weekly structure within nutrition plans';

-- PHASE 3B: Nutrition Days & Meals

CREATE TABLE nutrition_days (
    day_id SERIAL PRIMARY KEY,
    week_id INT NOT NULL REFERENCES nutrition_weeks(week_id) ON DELETE CASCADE,
    day_name VARCHAR(50) NOT NULL,
    daily_calories INT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_nutrition_days_week ON nutrition_days(week_id);
COMMENT ON TABLE nutrition_days IS 'Daily meal plans within each week';

CREATE TABLE meals (
    meal_id SERIAL PRIMARY KEY,
    day_id INT NOT NULL REFERENCES nutrition_days(day_id) ON DELETE CASCADE,
    meal_type VARCHAR(20) NOT NULL CHECK (meal_type IN ('breakfast', 'lunch', 'dinner', 'snacks')),
    name VARCHAR(255) NOT NULL,
    description TEXT,
    calories INT,
    protein NUMERIC(5,1),
    carbs NUMERIC(5,1),
    fats NUMERIC(5,1),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_meals_day ON meals(day_id);
CREATE INDEX idx_meals_type ON meals(day_id, meal_type);
COMMENT ON TABLE meals IS 'Individual meals within nutrition days';

-- =======================================================================================
-- PHASE 4: FEEDBACK SYSTEM (Added November 2025)
-- =======================================================================================

-- PHASE 4A: Feedback Questions

CREATE TABLE feedback_questions (
    question_id SERIAL PRIMARY KEY,
    week_table VARCHAR(20) NOT NULL CHECK (week_table IN ('workout_weeks', 'nutrition_weeks')),
    week_id INT NOT NULL,
    question_text TEXT NOT NULL,
    question_type VARCHAR(20) NOT NULL CHECK (question_type IN ('radio', 'multi-select')),
    options JSONB,
    allow_text BOOLEAN DEFAULT FALSE,
    dynamic_options VARCHAR(20) CHECK (dynamic_options IN ('exercises', 'meals', NULL)),
    question_order INT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_feedback_questions_week ON feedback_questions(week_table, week_id);
CREATE INDEX idx_feedback_questions_order ON feedback_questions(week_table, week_id, question_order);
COMMENT ON TABLE feedback_questions IS 'AI-generated feedback questions for specific weeks (polymorphic reference)';

-- PHASE 4B: Feedback Responses

CREATE TABLE feedback (
    feedback_id SERIAL PRIMARY KEY,
    user_id INT NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    week_table VARCHAR(20) NOT NULL CHECK (week_table IN ('workout_weeks', 'nutrition_weeks')),
    week_id INT NOT NULL,
    responses JSONB NOT NULL,
    submitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_feedback_user ON feedback(user_id);
CREATE INDEX idx_feedback_week ON feedback(week_table, week_id);
CREATE INDEX idx_feedback_submitted ON feedback(submitted_at);
COMMENT ON TABLE feedback IS 'User feedback responses for workout/nutrition weeks (polymorphic reference)';
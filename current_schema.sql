--
-- PostgreSQL database dump
--

\restrict mqF1IQHDSSBB61JohZzKVbo0Jb1h0grVpe18XvEWjx33hkSadFLbNKcTMsIpTh9

-- Dumped from database version 16.10 (Ubuntu 16.10-1.pgdg24.04+1)
-- Dumped by pg_dump version 16.10 (Ubuntu 16.10-1.pgdg24.04+1)

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

--
-- Name: vector; Type: EXTENSION; Schema: -; Owner: -
--

CREATE EXTENSION IF NOT EXISTS vector WITH SCHEMA public;


--
-- Name: EXTENSION vector; Type: COMMENT; Schema: -; Owner: 
--

COMMENT ON EXTENSION vector IS 'vector data type and ivfflat and hnsw access methods';


--
-- Name: update_modified_column(); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.update_modified_column() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$;


ALTER FUNCTION public.update_modified_column() OWNER TO postgres;

--
-- Name: update_user_credits(); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.update_user_credits() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
BEGIN
    UPDATE users SET credits = credits + NEW.amount WHERE user_id = NEW.user_id;
    RETURN NEW;
END;
$$;


ALTER FUNCTION public.update_user_credits() OWNER TO postgres;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: alembic_version; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.alembic_version (
    version_num character varying(32) NOT NULL
);


ALTER TABLE public.alembic_version OWNER TO postgres;

--
-- Name: credit_transactions; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.credit_transactions (
    transaction_id integer NOT NULL,
    user_id integer NOT NULL,
    transaction_type character varying(20) NOT NULL,
    amount integer NOT NULL,
    description text,
    plan_type character varying(20),
    plan_id integer,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT credit_transactions_plan_type_check CHECK (((plan_type)::text = ANY (ARRAY[('workout'::character varying)::text, ('nutrition'::character varying)::text]))),
    CONSTRAINT credit_transactions_transaction_type_check CHECK (((transaction_type)::text = ANY (ARRAY[('purchase'::character varying)::text, ('usage'::character varying)::text, ('referral'::character varying)::text, ('bonus'::character varying)::text])))
);


ALTER TABLE public.credit_transactions OWNER TO postgres;

--
-- Name: TABLE credit_transactions; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON TABLE public.credit_transactions IS 'Credit transaction audit trail';


--
-- Name: credit_transactions_transaction_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.credit_transactions_transaction_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.credit_transactions_transaction_id_seq OWNER TO postgres;

--
-- Name: credit_transactions_transaction_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.credit_transactions_transaction_id_seq OWNED BY public.credit_transactions.transaction_id;


--
-- Name: difficulty; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.difficulty (
    difficulty_id integer NOT NULL,
    name_en character varying(100) NOT NULL,
    name_fa character varying(100) NOT NULL
);


ALTER TABLE public.difficulty OWNER TO postgres;

--
-- Name: difficulty_difficulty_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.difficulty_difficulty_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.difficulty_difficulty_id_seq OWNER TO postgres;

--
-- Name: difficulty_difficulty_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.difficulty_difficulty_id_seq OWNED BY public.difficulty.difficulty_id;


--
-- Name: equipment; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.equipment (
    equipment_id integer NOT NULL,
    name_en character varying(100) NOT NULL,
    name_fa character varying(100) NOT NULL
);


ALTER TABLE public.equipment OWNER TO postgres;

--
-- Name: equipment_equipment_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.equipment_equipment_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.equipment_equipment_id_seq OWNER TO postgres;

--
-- Name: equipment_equipment_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.equipment_equipment_id_seq OWNED BY public.equipment.equipment_id;


--
-- Name: exercise; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.exercise (
    exercise_id integer NOT NULL,
    name_en text NOT NULL,
    name_fa text NOT NULL,
    difficulty_id integer,
    style_id integer,
    instructions_en text[],
    instructions_fa text[],
    page_url text,
    male_urls text[],
    female_urls text[],
    male_image_urls text[],
    female_image_urls text[]
);


ALTER TABLE public.exercise OWNER TO postgres;

--
-- Name: exercise_equipment; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.exercise_equipment (
    exercise_id integer NOT NULL,
    equipment_id integer NOT NULL
);


ALTER TABLE public.exercise_equipment OWNER TO postgres;

--
-- Name: exercise_force_pattern; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.exercise_force_pattern (
    exercise_id integer NOT NULL,
    pattern_id integer NOT NULL
);


ALTER TABLE public.exercise_force_pattern OWNER TO postgres;

--
-- Name: exercise_goal; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.exercise_goal (
    exercise_id integer NOT NULL,
    goal_id integer NOT NULL
);


ALTER TABLE public.exercise_goal OWNER TO postgres;

--
-- Name: exercise_mechanics; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.exercise_mechanics (
    exercise_id integer NOT NULL,
    mechanics_id integer NOT NULL
);


ALTER TABLE public.exercise_mechanics OWNER TO postgres;

--
-- Name: exercise_movement_pattern; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.exercise_movement_pattern (
    exercise_id integer NOT NULL,
    pattern_id integer NOT NULL
);


ALTER TABLE public.exercise_movement_pattern OWNER TO postgres;

--
-- Name: TABLE exercise_movement_pattern; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON TABLE public.exercise_movement_pattern IS 'Links exercises to their primary movement pattern (one per exercise)';


--
-- Name: exercise_muscle; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.exercise_muscle (
    exercise_id integer NOT NULL,
    muscle_id integer NOT NULL
);


ALTER TABLE public.exercise_muscle OWNER TO postgres;

--
-- Name: exercise_muscle_group; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.exercise_muscle_group (
    exercise_id integer NOT NULL,
    muscle_group_id integer NOT NULL
);


ALTER TABLE public.exercise_muscle_group OWNER TO postgres;

--
-- Name: TABLE exercise_muscle_group; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON TABLE public.exercise_muscle_group IS 'Links exercises to high-level muscle groups';


--
-- Name: exercise_muscle_region; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.exercise_muscle_region (
    exercise_id integer NOT NULL,
    muscle_region_id integer NOT NULL
);


ALTER TABLE public.exercise_muscle_region OWNER TO postgres;

--
-- Name: TABLE exercise_muscle_region; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON TABLE public.exercise_muscle_region IS 'Links exercises to specific muscle regions for targeted training';


--
-- Name: exercise_position; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.exercise_position (
    exercise_id integer NOT NULL,
    position_id integer NOT NULL
);


ALTER TABLE public.exercise_position OWNER TO postgres;

--
-- Name: exercise_training_phase; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.exercise_training_phase (
    exercise_id integer NOT NULL,
    phase_id integer NOT NULL
);


ALTER TABLE public.exercise_training_phase OWNER TO postgres;

--
-- Name: feedback; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.feedback (
    feedback_id integer NOT NULL,
    user_id integer NOT NULL,
    week_table character varying(20) NOT NULL,
    week_id integer NOT NULL,
    responses jsonb NOT NULL,
    submitted_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT feedback_week_table_check CHECK (((week_table)::text = ANY (ARRAY[('workout_weeks'::character varying)::text, ('nutrition_weeks'::character varying)::text])))
);


ALTER TABLE public.feedback OWNER TO postgres;

--
-- Name: TABLE feedback; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON TABLE public.feedback IS 'User feedback responses for workout/nutrition weeks';


--
-- Name: COLUMN feedback.week_table; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.feedback.week_table IS 'Which table week_id references: workout_weeks or nutrition_weeks';


--
-- Name: COLUMN feedback.week_id; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.feedback.week_id IS 'Foreign key to workout_weeks.week_id OR nutrition_weeks.week_id';


--
-- Name: COLUMN feedback.responses; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.feedback.responses IS 'JSONB array of {question_id, answer, text_response}';


--
-- Name: feedback_feedback_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.feedback_feedback_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.feedback_feedback_id_seq OWNER TO postgres;

--
-- Name: feedback_feedback_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.feedback_feedback_id_seq OWNED BY public.feedback.feedback_id;


--
-- Name: feedback_questions; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.feedback_questions (
    question_id integer NOT NULL,
    week_table character varying(20) NOT NULL,
    week_number integer NOT NULL,
    focus character varying(50) NOT NULL,
    question_text text NOT NULL,
    question_type character varying(20) NOT NULL,
    options jsonb,
    allow_text boolean DEFAULT false,
    dynamic_options character varying(20),
    question_order integer NOT NULL,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT feedback_questions_dynamic_options_check CHECK (((dynamic_options)::text = ANY (ARRAY[('exercises'::character varying)::text, ('meals'::character varying)::text, (NULL::character varying)::text]))),
    CONSTRAINT feedback_questions_focus_check CHECK (((focus)::text = ANY (ARRAY[('performance_enhancement'::character varying)::text, ('body_recomposition'::character varying)::text, ('efficiency'::character varying)::text, ('rebuilding_rehab'::character varying)::text]))),
    CONSTRAINT feedback_questions_question_type_check CHECK (((question_type)::text = ANY (ARRAY[('radio'::character varying)::text, ('multi-select'::character varying)::text]))),
    CONSTRAINT feedback_questions_week_table_check CHECK (((week_table)::text = ANY (ARRAY[('workout_weeks'::character varying)::text, ('nutrition_weeks'::character varying)::text])))
);


ALTER TABLE public.feedback_questions OWNER TO postgres;

--
-- Name: TABLE feedback_questions; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON TABLE public.feedback_questions IS 'AI-generated feedback questions for specific weeks';


--
-- Name: COLUMN feedback_questions.week_table; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.feedback_questions.week_table IS 'Which table week_id references: workout_weeks or nutrition_weeks';


--
-- Name: COLUMN feedback_questions.week_number; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.feedback_questions.week_number IS 'Foreign key to workout_weeks.week_id OR nutrition_weeks.week_id (polymorphic)';


--
-- Name: COLUMN feedback_questions.focus; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.feedback_questions.focus IS 'User fitness focus: general_fitness, performance_enhancement, weight_loss, muscle_building';


--
-- Name: COLUMN feedback_questions.options; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.feedback_questions.options IS 'JSONB array: [{"label":"Easy","value":"easy"}]';


--
-- Name: COLUMN feedback_questions.dynamic_options; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.feedback_questions.dynamic_options IS 'If "exercises" or "meals", generate options from week data';


--
-- Name: feedback_questions_question_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.feedback_questions_question_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.feedback_questions_question_id_seq OWNER TO postgres;

--
-- Name: feedback_questions_question_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.feedback_questions_question_id_seq OWNED BY public.feedback_questions.question_id;


--
-- Name: force_pattern; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.force_pattern (
    pattern_id integer NOT NULL,
    name_en character varying(100) NOT NULL,
    name_fa character varying(100) NOT NULL
);


ALTER TABLE public.force_pattern OWNER TO postgres;

--
-- Name: force_pattern_pattern_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.force_pattern_pattern_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.force_pattern_pattern_id_seq OWNER TO postgres;

--
-- Name: force_pattern_pattern_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.force_pattern_pattern_id_seq OWNED BY public.force_pattern.pattern_id;


--
-- Name: goal; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.goal (
    goal_id integer NOT NULL,
    name_en character varying(100) NOT NULL,
    name_fa character varying(100) NOT NULL
);


ALTER TABLE public.goal OWNER TO postgres;

--
-- Name: goal_goal_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.goal_goal_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.goal_goal_id_seq OWNER TO postgres;

--
-- Name: goal_goal_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.goal_goal_id_seq OWNED BY public.goal.goal_id;


--
-- Name: langchain_pg_collection; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.langchain_pg_collection (
    name character varying,
    cmetadata json,
    uuid uuid NOT NULL
);


ALTER TABLE public.langchain_pg_collection OWNER TO postgres;

--
-- Name: langchain_pg_embedding; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.langchain_pg_embedding (
    collection_id uuid,
    embedding public.vector,
    document character varying,
    cmetadata json,
    custom_id character varying,
    uuid uuid NOT NULL
);


ALTER TABLE public.langchain_pg_embedding OWNER TO postgres;

--
-- Name: meals; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.meals (
    meal_id integer NOT NULL,
    day_id integer NOT NULL,
    meal_type character varying(20) NOT NULL,
    name character varying(255) NOT NULL,
    description text,
    calories integer,
    protein numeric(5,1),
    carbs numeric(5,1),
    fats numeric(5,1),
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT meals_meal_type_check CHECK (((meal_type)::text = ANY (ARRAY[('breakfast'::character varying)::text, ('lunch'::character varying)::text, ('dinner'::character varying)::text, ('snacks'::character varying)::text])))
);


ALTER TABLE public.meals OWNER TO postgres;

--
-- Name: TABLE meals; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON TABLE public.meals IS 'Individual meals within nutrition days';


--
-- Name: COLUMN meals.meal_type; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.meals.meal_type IS 'One of: breakfast, lunch, dinner, snacks';


--
-- Name: COLUMN meals.protein; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.meals.protein IS 'Protein in grams';


--
-- Name: COLUMN meals.carbs; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.meals.carbs IS 'Carbohydrates in grams';


--
-- Name: COLUMN meals.fats; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.meals.fats IS 'Fats in grams';


--
-- Name: meals_meal_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.meals_meal_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.meals_meal_id_seq OWNER TO postgres;

--
-- Name: meals_meal_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.meals_meal_id_seq OWNED BY public.meals.meal_id;


--
-- Name: mechanics; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.mechanics (
    mechanics_id integer NOT NULL,
    name_en character varying(100) NOT NULL,
    name_fa character varying(100) NOT NULL
);


ALTER TABLE public.mechanics OWNER TO postgres;

--
-- Name: mechanics_mechanics_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.mechanics_mechanics_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.mechanics_mechanics_id_seq OWNER TO postgres;

--
-- Name: mechanics_mechanics_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.mechanics_mechanics_id_seq OWNED BY public.mechanics.mechanics_id;


--
-- Name: movement_pattern; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.movement_pattern (
    pattern_id integer NOT NULL,
    name_en character varying(100) NOT NULL,
    name_fa character varying(100) NOT NULL
);


ALTER TABLE public.movement_pattern OWNER TO postgres;

--
-- Name: TABLE movement_pattern; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON TABLE public.movement_pattern IS 'Primary movement patterns for exercise classification';


--
-- Name: movement_pattern_pattern_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.movement_pattern_pattern_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.movement_pattern_pattern_id_seq OWNER TO postgres;

--
-- Name: movement_pattern_pattern_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.movement_pattern_pattern_id_seq OWNED BY public.movement_pattern.pattern_id;


--
-- Name: muscle; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.muscle (
    muscle_id integer NOT NULL,
    name_en character varying(100) NOT NULL,
    name_fa character varying(100) NOT NULL
);


ALTER TABLE public.muscle OWNER TO postgres;

--
-- Name: muscle_group; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.muscle_group (
    muscle_group_id integer NOT NULL,
    name_en character varying(100) NOT NULL,
    name_fa character varying(100) NOT NULL
);


ALTER TABLE public.muscle_group OWNER TO postgres;

--
-- Name: TABLE muscle_group; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON TABLE public.muscle_group IS 'High-level muscle groups (Glutes, Quads, Hamstrings, etc.)';


--
-- Name: muscle_group_muscle_group_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.muscle_group_muscle_group_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.muscle_group_muscle_group_id_seq OWNER TO postgres;

--
-- Name: muscle_group_muscle_group_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.muscle_group_muscle_group_id_seq OWNED BY public.muscle_group.muscle_group_id;


--
-- Name: muscle_muscle_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.muscle_muscle_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.muscle_muscle_id_seq OWNER TO postgres;

--
-- Name: muscle_muscle_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.muscle_muscle_id_seq OWNED BY public.muscle.muscle_id;


--
-- Name: muscle_region; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.muscle_region (
    muscle_region_id integer NOT NULL,
    muscle_group_id integer NOT NULL,
    name_en character varying(100) NOT NULL,
    name_fa character varying(100) NOT NULL
);


ALTER TABLE public.muscle_region OWNER TO postgres;

--
-- Name: TABLE muscle_region; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON TABLE public.muscle_region IS 'Specific regions within muscle groups (e.g., Vastus Medialis within Quads)';


--
-- Name: muscle_region_muscle_region_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.muscle_region_muscle_region_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.muscle_region_muscle_region_id_seq OWNER TO postgres;

--
-- Name: muscle_region_muscle_region_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.muscle_region_muscle_region_id_seq OWNED BY public.muscle_region.muscle_region_id;


--
-- Name: nutrition_days; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.nutrition_days (
    day_id integer NOT NULL,
    week_id integer NOT NULL,
    day_name character varying(50) NOT NULL,
    daily_calories integer,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE public.nutrition_days OWNER TO postgres;

--
-- Name: TABLE nutrition_days; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON TABLE public.nutrition_days IS 'Daily meal plans within each week';


--
-- Name: COLUMN nutrition_days.day_name; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.nutrition_days.day_name IS 'Day name (e.g., "شنبه", "Monday", "Day 1")';


--
-- Name: COLUMN nutrition_days.daily_calories; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.nutrition_days.daily_calories IS 'Target calories for the day';


--
-- Name: nutrition_days_day_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.nutrition_days_day_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.nutrition_days_day_id_seq OWNER TO postgres;

--
-- Name: nutrition_days_day_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.nutrition_days_day_id_seq OWNED BY public.nutrition_days.day_id;


--
-- Name: nutrition_goals; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.nutrition_goals (
    nutrition_goal_id integer NOT NULL,
    focus character varying(50) NOT NULL,
    goal_key character varying(100) NOT NULL,
    goal_label_en character varying(255) NOT NULL,
    goal_label_fa character varying(255),
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    description_en text,
    description_fa text,
    CONSTRAINT nutrition_goals_focus_check CHECK (((focus)::text = ANY (ARRAY[('performance_enhancement'::character varying)::text, ('body_recomposition'::character varying)::text, ('efficiency'::character varying)::text, ('rebuilding_rehab'::character varying)::text])))
);


ALTER TABLE public.nutrition_goals OWNER TO postgres;

--
-- Name: TABLE nutrition_goals; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON TABLE public.nutrition_goals IS 'Nutrition plan generation goals - 5 per focus area';


--
-- Name: nutrition_goals_nutrition_goal_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.nutrition_goals_nutrition_goal_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.nutrition_goals_nutrition_goal_id_seq OWNER TO postgres;

--
-- Name: nutrition_goals_nutrition_goal_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.nutrition_goals_nutrition_goal_id_seq OWNED BY public.nutrition_goals.nutrition_goal_id;


--
-- Name: nutrition_plans; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.nutrition_plans (
    plan_id integer NOT NULL,
    user_id integer NOT NULL,
    nutrition_goal_id integer,
    name character varying(255) NOT NULL,
    total_weeks integer NOT NULL,
    current_week integer DEFAULT 1,
    completed_weeks integer[] DEFAULT ARRAY[]::integer[],
    strategy jsonb,
    expectations jsonb,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT chk_nutrition_current_week_range CHECK ((current_week <= total_weeks)),
    CONSTRAINT nutrition_plans_current_week_check CHECK ((current_week >= 1)),
    CONSTRAINT nutrition_plans_total_weeks_check CHECK ((total_weeks = ANY (ARRAY[1, 4, 12])))
);


ALTER TABLE public.nutrition_plans OWNER TO postgres;

--
-- Name: TABLE nutrition_plans; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON TABLE public.nutrition_plans IS 'User nutrition plans with meal structure';


--
-- Name: COLUMN nutrition_plans.nutrition_goal_id; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.nutrition_plans.nutrition_goal_id IS 'User selected nutrition goal at plan generation';


--
-- Name: nutrition_plans_plan_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.nutrition_plans_plan_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.nutrition_plans_plan_id_seq OWNER TO postgres;

--
-- Name: nutrition_plans_plan_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.nutrition_plans_plan_id_seq OWNED BY public.nutrition_plans.plan_id;


--
-- Name: nutrition_weeks; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.nutrition_weeks (
    week_id integer NOT NULL,
    plan_id integer NOT NULL,
    week_number integer NOT NULL,
    title character varying(255),
    description text,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT nutrition_weeks_week_number_check CHECK (((week_number >= 1) AND (week_number <= 12)))
);


ALTER TABLE public.nutrition_weeks OWNER TO postgres;

--
-- Name: TABLE nutrition_weeks; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON TABLE public.nutrition_weeks IS 'Weekly structure within nutrition plans';


--
-- Name: nutrition_weeks_week_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.nutrition_weeks_week_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.nutrition_weeks_week_id_seq OWNER TO postgres;

--
-- Name: nutrition_weeks_week_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.nutrition_weeks_week_id_seq OWNED BY public.nutrition_weeks.week_id;


--
-- Name: position; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public."position" (
    position_id integer NOT NULL,
    name_en character varying(100) NOT NULL,
    name_fa character varying(100) NOT NULL
);


ALTER TABLE public."position" OWNER TO postgres;

--
-- Name: position_position_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.position_position_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.position_position_id_seq OWNER TO postgres;

--
-- Name: position_position_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.position_position_id_seq OWNED BY public."position".position_id;


--
-- Name: style; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.style (
    style_id integer NOT NULL,
    name_en character varying(100) NOT NULL,
    name_fa character varying(100) NOT NULL
);


ALTER TABLE public.style OWNER TO postgres;

--
-- Name: style_style_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.style_style_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.style_style_id_seq OWNER TO postgres;

--
-- Name: style_style_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.style_style_id_seq OWNED BY public.style.style_id;


--
-- Name: training_phase; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.training_phase (
    phase_id integer NOT NULL,
    name_en character varying(100) NOT NULL,
    name_fa character varying(100) NOT NULL
);


ALTER TABLE public.training_phase OWNER TO postgres;

--
-- Name: training_phase_phase_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.training_phase_phase_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.training_phase_phase_id_seq OWNER TO postgres;

--
-- Name: training_phase_phase_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.training_phase_phase_id_seq OWNED BY public.training_phase.phase_id;


--
-- Name: user_auth_methods; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.user_auth_methods (
    id integer NOT NULL,
    user_id integer NOT NULL,
    auth_provider character varying(20) NOT NULL,
    auth_identifier character varying(255) NOT NULL,
    auth_data json,
    is_verified boolean DEFAULT true NOT NULL,
    is_primary boolean DEFAULT false NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.user_auth_methods OWNER TO postgres;

--
-- Name: user_auth_methods_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.user_auth_methods_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.user_auth_methods_id_seq OWNER TO postgres;

--
-- Name: user_auth_methods_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.user_auth_methods_id_seq OWNED BY public.user_auth_methods.id;


--
-- Name: user_gym_equipment; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.user_gym_equipment (
    user_equipment_id integer NOT NULL,
    user_id integer NOT NULL,
    equipment_id integer NOT NULL,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE public.user_gym_equipment OWNER TO postgres;

--
-- Name: TABLE user_gym_equipment; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON TABLE public.user_gym_equipment IS 'Stores gym equipment available to each user';


--
-- Name: COLUMN user_gym_equipment.user_equipment_id; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.user_gym_equipment.user_equipment_id IS 'Primary key for user gym equipment relation';


--
-- Name: COLUMN user_gym_equipment.user_id; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.user_gym_equipment.user_id IS 'Reference to the user';


--
-- Name: COLUMN user_gym_equipment.equipment_id; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.user_gym_equipment.equipment_id IS 'Reference to the equipment available at gym';


--
-- Name: COLUMN user_gym_equipment.created_at; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.user_gym_equipment.created_at IS 'Timestamp when the equipment was added to user profile';


--
-- Name: user_gym_equipment_user_equipment_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.user_gym_equipment_user_equipment_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.user_gym_equipment_user_equipment_id_seq OWNER TO postgres;

--
-- Name: user_gym_equipment_user_equipment_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.user_gym_equipment_user_equipment_id_seq OWNED BY public.user_gym_equipment.user_equipment_id;


--
-- Name: user_home_equipment; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.user_home_equipment (
    user_equipment_id integer NOT NULL,
    user_id integer NOT NULL,
    equipment_id integer NOT NULL,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE public.user_home_equipment OWNER TO postgres;

--
-- Name: TABLE user_home_equipment; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON TABLE public.user_home_equipment IS 'User home equipment junction table';


--
-- Name: user_home_equipment_user_equipment_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.user_home_equipment_user_equipment_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.user_home_equipment_user_equipment_id_seq OWNER TO postgres;

--
-- Name: user_home_equipment_user_equipment_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.user_home_equipment_user_equipment_id_seq OWNED BY public.user_home_equipment.user_equipment_id;


--
-- Name: user_sessions; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.user_sessions (
    session_id integer NOT NULL,
    user_id integer NOT NULL,
    session_token character varying(255) NOT NULL,
    expires_at timestamp without time zone NOT NULL,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE public.user_sessions OWNER TO postgres;

--
-- Name: TABLE user_sessions; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON TABLE public.user_sessions IS 'JWT authentication sessions';


--
-- Name: user_sessions_session_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.user_sessions_session_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.user_sessions_session_id_seq OWNER TO postgres;

--
-- Name: user_sessions_session_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.user_sessions_session_id_seq OWNED BY public.user_sessions.session_id;


--
-- Name: users; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.users (
    user_id integer NOT NULL,
    email character varying(255),
    password_hash character varying(255),
    is_active boolean DEFAULT true,
    age integer,
    weight numeric(5,2),
    height numeric(5,2),
    gender character varying(10),
    focus character varying(50),
    physical_fitness character varying(20),
    fitness_days integer,
    workout_goal_id integer,
    nutrition_goal_id integer,
    sport character varying(100),
    sport_days integer,
    specialized_sport character varying(100),
    training_location character varying(10),
    workout_limitations text,
    dietary_restrictions text,
    cooking_time character varying(20),
    cooking_skill character varying(20),
    kitchen_appliances text[],
    food_preferences text[],
    forbidden_ingredients text[],
    credits integer DEFAULT 0,
    referral_code character varying(20) NOT NULL,
    has_used_referral boolean DEFAULT false,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    telegram_id bigint,
    CONSTRAINT users_cooking_skill_check CHECK (((cooking_skill)::text = ANY (ARRAY[('beginner'::character varying)::text, ('intermediate'::character varying)::text, ('advanced'::character varying)::text]))),
    CONSTRAINT users_cooking_time_check CHECK (((cooking_time)::text = ANY (ARRAY[('under_15'::character varying)::text, ('15_30'::character varying)::text, ('30_60'::character varying)::text, ('over_60'::character varying)::text]))),
    CONSTRAINT users_credits_check CHECK ((credits >= 0)),
    CONSTRAINT users_fitness_days_check CHECK (((fitness_days >= 1) AND (fitness_days <= 7))),
    CONSTRAINT users_focus_check CHECK (((focus)::text = ANY (ARRAY[('performance_enhancement'::character varying)::text, ('body_recomposition'::character varying)::text, ('efficiency'::character varying)::text, ('rebuilding_rehab'::character varying)::text]))),
    CONSTRAINT users_gender_check CHECK (((gender)::text = ANY (ARRAY[('male'::character varying)::text, ('female'::character varying)::text]))),
    CONSTRAINT users_physical_fitness_check CHECK (((physical_fitness)::text = ANY (ARRAY[('novice'::character varying)::text, ('beginner'::character varying)::text, ('intermediate'::character varying)::text, ('advanced'::character varying)::text]))),
    CONSTRAINT users_sport_days_check CHECK (((sport_days >= 1) AND (sport_days <= 7))),
    CONSTRAINT users_training_location_check CHECK (((training_location)::text = ANY (ARRAY[('home'::character varying)::text, ('gym'::character varying)::text])))
);


ALTER TABLE public.users OWNER TO postgres;

--
-- Name: TABLE users; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON TABLE public.users IS 'User profiles with fitness/nutrition preferences';


--
-- Name: COLUMN users.workout_goal_id; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.users.workout_goal_id IS 'Selected workout goal from workout_goals table';


--
-- Name: COLUMN users.nutrition_goal_id; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.users.nutrition_goal_id IS 'Selected nutrition goal from nutrition_goals table';


--
-- Name: user_statistics; Type: VIEW; Schema: public; Owner: postgres
--

CREATE VIEW public.user_statistics AS
 SELECT u.user_id,
    u.email,
    u.credits,
    u.created_at,
    u.has_used_referral,
    count(DISTINCT ct.transaction_id) FILTER (WHERE ((ct.transaction_type)::text = 'usage'::text)) AS total_plans_generated,
    COALESCE(sum(ct.amount) FILTER (WHERE ((ct.transaction_type)::text = 'purchase'::text)), (0)::bigint) AS total_credits_purchased,
    COALESCE(sum(abs(ct.amount)) FILTER (WHERE ((ct.transaction_type)::text = 'usage'::text)), (0)::bigint) AS total_credits_spent
   FROM (public.users u
     LEFT JOIN public.credit_transactions ct ON ((u.user_id = ct.user_id)))
  GROUP BY u.user_id, u.email, u.credits, u.created_at, u.has_used_referral;


ALTER VIEW public.user_statistics OWNER TO postgres;

--
-- Name: users_user_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.users_user_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.users_user_id_seq OWNER TO postgres;

--
-- Name: users_user_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.users_user_id_seq OWNED BY public.users.user_id;


--
-- Name: verification_codes; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.verification_codes (
    id integer NOT NULL,
    identifier character varying(255) NOT NULL,
    code character varying(6) NOT NULL,
    code_type character varying(10) NOT NULL,
    expires_at timestamp with time zone NOT NULL,
    attempts integer DEFAULT 0 NOT NULL,
    verified boolean DEFAULT false NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.verification_codes OWNER TO postgres;

--
-- Name: verification_codes_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.verification_codes_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.verification_codes_id_seq OWNER TO postgres;

--
-- Name: verification_codes_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.verification_codes_id_seq OWNED BY public.verification_codes.id;


--
-- Name: workout_day_exercises; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.workout_day_exercises (
    workout_day_exercise_id integer NOT NULL,
    day_id integer NOT NULL,
    exercise_id integer NOT NULL,
    sets character varying(50),
    reps character varying(50),
    tempo character varying(50),
    rest character varying(50),
    notes text,
    exercise_order integer NOT NULL,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE public.workout_day_exercises OWNER TO postgres;

--
-- Name: TABLE workout_day_exercises; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON TABLE public.workout_day_exercises IS 'Junction table linking workout days to exercises with AI-generated parameters';


--
-- Name: COLUMN workout_day_exercises.exercise_id; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.workout_day_exercises.exercise_id IS 'References exercise table - the actual exercise from database';


--
-- Name: COLUMN workout_day_exercises.sets; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.workout_day_exercises.sets IS 'AI-generated sets (e.g., "3", "4-5")';


--
-- Name: COLUMN workout_day_exercises.reps; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.workout_day_exercises.reps IS 'AI-generated rep range (e.g., "8-12", "AMRAP")';


--
-- Name: COLUMN workout_day_exercises.tempo; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.workout_day_exercises.tempo IS 'AI-generated tempo (e.g., "3010", "Explosive")';


--
-- Name: COLUMN workout_day_exercises.rest; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.workout_day_exercises.rest IS 'AI-generated rest period (e.g., "60 sec", "90-120 sec")';


--
-- Name: COLUMN workout_day_exercises.exercise_order; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.workout_day_exercises.exercise_order IS 'Order of exercise in the workout day';


--
-- Name: workout_day_exercises_workout_day_exercise_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.workout_day_exercises_workout_day_exercise_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.workout_day_exercises_workout_day_exercise_id_seq OWNER TO postgres;

--
-- Name: workout_day_exercises_workout_day_exercise_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.workout_day_exercises_workout_day_exercise_id_seq OWNED BY public.workout_day_exercises.workout_day_exercise_id;


--
-- Name: workout_days; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.workout_days (
    day_id integer NOT NULL,
    week_id integer NOT NULL,
    day_name character varying(50) NOT NULL,
    focus text,
    warmup text,
    cooldown text,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE public.workout_days OWNER TO postgres;

--
-- Name: TABLE workout_days; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON TABLE public.workout_days IS 'Daily workouts within each week';


--
-- Name: COLUMN workout_days.day_name; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.workout_days.day_name IS 'Day name (e.g., "شنبه", "Monday", "Day 1")';


--
-- Name: COLUMN workout_days.focus; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.workout_days.focus IS 'Daily focus (e.g., "سینه و سه سر", "Chest & Triceps")';


--
-- Name: workout_days_day_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.workout_days_day_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.workout_days_day_id_seq OWNER TO postgres;

--
-- Name: workout_days_day_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.workout_days_day_id_seq OWNED BY public.workout_days.day_id;


--
-- Name: workout_goals; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.workout_goals (
    workout_goal_id integer NOT NULL,
    focus character varying(50) NOT NULL,
    goal_key character varying(100) NOT NULL,
    goal_label_en character varying(255) NOT NULL,
    goal_label_fa character varying(255),
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    description_en text,
    description_fa text,
    CONSTRAINT workout_goals_focus_check CHECK (((focus)::text = ANY (ARRAY[('performance_enhancement'::character varying)::text, ('body_recomposition'::character varying)::text, ('efficiency'::character varying)::text, ('rebuilding_rehab'::character varying)::text])))
);


ALTER TABLE public.workout_goals OWNER TO postgres;

--
-- Name: TABLE workout_goals; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON TABLE public.workout_goals IS 'Workout plan generation goals - 5 per focus area';


--
-- Name: workout_goals_workout_goal_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.workout_goals_workout_goal_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.workout_goals_workout_goal_id_seq OWNER TO postgres;

--
-- Name: workout_goals_workout_goal_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.workout_goals_workout_goal_id_seq OWNED BY public.workout_goals.workout_goal_id;


--
-- Name: workout_plans; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.workout_plans (
    plan_id integer NOT NULL,
    user_id integer NOT NULL,
    workout_goal_id integer,
    name character varying(255) NOT NULL,
    total_weeks integer NOT NULL,
    current_week integer DEFAULT 1,
    completed_weeks integer[] DEFAULT ARRAY[]::integer[],
    strategy jsonb,
    expectations jsonb,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT chk_current_week_range CHECK ((current_week <= total_weeks)),
    CONSTRAINT workout_plans_current_week_check CHECK ((current_week >= 1)),
    CONSTRAINT workout_plans_total_weeks_check CHECK ((total_weeks = ANY (ARRAY[1, 4, 12])))
);


ALTER TABLE public.workout_plans OWNER TO postgres;

--
-- Name: TABLE workout_plans; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON TABLE public.workout_plans IS 'User workout plans with progress tracking';


--
-- Name: COLUMN workout_plans.workout_goal_id; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.workout_plans.workout_goal_id IS 'User selected workout goal at plan generation';


--
-- Name: COLUMN workout_plans.strategy; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.workout_plans.strategy IS 'AI-generated strategy JSONB: {"title": "...", "description": "..."}';


--
-- Name: COLUMN workout_plans.expectations; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.workout_plans.expectations IS 'AI-generated expectations JSONB: {"title": "...", "description": "..."}';


--
-- Name: workout_plans_plan_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.workout_plans_plan_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.workout_plans_plan_id_seq OWNER TO postgres;

--
-- Name: workout_plans_plan_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.workout_plans_plan_id_seq OWNED BY public.workout_plans.plan_id;


--
-- Name: workout_weeks; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.workout_weeks (
    week_id integer NOT NULL,
    plan_id integer NOT NULL,
    week_number integer NOT NULL,
    title character varying(255),
    description text,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT workout_weeks_week_number_check CHECK (((week_number >= 1) AND (week_number <= 12)))
);


ALTER TABLE public.workout_weeks OWNER TO postgres;

--
-- Name: TABLE workout_weeks; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON TABLE public.workout_weeks IS 'Weekly structure within workout plans';


--
-- Name: workout_weeks_week_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.workout_weeks_week_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.workout_weeks_week_id_seq OWNER TO postgres;

--
-- Name: workout_weeks_week_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.workout_weeks_week_id_seq OWNED BY public.workout_weeks.week_id;


--
-- Name: credit_transactions transaction_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.credit_transactions ALTER COLUMN transaction_id SET DEFAULT nextval('public.credit_transactions_transaction_id_seq'::regclass);


--
-- Name: difficulty difficulty_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.difficulty ALTER COLUMN difficulty_id SET DEFAULT nextval('public.difficulty_difficulty_id_seq'::regclass);


--
-- Name: equipment equipment_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.equipment ALTER COLUMN equipment_id SET DEFAULT nextval('public.equipment_equipment_id_seq'::regclass);


--
-- Name: feedback feedback_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.feedback ALTER COLUMN feedback_id SET DEFAULT nextval('public.feedback_feedback_id_seq'::regclass);


--
-- Name: feedback_questions question_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.feedback_questions ALTER COLUMN question_id SET DEFAULT nextval('public.feedback_questions_question_id_seq'::regclass);


--
-- Name: force_pattern pattern_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.force_pattern ALTER COLUMN pattern_id SET DEFAULT nextval('public.force_pattern_pattern_id_seq'::regclass);


--
-- Name: goal goal_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.goal ALTER COLUMN goal_id SET DEFAULT nextval('public.goal_goal_id_seq'::regclass);


--
-- Name: meals meal_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.meals ALTER COLUMN meal_id SET DEFAULT nextval('public.meals_meal_id_seq'::regclass);


--
-- Name: mechanics mechanics_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.mechanics ALTER COLUMN mechanics_id SET DEFAULT nextval('public.mechanics_mechanics_id_seq'::regclass);


--
-- Name: movement_pattern pattern_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.movement_pattern ALTER COLUMN pattern_id SET DEFAULT nextval('public.movement_pattern_pattern_id_seq'::regclass);


--
-- Name: muscle muscle_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.muscle ALTER COLUMN muscle_id SET DEFAULT nextval('public.muscle_muscle_id_seq'::regclass);


--
-- Name: muscle_group muscle_group_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.muscle_group ALTER COLUMN muscle_group_id SET DEFAULT nextval('public.muscle_group_muscle_group_id_seq'::regclass);


--
-- Name: muscle_region muscle_region_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.muscle_region ALTER COLUMN muscle_region_id SET DEFAULT nextval('public.muscle_region_muscle_region_id_seq'::regclass);


--
-- Name: nutrition_days day_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.nutrition_days ALTER COLUMN day_id SET DEFAULT nextval('public.nutrition_days_day_id_seq'::regclass);


--
-- Name: nutrition_goals nutrition_goal_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.nutrition_goals ALTER COLUMN nutrition_goal_id SET DEFAULT nextval('public.nutrition_goals_nutrition_goal_id_seq'::regclass);


--
-- Name: nutrition_plans plan_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.nutrition_plans ALTER COLUMN plan_id SET DEFAULT nextval('public.nutrition_plans_plan_id_seq'::regclass);


--
-- Name: nutrition_weeks week_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.nutrition_weeks ALTER COLUMN week_id SET DEFAULT nextval('public.nutrition_weeks_week_id_seq'::regclass);


--
-- Name: position position_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public."position" ALTER COLUMN position_id SET DEFAULT nextval('public.position_position_id_seq'::regclass);


--
-- Name: style style_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.style ALTER COLUMN style_id SET DEFAULT nextval('public.style_style_id_seq'::regclass);


--
-- Name: training_phase phase_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.training_phase ALTER COLUMN phase_id SET DEFAULT nextval('public.training_phase_phase_id_seq'::regclass);


--
-- Name: user_auth_methods id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.user_auth_methods ALTER COLUMN id SET DEFAULT nextval('public.user_auth_methods_id_seq'::regclass);


--
-- Name: user_gym_equipment user_equipment_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.user_gym_equipment ALTER COLUMN user_equipment_id SET DEFAULT nextval('public.user_gym_equipment_user_equipment_id_seq'::regclass);


--
-- Name: user_home_equipment user_equipment_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.user_home_equipment ALTER COLUMN user_equipment_id SET DEFAULT nextval('public.user_home_equipment_user_equipment_id_seq'::regclass);


--
-- Name: user_sessions session_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.user_sessions ALTER COLUMN session_id SET DEFAULT nextval('public.user_sessions_session_id_seq'::regclass);


--
-- Name: users user_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.users ALTER COLUMN user_id SET DEFAULT nextval('public.users_user_id_seq'::regclass);


--
-- Name: verification_codes id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.verification_codes ALTER COLUMN id SET DEFAULT nextval('public.verification_codes_id_seq'::regclass);


--
-- Name: workout_day_exercises workout_day_exercise_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.workout_day_exercises ALTER COLUMN workout_day_exercise_id SET DEFAULT nextval('public.workout_day_exercises_workout_day_exercise_id_seq'::regclass);


--
-- Name: workout_days day_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.workout_days ALTER COLUMN day_id SET DEFAULT nextval('public.workout_days_day_id_seq'::regclass);


--
-- Name: workout_goals workout_goal_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.workout_goals ALTER COLUMN workout_goal_id SET DEFAULT nextval('public.workout_goals_workout_goal_id_seq'::regclass);


--
-- Name: workout_plans plan_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.workout_plans ALTER COLUMN plan_id SET DEFAULT nextval('public.workout_plans_plan_id_seq'::regclass);


--
-- Name: workout_weeks week_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.workout_weeks ALTER COLUMN week_id SET DEFAULT nextval('public.workout_weeks_week_id_seq'::regclass);


--
-- Name: alembic_version alembic_version_pkc; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.alembic_version
    ADD CONSTRAINT alembic_version_pkc PRIMARY KEY (version_num);


--
-- Name: credit_transactions credit_transactions_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.credit_transactions
    ADD CONSTRAINT credit_transactions_pkey PRIMARY KEY (transaction_id);


--
-- Name: difficulty difficulty_name_en_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.difficulty
    ADD CONSTRAINT difficulty_name_en_key UNIQUE (name_en);


--
-- Name: difficulty difficulty_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.difficulty
    ADD CONSTRAINT difficulty_pkey PRIMARY KEY (difficulty_id);


--
-- Name: equipment equipment_name_en_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.equipment
    ADD CONSTRAINT equipment_name_en_key UNIQUE (name_en);


--
-- Name: equipment equipment_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.equipment
    ADD CONSTRAINT equipment_pkey PRIMARY KEY (equipment_id);


--
-- Name: exercise_equipment exercise_equipment_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.exercise_equipment
    ADD CONSTRAINT exercise_equipment_pkey PRIMARY KEY (exercise_id, equipment_id);


--
-- Name: exercise_force_pattern exercise_force_pattern_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.exercise_force_pattern
    ADD CONSTRAINT exercise_force_pattern_pkey PRIMARY KEY (exercise_id, pattern_id);


--
-- Name: exercise_goal exercise_goal_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.exercise_goal
    ADD CONSTRAINT exercise_goal_pkey PRIMARY KEY (exercise_id, goal_id);


--
-- Name: exercise_mechanics exercise_mechanics_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.exercise_mechanics
    ADD CONSTRAINT exercise_mechanics_pkey PRIMARY KEY (exercise_id, mechanics_id);


--
-- Name: exercise_movement_pattern exercise_movement_pattern_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.exercise_movement_pattern
    ADD CONSTRAINT exercise_movement_pattern_pkey PRIMARY KEY (exercise_id, pattern_id);


--
-- Name: exercise_muscle_group exercise_muscle_group_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.exercise_muscle_group
    ADD CONSTRAINT exercise_muscle_group_pkey PRIMARY KEY (exercise_id, muscle_group_id);


--
-- Name: exercise_muscle exercise_muscle_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.exercise_muscle
    ADD CONSTRAINT exercise_muscle_pkey PRIMARY KEY (exercise_id, muscle_id);


--
-- Name: exercise_muscle_region exercise_muscle_region_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.exercise_muscle_region
    ADD CONSTRAINT exercise_muscle_region_pkey PRIMARY KEY (exercise_id, muscle_region_id);


--
-- Name: exercise exercise_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.exercise
    ADD CONSTRAINT exercise_pkey PRIMARY KEY (exercise_id);


--
-- Name: exercise_position exercise_position_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.exercise_position
    ADD CONSTRAINT exercise_position_pkey PRIMARY KEY (exercise_id, position_id);


--
-- Name: exercise_training_phase exercise_training_phase_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.exercise_training_phase
    ADD CONSTRAINT exercise_training_phase_pkey PRIMARY KEY (exercise_id, phase_id);


--
-- Name: feedback feedback_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.feedback
    ADD CONSTRAINT feedback_pkey PRIMARY KEY (feedback_id);


--
-- Name: feedback_questions feedback_questions_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.feedback_questions
    ADD CONSTRAINT feedback_questions_pkey PRIMARY KEY (question_id);


--
-- Name: force_pattern force_pattern_name_en_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.force_pattern
    ADD CONSTRAINT force_pattern_name_en_key UNIQUE (name_en);


--
-- Name: force_pattern force_pattern_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.force_pattern
    ADD CONSTRAINT force_pattern_pkey PRIMARY KEY (pattern_id);


--
-- Name: goal goal_name_en_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.goal
    ADD CONSTRAINT goal_name_en_key UNIQUE (name_en);


--
-- Name: goal goal_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.goal
    ADD CONSTRAINT goal_pkey PRIMARY KEY (goal_id);


--
-- Name: langchain_pg_collection langchain_pg_collection_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.langchain_pg_collection
    ADD CONSTRAINT langchain_pg_collection_pkey PRIMARY KEY (uuid);


--
-- Name: langchain_pg_embedding langchain_pg_embedding_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.langchain_pg_embedding
    ADD CONSTRAINT langchain_pg_embedding_pkey PRIMARY KEY (uuid);


--
-- Name: meals meals_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.meals
    ADD CONSTRAINT meals_pkey PRIMARY KEY (meal_id);


--
-- Name: mechanics mechanics_name_en_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.mechanics
    ADD CONSTRAINT mechanics_name_en_key UNIQUE (name_en);


--
-- Name: mechanics mechanics_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.mechanics
    ADD CONSTRAINT mechanics_pkey PRIMARY KEY (mechanics_id);


--
-- Name: movement_pattern movement_pattern_name_en_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.movement_pattern
    ADD CONSTRAINT movement_pattern_name_en_key UNIQUE (name_en);


--
-- Name: movement_pattern movement_pattern_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.movement_pattern
    ADD CONSTRAINT movement_pattern_pkey PRIMARY KEY (pattern_id);


--
-- Name: muscle_group muscle_group_name_en_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.muscle_group
    ADD CONSTRAINT muscle_group_name_en_key UNIQUE (name_en);


--
-- Name: muscle_group muscle_group_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.muscle_group
    ADD CONSTRAINT muscle_group_pkey PRIMARY KEY (muscle_group_id);


--
-- Name: muscle muscle_name_en_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.muscle
    ADD CONSTRAINT muscle_name_en_key UNIQUE (name_en);


--
-- Name: muscle muscle_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.muscle
    ADD CONSTRAINT muscle_pkey PRIMARY KEY (muscle_id);


--
-- Name: muscle_region muscle_region_muscle_group_id_name_en_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.muscle_region
    ADD CONSTRAINT muscle_region_muscle_group_id_name_en_key UNIQUE (muscle_group_id, name_en);


--
-- Name: muscle_region muscle_region_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.muscle_region
    ADD CONSTRAINT muscle_region_pkey PRIMARY KEY (muscle_region_id);


--
-- Name: nutrition_days nutrition_days_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.nutrition_days
    ADD CONSTRAINT nutrition_days_pkey PRIMARY KEY (day_id);


--
-- Name: nutrition_goals nutrition_goals_goal_key_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.nutrition_goals
    ADD CONSTRAINT nutrition_goals_goal_key_key UNIQUE (goal_key);


--
-- Name: nutrition_goals nutrition_goals_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.nutrition_goals
    ADD CONSTRAINT nutrition_goals_pkey PRIMARY KEY (nutrition_goal_id);


--
-- Name: nutrition_plans nutrition_plans_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.nutrition_plans
    ADD CONSTRAINT nutrition_plans_pkey PRIMARY KEY (plan_id);


--
-- Name: nutrition_weeks nutrition_weeks_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.nutrition_weeks
    ADD CONSTRAINT nutrition_weeks_pkey PRIMARY KEY (week_id);


--
-- Name: nutrition_weeks nutrition_weeks_plan_id_week_number_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.nutrition_weeks
    ADD CONSTRAINT nutrition_weeks_plan_id_week_number_key UNIQUE (plan_id, week_number);


--
-- Name: position position_name_en_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public."position"
    ADD CONSTRAINT position_name_en_key UNIQUE (name_en);


--
-- Name: position position_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public."position"
    ADD CONSTRAINT position_pkey PRIMARY KEY (position_id);


--
-- Name: style style_name_en_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.style
    ADD CONSTRAINT style_name_en_key UNIQUE (name_en);


--
-- Name: style style_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.style
    ADD CONSTRAINT style_pkey PRIMARY KEY (style_id);


--
-- Name: training_phase training_phase_name_en_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.training_phase
    ADD CONSTRAINT training_phase_name_en_key UNIQUE (name_en);


--
-- Name: training_phase training_phase_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.training_phase
    ADD CONSTRAINT training_phase_pkey PRIMARY KEY (phase_id);


--
-- Name: user_auth_methods uix_provider_identifier; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.user_auth_methods
    ADD CONSTRAINT uix_provider_identifier UNIQUE (auth_provider, auth_identifier);


--
-- Name: user_auth_methods user_auth_methods_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.user_auth_methods
    ADD CONSTRAINT user_auth_methods_pkey PRIMARY KEY (id);


--
-- Name: user_gym_equipment user_gym_equipment_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.user_gym_equipment
    ADD CONSTRAINT user_gym_equipment_pkey PRIMARY KEY (user_equipment_id);


--
-- Name: user_gym_equipment user_gym_equipment_user_id_equipment_id_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.user_gym_equipment
    ADD CONSTRAINT user_gym_equipment_user_id_equipment_id_key UNIQUE (user_id, equipment_id);


--
-- Name: user_home_equipment user_home_equipment_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.user_home_equipment
    ADD CONSTRAINT user_home_equipment_pkey PRIMARY KEY (user_equipment_id);


--
-- Name: user_home_equipment user_home_equipment_user_id_equipment_id_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.user_home_equipment
    ADD CONSTRAINT user_home_equipment_user_id_equipment_id_key UNIQUE (user_id, equipment_id);


--
-- Name: user_sessions user_sessions_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.user_sessions
    ADD CONSTRAINT user_sessions_pkey PRIMARY KEY (session_id);


--
-- Name: user_sessions user_sessions_session_token_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.user_sessions
    ADD CONSTRAINT user_sessions_session_token_key UNIQUE (session_token);


--
-- Name: users users_email_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_email_key UNIQUE (email);


--
-- Name: users users_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_pkey PRIMARY KEY (user_id);


--
-- Name: users users_referral_code_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_referral_code_key UNIQUE (referral_code);


--
-- Name: verification_codes verification_codes_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.verification_codes
    ADD CONSTRAINT verification_codes_pkey PRIMARY KEY (id);


--
-- Name: workout_day_exercises workout_day_exercises_day_id_exercise_order_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.workout_day_exercises
    ADD CONSTRAINT workout_day_exercises_day_id_exercise_order_key UNIQUE (day_id, exercise_order);


--
-- Name: workout_day_exercises workout_day_exercises_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.workout_day_exercises
    ADD CONSTRAINT workout_day_exercises_pkey PRIMARY KEY (workout_day_exercise_id);


--
-- Name: workout_days workout_days_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.workout_days
    ADD CONSTRAINT workout_days_pkey PRIMARY KEY (day_id);


--
-- Name: workout_goals workout_goals_goal_key_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.workout_goals
    ADD CONSTRAINT workout_goals_goal_key_key UNIQUE (goal_key);


--
-- Name: workout_goals workout_goals_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.workout_goals
    ADD CONSTRAINT workout_goals_pkey PRIMARY KEY (workout_goal_id);


--
-- Name: workout_plans workout_plans_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.workout_plans
    ADD CONSTRAINT workout_plans_pkey PRIMARY KEY (plan_id);


--
-- Name: workout_weeks workout_weeks_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.workout_weeks
    ADD CONSTRAINT workout_weeks_pkey PRIMARY KEY (week_id);


--
-- Name: workout_weeks workout_weeks_plan_id_week_number_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.workout_weeks
    ADD CONSTRAINT workout_weeks_plan_id_week_number_key UNIQUE (plan_id, week_number);


--
-- Name: idx_exercise_movement_pattern_exercise; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_exercise_movement_pattern_exercise ON public.exercise_movement_pattern USING btree (exercise_id);


--
-- Name: idx_exercise_movement_pattern_pattern; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_exercise_movement_pattern_pattern ON public.exercise_movement_pattern USING btree (pattern_id);


--
-- Name: idx_exercise_muscle_group_exercise; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_exercise_muscle_group_exercise ON public.exercise_muscle_group USING btree (exercise_id);


--
-- Name: idx_exercise_muscle_group_group; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_exercise_muscle_group_group ON public.exercise_muscle_group USING btree (muscle_group_id);


--
-- Name: idx_exercise_muscle_region_exercise; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_exercise_muscle_region_exercise ON public.exercise_muscle_region USING btree (exercise_id);


--
-- Name: idx_exercise_muscle_region_region; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_exercise_muscle_region_region ON public.exercise_muscle_region USING btree (muscle_region_id);


--
-- Name: idx_feedback_questions_focus; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_feedback_questions_focus ON public.feedback_questions USING btree (focus);


--
-- Name: idx_feedback_questions_order; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_feedback_questions_order ON public.feedback_questions USING btree (week_table, week_number, question_order);


--
-- Name: idx_feedback_questions_week; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_feedback_questions_week ON public.feedback_questions USING btree (week_table, week_number);


--
-- Name: idx_feedback_submitted; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_feedback_submitted ON public.feedback USING btree (submitted_at);


--
-- Name: idx_feedback_user; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_feedback_user ON public.feedback USING btree (user_id);


--
-- Name: idx_feedback_week; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_feedback_week ON public.feedback USING btree (week_table, week_id);


--
-- Name: idx_meals_day; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_meals_day ON public.meals USING btree (day_id);


--
-- Name: idx_meals_type; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_meals_type ON public.meals USING btree (day_id, meal_type);


--
-- Name: idx_muscle_region_group; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_muscle_region_group ON public.muscle_region USING btree (muscle_group_id);


--
-- Name: idx_nutrition_days_week; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_nutrition_days_week ON public.nutrition_days USING btree (week_id);


--
-- Name: idx_nutrition_goals_focus; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_nutrition_goals_focus ON public.nutrition_goals USING btree (focus);


--
-- Name: idx_nutrition_goals_key; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_nutrition_goals_key ON public.nutrition_goals USING btree (goal_key);


--
-- Name: idx_nutrition_plans_created; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_nutrition_plans_created ON public.nutrition_plans USING btree (created_at);


--
-- Name: idx_nutrition_plans_user; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_nutrition_plans_user ON public.nutrition_plans USING btree (user_id);


--
-- Name: idx_nutrition_weeks_number; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_nutrition_weeks_number ON public.nutrition_weeks USING btree (plan_id, week_number);


--
-- Name: idx_nutrition_weeks_plan; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_nutrition_weeks_plan ON public.nutrition_weeks USING btree (plan_id);


--
-- Name: idx_sessions_expires; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_sessions_expires ON public.user_sessions USING btree (expires_at);


--
-- Name: idx_sessions_token; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_sessions_token ON public.user_sessions USING btree (session_token);


--
-- Name: idx_sessions_user; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_sessions_user ON public.user_sessions USING btree (user_id);


--
-- Name: idx_transactions_created; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_transactions_created ON public.credit_transactions USING btree (created_at);


--
-- Name: idx_transactions_type; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_transactions_type ON public.credit_transactions USING btree (transaction_type);


--
-- Name: idx_transactions_user; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_transactions_user ON public.credit_transactions USING btree (user_id);


--
-- Name: idx_user_equipment_equipment; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_user_equipment_equipment ON public.user_home_equipment USING btree (equipment_id);


--
-- Name: idx_user_equipment_user; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_user_equipment_user ON public.user_home_equipment USING btree (user_id);


--
-- Name: idx_user_gym_equipment_equipment; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_user_gym_equipment_equipment ON public.user_gym_equipment USING btree (equipment_id);


--
-- Name: idx_user_gym_equipment_user; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_user_gym_equipment_user ON public.user_gym_equipment USING btree (user_id);


--
-- Name: idx_users_created_at; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_users_created_at ON public.users USING btree (created_at);


--
-- Name: idx_users_email; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_users_email ON public.users USING btree (email);


--
-- Name: idx_users_referral_code; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_users_referral_code ON public.users USING btree (referral_code);


--
-- Name: idx_workout_day_exercises_day; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_workout_day_exercises_day ON public.workout_day_exercises USING btree (day_id);


--
-- Name: idx_workout_day_exercises_exercise; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_workout_day_exercises_exercise ON public.workout_day_exercises USING btree (exercise_id);


--
-- Name: idx_workout_day_exercises_order; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_workout_day_exercises_order ON public.workout_day_exercises USING btree (day_id, exercise_order);


--
-- Name: idx_workout_days_week; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_workout_days_week ON public.workout_days USING btree (week_id);


--
-- Name: idx_workout_goals_focus; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_workout_goals_focus ON public.workout_goals USING btree (focus);


--
-- Name: idx_workout_goals_key; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_workout_goals_key ON public.workout_goals USING btree (goal_key);


--
-- Name: idx_workout_plans_created; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_workout_plans_created ON public.workout_plans USING btree (created_at);


--
-- Name: idx_workout_plans_user; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_workout_plans_user ON public.workout_plans USING btree (user_id);


--
-- Name: idx_workout_weeks_number; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_workout_weeks_number ON public.workout_weeks USING btree (plan_id, week_number);


--
-- Name: idx_workout_weeks_plan; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_workout_weeks_plan ON public.workout_weeks USING btree (plan_id);


--
-- Name: ix_user_auth_methods_auth_identifier; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_user_auth_methods_auth_identifier ON public.user_auth_methods USING btree (auth_identifier);


--
-- Name: ix_user_auth_methods_user_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_user_auth_methods_user_id ON public.user_auth_methods USING btree (user_id);


--
-- Name: ix_users_telegram_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX ix_users_telegram_id ON public.users USING btree (telegram_id);


--
-- Name: ix_verification_codes_identifier; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_verification_codes_identifier ON public.verification_codes USING btree (identifier);


--
-- Name: credit_transactions trigger_update_credits; Type: TRIGGER; Schema: public; Owner: postgres
--

CREATE TRIGGER trigger_update_credits AFTER INSERT ON public.credit_transactions FOR EACH ROW EXECUTE FUNCTION public.update_user_credits();


--
-- Name: users update_users_modtime; Type: TRIGGER; Schema: public; Owner: postgres
--

CREATE TRIGGER update_users_modtime BEFORE UPDATE ON public.users FOR EACH ROW EXECUTE FUNCTION public.update_modified_column();


--
-- Name: credit_transactions credit_transactions_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.credit_transactions
    ADD CONSTRAINT credit_transactions_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(user_id) ON DELETE CASCADE;


--
-- Name: exercise exercise_difficulty_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.exercise
    ADD CONSTRAINT exercise_difficulty_id_fkey FOREIGN KEY (difficulty_id) REFERENCES public.difficulty(difficulty_id);


--
-- Name: exercise_equipment exercise_equipment_equipment_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.exercise_equipment
    ADD CONSTRAINT exercise_equipment_equipment_id_fkey FOREIGN KEY (equipment_id) REFERENCES public.equipment(equipment_id) ON DELETE CASCADE;


--
-- Name: exercise_equipment exercise_equipment_exercise_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.exercise_equipment
    ADD CONSTRAINT exercise_equipment_exercise_id_fkey FOREIGN KEY (exercise_id) REFERENCES public.exercise(exercise_id) ON DELETE CASCADE;


--
-- Name: exercise_force_pattern exercise_force_pattern_exercise_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.exercise_force_pattern
    ADD CONSTRAINT exercise_force_pattern_exercise_id_fkey FOREIGN KEY (exercise_id) REFERENCES public.exercise(exercise_id) ON DELETE CASCADE;


--
-- Name: exercise_force_pattern exercise_force_pattern_pattern_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.exercise_force_pattern
    ADD CONSTRAINT exercise_force_pattern_pattern_id_fkey FOREIGN KEY (pattern_id) REFERENCES public.force_pattern(pattern_id) ON DELETE CASCADE;


--
-- Name: exercise_goal exercise_goal_exercise_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.exercise_goal
    ADD CONSTRAINT exercise_goal_exercise_id_fkey FOREIGN KEY (exercise_id) REFERENCES public.exercise(exercise_id) ON DELETE CASCADE;


--
-- Name: exercise_goal exercise_goal_goal_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.exercise_goal
    ADD CONSTRAINT exercise_goal_goal_id_fkey FOREIGN KEY (goal_id) REFERENCES public.goal(goal_id) ON DELETE CASCADE;


--
-- Name: exercise_mechanics exercise_mechanics_exercise_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.exercise_mechanics
    ADD CONSTRAINT exercise_mechanics_exercise_id_fkey FOREIGN KEY (exercise_id) REFERENCES public.exercise(exercise_id) ON DELETE CASCADE;


--
-- Name: exercise_mechanics exercise_mechanics_mechanics_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.exercise_mechanics
    ADD CONSTRAINT exercise_mechanics_mechanics_id_fkey FOREIGN KEY (mechanics_id) REFERENCES public.mechanics(mechanics_id) ON DELETE CASCADE;


--
-- Name: exercise_movement_pattern exercise_movement_pattern_exercise_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.exercise_movement_pattern
    ADD CONSTRAINT exercise_movement_pattern_exercise_id_fkey FOREIGN KEY (exercise_id) REFERENCES public.exercise(exercise_id) ON DELETE CASCADE;


--
-- Name: exercise_movement_pattern exercise_movement_pattern_pattern_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.exercise_movement_pattern
    ADD CONSTRAINT exercise_movement_pattern_pattern_id_fkey FOREIGN KEY (pattern_id) REFERENCES public.movement_pattern(pattern_id) ON DELETE CASCADE;


--
-- Name: exercise_muscle exercise_muscle_exercise_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.exercise_muscle
    ADD CONSTRAINT exercise_muscle_exercise_id_fkey FOREIGN KEY (exercise_id) REFERENCES public.exercise(exercise_id) ON DELETE CASCADE;


--
-- Name: exercise_muscle_group exercise_muscle_group_exercise_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.exercise_muscle_group
    ADD CONSTRAINT exercise_muscle_group_exercise_id_fkey FOREIGN KEY (exercise_id) REFERENCES public.exercise(exercise_id) ON DELETE CASCADE;


--
-- Name: exercise_muscle_group exercise_muscle_group_muscle_group_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.exercise_muscle_group
    ADD CONSTRAINT exercise_muscle_group_muscle_group_id_fkey FOREIGN KEY (muscle_group_id) REFERENCES public.muscle_group(muscle_group_id) ON DELETE CASCADE;


--
-- Name: exercise_muscle exercise_muscle_muscle_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.exercise_muscle
    ADD CONSTRAINT exercise_muscle_muscle_id_fkey FOREIGN KEY (muscle_id) REFERENCES public.muscle(muscle_id) ON DELETE CASCADE;


--
-- Name: exercise_muscle_region exercise_muscle_region_exercise_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.exercise_muscle_region
    ADD CONSTRAINT exercise_muscle_region_exercise_id_fkey FOREIGN KEY (exercise_id) REFERENCES public.exercise(exercise_id) ON DELETE CASCADE;


--
-- Name: exercise_muscle_region exercise_muscle_region_muscle_region_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.exercise_muscle_region
    ADD CONSTRAINT exercise_muscle_region_muscle_region_id_fkey FOREIGN KEY (muscle_region_id) REFERENCES public.muscle_region(muscle_region_id) ON DELETE CASCADE;


--
-- Name: exercise_position exercise_position_exercise_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.exercise_position
    ADD CONSTRAINT exercise_position_exercise_id_fkey FOREIGN KEY (exercise_id) REFERENCES public.exercise(exercise_id) ON DELETE CASCADE;


--
-- Name: exercise_position exercise_position_position_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.exercise_position
    ADD CONSTRAINT exercise_position_position_id_fkey FOREIGN KEY (position_id) REFERENCES public."position"(position_id) ON DELETE CASCADE;


--
-- Name: exercise exercise_style_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.exercise
    ADD CONSTRAINT exercise_style_id_fkey FOREIGN KEY (style_id) REFERENCES public.style(style_id);


--
-- Name: exercise_training_phase exercise_training_phase_exercise_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.exercise_training_phase
    ADD CONSTRAINT exercise_training_phase_exercise_id_fkey FOREIGN KEY (exercise_id) REFERENCES public.exercise(exercise_id) ON DELETE CASCADE;


--
-- Name: exercise_training_phase exercise_training_phase_phase_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.exercise_training_phase
    ADD CONSTRAINT exercise_training_phase_phase_id_fkey FOREIGN KEY (phase_id) REFERENCES public.training_phase(phase_id) ON DELETE CASCADE;


--
-- Name: feedback feedback_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.feedback
    ADD CONSTRAINT feedback_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(user_id) ON DELETE CASCADE;


--
-- Name: langchain_pg_embedding langchain_pg_embedding_collection_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.langchain_pg_embedding
    ADD CONSTRAINT langchain_pg_embedding_collection_id_fkey FOREIGN KEY (collection_id) REFERENCES public.langchain_pg_collection(uuid) ON DELETE CASCADE;


--
-- Name: meals meals_day_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.meals
    ADD CONSTRAINT meals_day_id_fkey FOREIGN KEY (day_id) REFERENCES public.nutrition_days(day_id) ON DELETE CASCADE;


--
-- Name: muscle_region muscle_region_muscle_group_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.muscle_region
    ADD CONSTRAINT muscle_region_muscle_group_id_fkey FOREIGN KEY (muscle_group_id) REFERENCES public.muscle_group(muscle_group_id) ON DELETE CASCADE;


--
-- Name: nutrition_days nutrition_days_week_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.nutrition_days
    ADD CONSTRAINT nutrition_days_week_id_fkey FOREIGN KEY (week_id) REFERENCES public.nutrition_weeks(week_id) ON DELETE CASCADE;


--
-- Name: nutrition_plans nutrition_plans_nutrition_goal_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.nutrition_plans
    ADD CONSTRAINT nutrition_plans_nutrition_goal_id_fkey FOREIGN KEY (nutrition_goal_id) REFERENCES public.nutrition_goals(nutrition_goal_id) ON DELETE SET NULL;


--
-- Name: nutrition_plans nutrition_plans_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.nutrition_plans
    ADD CONSTRAINT nutrition_plans_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(user_id) ON DELETE CASCADE;


--
-- Name: nutrition_weeks nutrition_weeks_plan_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.nutrition_weeks
    ADD CONSTRAINT nutrition_weeks_plan_id_fkey FOREIGN KEY (plan_id) REFERENCES public.nutrition_plans(plan_id) ON DELETE CASCADE;


--
-- Name: user_auth_methods user_auth_methods_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.user_auth_methods
    ADD CONSTRAINT user_auth_methods_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(user_id) ON DELETE CASCADE;


--
-- Name: user_gym_equipment user_gym_equipment_equipment_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.user_gym_equipment
    ADD CONSTRAINT user_gym_equipment_equipment_id_fkey FOREIGN KEY (equipment_id) REFERENCES public.equipment(equipment_id) ON DELETE CASCADE;


--
-- Name: user_gym_equipment user_gym_equipment_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.user_gym_equipment
    ADD CONSTRAINT user_gym_equipment_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(user_id) ON DELETE CASCADE;


--
-- Name: user_home_equipment user_home_equipment_equipment_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.user_home_equipment
    ADD CONSTRAINT user_home_equipment_equipment_id_fkey FOREIGN KEY (equipment_id) REFERENCES public.equipment(equipment_id) ON DELETE CASCADE;


--
-- Name: user_home_equipment user_home_equipment_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.user_home_equipment
    ADD CONSTRAINT user_home_equipment_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(user_id) ON DELETE CASCADE;


--
-- Name: user_sessions user_sessions_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.user_sessions
    ADD CONSTRAINT user_sessions_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(user_id) ON DELETE CASCADE;


--
-- Name: users users_nutrition_goal_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_nutrition_goal_id_fkey FOREIGN KEY (nutrition_goal_id) REFERENCES public.nutrition_goals(nutrition_goal_id) ON DELETE SET NULL;


--
-- Name: users users_workout_goal_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_workout_goal_id_fkey FOREIGN KEY (workout_goal_id) REFERENCES public.workout_goals(workout_goal_id) ON DELETE SET NULL;


--
-- Name: workout_day_exercises workout_day_exercises_day_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.workout_day_exercises
    ADD CONSTRAINT workout_day_exercises_day_id_fkey FOREIGN KEY (day_id) REFERENCES public.workout_days(day_id) ON DELETE CASCADE;


--
-- Name: workout_day_exercises workout_day_exercises_exercise_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.workout_day_exercises
    ADD CONSTRAINT workout_day_exercises_exercise_id_fkey FOREIGN KEY (exercise_id) REFERENCES public.exercise(exercise_id) ON DELETE CASCADE;


--
-- Name: workout_days workout_days_week_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.workout_days
    ADD CONSTRAINT workout_days_week_id_fkey FOREIGN KEY (week_id) REFERENCES public.workout_weeks(week_id) ON DELETE CASCADE;


--
-- Name: workout_plans workout_plans_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.workout_plans
    ADD CONSTRAINT workout_plans_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(user_id) ON DELETE CASCADE;


--
-- Name: workout_plans workout_plans_workout_goal_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.workout_plans
    ADD CONSTRAINT workout_plans_workout_goal_id_fkey FOREIGN KEY (workout_goal_id) REFERENCES public.workout_goals(workout_goal_id) ON DELETE SET NULL;


--
-- Name: workout_weeks workout_weeks_plan_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.workout_weeks
    ADD CONSTRAINT workout_weeks_plan_id_fkey FOREIGN KEY (plan_id) REFERENCES public.workout_plans(plan_id) ON DELETE CASCADE;


--
-- PostgreSQL database dump complete
--

\unrestrict mqF1IQHDSSBB61JohZzKVbo0Jb1h0grVpe18XvEWjx33hkSadFLbNKcTMsIpTh9


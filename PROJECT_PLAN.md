# MovoAI Backend API - 4-Phase Development Plan

**Project**: FastAPI Backend for MovoAI Fitness Application  
**Database**: PostgreSQL (located at `/Zitan/database/`)  
**Frontend**: React/TypeScript (located at `/MovoAI/`)  
**Tech Stack**: FastAPI, PostgreSQL, LangChain, Pydantic, SQLAlchemy

---

## Project Overview

This document outlines a 4-phase incremental development approach for building the MovoAI backend API. Each phase is designed to be:
- **Self-contained**: Deliverable and testable independently
- **Frontend-integrated**: Testable with the frontend after completion
- **Production-ready**: Fully functional before moving to the next phase

**Database Schema Reference**: `/schema.sql` contains tables for users, exercises, workout_plans, plan_exercises, user_plans, and user_workout_logs.

---

## 🔵 PHASE 1: Foundation & Exercise/Workout APIs (No Auth Required)

### Objective
Establish the core backend infrastructure and implement public exercise library and workout plan browsing. **No authentication required** - allow Telegram/web users to explore content freely.

### AI Prompt for Phase 1

```
Create a FastAPI backend project at /movoai_api/ with the following requirements:

PROJECT STRUCTURE:
- app/
  - main.py (FastAPI application entry point)
  - config.py (Database connection, environment variables)
  - dependencies.py (Optional auth support, DB sessions)
  - models/
    - exercise.py (SQLAlchemy Exercise model)
    - workout_plan.py (SQLAlchemy WorkoutPlan model)
    - plan_exercise.py (SQLAlchemy PlanExercise model)
  - schemas/
    - exercise.py (Pydantic schemas for Exercise)
    - workout_plan.py (Pydantic schemas for WorkoutPlan)
  - api/
    - v1/
      - endpoints/
        - exercises.py (Public exercise endpoints - NO AUTH)
        - workout_plans.py (Public workout plan browsing - NO AUTH)
      - api.py (API router aggregator)
  - database/
    - session.py (Database session management)
    - base.py (SQLAlchemy declarative base)
  - core/
    - config.py (Settings management with pydantic-settings)
- tests/
  - test_exercises.py (Unit tests for exercise endpoints)
  - test_workout_plans.py (Unit tests for workout plan endpoints)
- .env.example (Template for environment variables)
- requirements.txt (FastAPI, SQLAlchemy, PostgreSQL driver)
- README.md (Setup instructions)

DATABASE CONNECTION:
- Connect to PostgreSQL database at /Zitan/database/
- Use existing tables: exercises, workout_plans, plan_exercises
- Implement connection pooling
- Add database migrations support (Alembic)

EXERCISE LIBRARY ENDPOINTS (PUBLIC - NO AUTH):
1. GET /api/v1/exercises
   - List all exercises with pagination
   - Query parameters: difficulty, goal, muscles, equipment, search
   - Support English and French (exercise_en, exercise_fr)
   - Return: id, exercise_en/fr, difficulty, goal, muscles, instructions, equipments, gif URLs
   - NO AUTHENTICATION REQUIRED
   
2. GET /api/v1/exercises/{exercise_id}
   - Get single exercise details
   - Include male_gif_urls and female_gif_urls
   - NO AUTHENTICATION REQUIRED
   
3. GET /api/v1/exercises/search
   - Search exercises by name, muscle group, equipment
   - Full-text search capability
   - NO AUTHENTICATION REQUIRED
   
4. GET /api/v1/exercises/filter
   - Advanced filtering: difficulty, goal, muscles[], equipment[]
   - Support multiple muscle groups and equipment types
   - NO AUTHENTICATION REQUIRED

WORKOUT PLAN ENDPOINTS (PUBLIC - NO AUTH):
1. GET /api/v1/workout-plans
   - List all template workout plans (is_template=true)
   - Include plan name, description (EN/FR), exercise count, weeks
   - Pagination support
   - NO AUTHENTICATION REQUIRED
   
2. GET /api/v1/workout-plans/{plan_id}
   - Get detailed plan with all exercises
   - Return: plan details + list of plan_exercises with exercise info
   - Include day_number, week_number, sets, reps, duration, rest, order
   - Group by weeks and days
   - NO AUTHENTICATION REQUIRED
   
3. GET /api/v1/workout-plans/featured
   - Get featured/recommended workout plans
   - NO AUTHENTICATION REQUIRED

ANONYMOUS/GUEST SESSION (OPTIONAL):
- Allow users to browse all content without login
- Later phases can add session-based tracking for guest users
- Store guest preferences in browser localStorage (frontend)

SECURITY:
- Add middleware for CORS (allow frontend origin at /MovoAI/)
- Input validation with Pydantic models
- SQL injection protection via SQLAlchemy ORM
- Rate limiting: 100 requests per minute per IP (generous for public API)
- No sensitive data exposure in public endpoints

ERROR HANDLING:
- Custom exception handlers for 400, 404, 422, 500
- Structured JSON error responses
- Logging for all errors

TESTING:
- Write pytest tests for all endpoints
- Mock database connections
- Test pagination and filtering
- Test search functionality

DOCUMENTATION:
- Auto-generated OpenAPI docs at /docs
- Add detailed descriptions for all endpoints
- Include example requests/responses
- Emphasize public/no-auth nature of endpoints

PERFORMANCE OPTIMIZATIONS:
- Database indexing on: difficulty, goal, muscles, equipment
- Caching for exercise library (rarely changes)
- Eager loading for workout plans with exercises
- Response compression

DEPLOYMENT READINESS:
- Environment variable configuration (.env file):
  - DATABASE_URL
  - FRONTEND_URL (for CORS)
- Docker support (optional Dockerfile)
- Health check endpoint: GET /health
- Logging configuration (structured JSON logs)
```

### Phase 1 Deliverables
✅ Exercise library fully accessible (no auth)  
✅ Workout plan browsing functional (no auth)  
✅ Search and filtering working smoothly  
✅ Database connection established  
✅ API documentation accessible at `/docs`  
✅ Unit tests passing for all endpoints  
✅ **Frontend Integration Test**: Browse exercises, view workout plans, search/filter from Telegram/web without login

### Frontend Testing Checklist Phase 1
- [ ] Users can browse exercise library without login
- [ ] Exercise search returns relevant results
- [ ] Exercise filtering by muscle, difficulty, equipment works
- [ ] Users can view workout plan templates
- [ ] Workout plan details show all exercises grouped by week/day
- [ ] GIF animations display correctly
- [ ] Multi-language support (EN/FR) works
- [ ] Pagination works smoothly
- [ ] Fast response times (<300ms for lists)

---

## 🟢 PHASE 2: User Workout Tracking (Session-Based, Optional Auth)

### Objective
Implement workout logging, user plan assignment, and progress tracking. Support both **guest sessions** (browser storage) and **optional lightweight auth** (simple user ID) for data persistence.

### AI Prompt for Phase 2

```
Extend the FastAPI backend at /movoai_api/ to add user workout tracking with minimal auth:

NEW MODELS (app/models/):
- user.py (Minimal user model: id, created_at, last_active)
- user_plan.py (SQLAlchemy model for user_plans table)
- workout_log.py (SQLAlchemy model for user_workout_logs table)
- guest_session.py (Optional: track anonymous sessions)

NEW SCHEMAS (app/schemas/):
- user.py (Minimal user schemas)
- user_plan.py (Pydantic schemas for user plans)
- workout_log.py (Pydantic schemas for workout logs)

MINIMAL USER SYSTEM:
- Simple user creation: POST /api/v1/users (no password, just returns user_id)
- User can be created on-demand when first action needs persistence
- No password, no email, no complex auth - just an ID
- Frontend stores user_id in localStorage
- Optional: Generate anonymous guest_id for browser tracking

USER WORKOUT PLAN ENDPOINTS (OPTIONAL AUTH):
1. POST /api/v1/users/{user_id}/plans
   - Assign workout plan to user
   - Require: plan_id, start_date
   - Set status to 'active'
   - NO JWT required, just user_id in path
   
2. GET /api/v1/users/{user_id}/plans
   - Get all workout plans assigned to user
   - Filter by status: active, completed, paused
   - NO JWT required
   
3. GET /api/v1/users/{user_id}/plans/{user_plan_id}
   - Get detailed user plan with progress
   - Include workout logs for each exercise
   - NO JWT required
   
4. PUT /api/v1/users/{user_id}/plans/{user_plan_id}
   - Update user plan status (active, completed, paused)
   - NO JWT required
   
5. DELETE /api/v1/users/{user_id}/plans/{user_plan_id}
   - Remove plan from user
   - NO JWT required

WORKOUT LOGGING ENDPOINTS (OPTIONAL AUTH):
1. POST /api/v1/users/{user_id}/workout-logs
   - Log completed workout
   - Require: plan_exercise_id, date_performed, sets_completed, reps_completed
   - NO JWT required
   
2. GET /api/v1/users/{user_id}/workout-logs
   - Get user's workout history
   - Query params: start_date, end_date, plan_exercise_id
   - NO JWT required
   
3. GET /api/v1/users/{user_id}/progress
   - Get workout progress statistics
   - Return: total workouts, exercises completed, workout streak, weekly summary
   - NO JWT required
   
4. PUT /api/v1/users/{user_id}/workout-logs/{log_id}
   - Edit workout log entry
   - NO JWT required
   
5. DELETE /api/v1/users/{user_id}/workout-logs/{log_id}
   - Delete workout log entry
   - NO JWT required

SIMPLE USER CREATION:
1. POST /api/v1/users
   - Create new anonymous user
   - No input required (or optional: telegram_id, guest_id)
   - Return: user_id, created_at
   - Frontend stores user_id in localStorage
   
2. GET /api/v1/users/{user_id}
   - Get basic user info
   - Return: user_id, created_at, workout_count, plan_count
   - NO JWT required

GUEST SESSION SUPPORT:
- Frontend can work completely offline with localStorage
- When user wants to persist data: call POST /api/v1/users, get user_id
- User can "claim" their data later by linking auth (Phase 4)
- Optional: POST /api/v1/users/{user_id}/migrate to merge guest data

BUSINESS LOGIC:
- No complex auth validation, just check user_id exists
- Rate limiting per IP to prevent abuse (100 req/min)
- User can only access data if they know the user_id (security by obscurity for now)
- Phase 4 will add proper auth and ownership validation

PERFORMANCE OPTIMIZATIONS:
- Eager loading for related entities (plans with exercises)
- Database indexing on foreign keys (user_id, plan_id)
- Pagination for large result sets
- Cache user progress calculations

TESTING:
- Test CRUD operations for all new endpoints
- Test user creation flow
- Test workout logging without auth
- Test progress calculations
- Integration tests with database

DOCUMENTATION:
- Update OpenAPI docs with new endpoints
- Emphasize minimal auth approach
- Document migration path for Phase 4 auth
- Include examples for frontend localStorage usage
```

### Phase 2 Deliverables
✅ Minimal user system (just ID, no passwords)  
✅ User can assign workout plans to themselves  
✅ Workout logging functional without JWT  
✅ Progress tracking and statistics  
✅ Frontend can store user_id in localStorage  
✅ All endpoints tested with pytest  
✅ **Frontend Integration Test**: Create user, assign plan, log workouts, view progress - all without login

### Frontend Testing Checklist Phase 2
- [ ] User can create anonymous account (just get user_id)
- [ ] User_id persists in localStorage
- [ ] User can assign workout plan to themselves
- [ ] User can log completed workouts
- [ ] User can view workout history and progress
- [ ] Multi-week plans track progress correctly
- [ ] No login/password required for any action
- [ ] Works seamlessly from Telegram WebApp

---

## 🟡 PHASE 3: AI Agent Foundation (No Auth Required)

### Objective
Integrate LangChain for AI-powered workout recommendations, implement conversation management, and create intelligent fitness coaching. **Works with or without user_id** - AI can provide recommendations to anyone.

### AI Prompt for Phase 3

```
Extend the FastAPI backend at /movoai_api/ to add AI agent capabilities using LangChain:

DEPENDENCIES:
Add to requirements.txt:
- langchain>=0.1.0
- langchain-openai>=0.0.2
- langchain-community>=0.0.10
- openai>=1.0.0
- chromadb>=0.4.0 (for vector storage)
- tiktoken>=0.5.0 (for token counting)

NEW MODELS (app/models/):
- conversation.py (Store user conversation history)
  - Fields: id, user_id, message, role (user/assistant), timestamp, context_data (JSON)
- agent_session.py (Track AI agent sessions)
  - Fields: id, user_id, session_type (recommendation/coaching/planning), started_at, ended_at, status
- recommendation.py (Store AI-generated recommendations)
  - Fields: id, user_id, recommendation_type, recommendation_data (JSON), confidence_score, created_at

NEW SCHEMAS (app/schemas/):
- conversation.py (Pydantic schemas)
- agent_session.py (Pydantic schemas)
- recommendation.py (Pydantic schemas)

AI AGENT CORE (app/ai/):
- agent_manager.py (Main AI agent orchestrator)
- prompts.py (LangChain prompt templates)
- chains.py (LangChain chain definitions)
- memory.py (Conversation memory management)
- tools.py (LangChain tools for database queries)
- embeddings.py (Vector embeddings for exercises and plans)

LANGCHAIN INTEGRATION:
1. Initialize OpenAI LLM (or other provider)
   - Support for GPT-4, GPT-3.5-turbo
   - Temperature and max_tokens configuration
   
2. Create LangChain Tools:
   - get_user_profile_tool: Fetch user fitness data
   - search_exercises_tool: Search exercises by criteria
   - get_workout_history_tool: Retrieve user's workout logs
   - calculate_fitness_metrics_tool: Calculate BMI, progress, etc.
   
3. Build Conversation Chain:
   - Use ConversationBufferMemory for context
   - Integrate tools via ReActAgent or OpenAIFunctionsAgent
   - Maintain conversation history per user
   
4. Create Prompt Templates:
   - Fitness coaching persona
   - Workout recommendation template
   - Progress analysis template
   - Motivational messaging template

AI RECOMMENDATION ENDPOINTS (PUBLIC - NO AUTH):
1. POST /api/v1/ai/recommend-workout
   - Input: user preferences, goals, available equipment, time constraints, optional user_id
   - Output: Personalized workout plan with exercises
   - Use LangChain to generate recommendations
   - If user_id provided, can consider their history
   - NO AUTH REQUIRED
   
2. POST /api/v1/ai/analyze-progress
   - Input: user_id (optional), workout history or date_range
   - Output: AI-generated progress analysis, insights, suggestions
   - Works with or without user_id (can analyze provided data)
   - NO AUTH REQUIRED
   
3. POST /api/v1/ai/suggest-exercises
   - Input: target muscles, difficulty, equipment, optional context
   - Output: List of exercises with AI-generated reasoning
   - Use vector similarity search on exercise embeddings
   - NO AUTH REQUIRED

AI CONVERSATION ENDPOINTS (PUBLIC - OPTIONAL USER TRACKING):
1. POST /api/v1/ai/chat
   - Input: user message, optional user_id or session_id
   - Output: AI assistant response
   - Maintain conversation context (in-memory or session-based)
   - Optionally save conversation if user_id provided
   - NO AUTH REQUIRED
   
2. GET /api/v1/ai/conversations/{session_id}
   - Get conversation by session_id (temporary, 24hr expiry)
   - NO AUTH REQUIRED
   
3. GET /api/v1/users/{user_id}/conversations (OPTIONAL)
   - Get user's conversation history (if user_id exists)
   - NO AUTH REQUIRED
   
4. POST /api/v1/ai/session/start
   - Start new AI coaching session
   - Return session_id (can be anonymous)
   - NO AUTH REQUIRED
   
5. POST /api/v1/ai/session/{session_id}/end
   - End AI coaching session
   - Save session summary (if user_id linked)
   - NO AUTH REQUIRED

AI AGENT BUSINESS LOGIC:
- User Context Awareness:
  - Load user profile, goals, history before AI interaction
  - Pass relevant context to LangChain prompts
  
- Recommendation Engine:
  - Use user's fitness_level, goals, workout_style
  - Consider available equipment from exercises table
  - Generate plans matching user's daily_activity
  
- Safety & Validation:
  - Validate AI-generated workout plans
  - Ensure exercises exist in database
  - Check for exercise contraindications based on fitness level
  
- Conversation Memory:
  - Store last 10 messages for context
  - Summarize long conversations
  - Clear memory on session end

VECTOR EMBEDDINGS:
- Create embeddings for all exercises (instructions, muscles, goals)
- Store in ChromaDB or PostgreSQL with pgvector extension
- Enable semantic search for exercises
- Use for exercise recommendation similarity

PROMPT ENGINEERING:
- System prompt defines AI as fitness coach
- Include user profile in context window
- Use few-shot examples for consistent responses
- Structure outputs as JSON for parsing

ERROR HANDLING:
- Handle OpenAI API errors gracefully
- Fallback to rule-based recommendations if AI fails
- Rate limiting on AI endpoints
- Timeout handling for long LLM responses

COST MANAGEMENT:
- Token usage tracking and logging
- Set max_tokens limit per request
- Cache common AI responses
- Use cheaper models (GPT-3.5) for simple queries

TESTING:
- Mock OpenAI API calls in tests
- Test conversation memory persistence
- Test tool calling functionality
- Test recommendation validation logic
- Integration tests for AI endpoints

CONFIGURATION:
- Add OPENAI_API_KEY to .env
- Add LLM model selection (GPT_MODEL)
- Add temperature and max_tokens settings
- Add vector database connection settings

DOCUMENTATION:
- Document AI capabilities and limitations
- Provide example prompts for users
- Document conversation flow
- Include AI response schemas
```

### Phase 3 Deliverables
✅ LangChain integration functional  
✅ AI-powered workout recommendations  
✅ Conversation management system  
✅ Progress analysis with AI insights  
✅ Vector-based exercise search  
✅ All AI endpoints tested  
✅ **Frontend Integration Test**: Chat with AI coach, get recommendations, analyze progress from `/MovoAI/`

### Frontend Testing Checklist Phase 3
- [ ] Anyone can chat with AI fitness coach (no login)
- [ ] AI provides relevant workout recommendations
- [ ] AI analyzes progress (with or without user_id)
- [ ] Conversation context maintained via session_id
- [ ] AI suggests exercises based on goals
- [ ] Recommendations work without authentication
- [ ] AI responses are timely and relevant
- [ ] Works seamlessly in Telegram WebApp

---

## 🟣 PHASE 4: Full Authentication + Advanced AI Multi-Agent System

### Objective
**PRIORITY 1**: Implement complete multi-provider authentication (Telegram, SMS, Email, Google OAuth) with account linking, securing user data.
**PRIORITY 2**: Implement specialized AI agents for different fitness domains, create multi-agent orchestration system, and add advanced features like plan generation, injury prevention, and nutrition guidance.

### AI Prompt for Phase 4

```
Extend the FastAPI backend at /movoai_api/ to add FULL AUTHENTICATION first, then advanced multi-agent AI:

=== PART 1: COMPLETE AUTHENTICATION SYSTEM (PRIORITY) ===

NEW DEPENDENCIES:
Add to requirements.txt:
- passlib[bcrypt]>=1.7.4 (password hashing)
- python-jose[cryptography]>=3.3.0 (JWT tokens)
- python-multipart>=0.0.6 (form data)
- httpx>=0.25.0 (for OAuth callbacks)

NEW MODELS (app/models/):
- auth_method.py (UserAuthMethod for multi-provider auth)
  - Fields: id, user_id (FK), auth_provider (telegram/sms/email/google), auth_identifier, 
    auth_data (JSON), is_verified, is_primary, created_at, updated_at
- verification_code.py (VerificationCode for SMS/email codes)
  - Fields: id, identifier, code, code_type, expires_at, attempts, verified, created_at

NEW SCHEMAS (app/schemas/):
- auth.py (Login, token, verification code schemas)

AUTHENTICATION ENDPOINTS (app/api/v1/endpoints/auth.py):
1. POST /api/v1/auth/telegram/login
   - Authenticate with Telegram (Telegram WebApp auto-login)
   - Input: telegram_id, telegram_username, telegram_first_name, telegram_auth_date, telegram_hash
   - Verify Telegram data signature
   - If user exists (by telegram_id), return JWT token
   - If new user, create user + user_auth_method record, return JWT token
   
2. POST /api/v1/auth/telegram/link
   - Link Telegram to existing account (requires JWT)
   - Verify Telegram data, add to user_auth_methods
   
3. POST /api/v1/auth/phone/send-code
   - Send SMS verification code (NO AUTH)
   - Input: phone_number
   - Generate 6-digit code, send via Twilio/etc
   - Store in verification_codes table with 5-minute expiry
   
4. POST /api/v1/auth/phone/verify-code
   - Verify SMS code and login/register (NO AUTH)
   - Input: phone_number, code
   - If code valid and user exists, return JWT token
   - If code valid and new user, create user + user_auth_method, return JWT token
   
5. POST /api/v1/auth/phone/link
   - Link phone number to existing account (requires JWT)
   - Send verification code first, then verify
   
6. POST /api/v1/auth/email/send-code
   - Send email verification code (NO AUTH)
   - Input: email
   - Generate 6-digit code, send via SendGrid/etc
   - Store in verification_codes table with 10-minute expiry
   
7. POST /api/v1/auth/email/verify-code
   - Verify email code and login/register (NO AUTH)
   - Input: email, code
   - If code valid and user exists, return JWT token
   - If code valid and new user, create user + user_auth_method, return JWT token
   
8. POST /api/v1/auth/email/link
   - Link email to existing account (requires JWT)
   
9. GET /api/v1/auth/google/login
   - Redirect to Google OAuth consent screen (NO AUTH)
   - Use OAuth2 flow with google-auth library
   
10. GET /api/v1/auth/google/callback
    - Handle Google OAuth callback (NO AUTH)
    - Exchange code for Google user info
    - If user exists (by google_id), return JWT token
    - If new user, create user + user_auth_method, return JWT token
    
11. POST /api/v1/auth/google/link
    - Link Google account to existing account (requires JWT)
    
12. GET /api/v1/auth/methods
    - List all auth methods linked to current user (requires JWT)
    
13. DELETE /api/v1/auth/methods/{method_id}
    - Unlink authentication method (requires JWT)
    - Must have at least one remaining method
    
14. POST /api/v1/auth/methods/{method_id}/set-primary
    - Set primary authentication method (requires JWT)
    
15. POST /api/v1/auth/refresh
    - Refresh JWT access token using refresh token (NO AUTH, uses refresh token)
    - Return new access token
    
16. POST /api/v1/auth/logout
    - Invalidate refresh token (requires JWT)
    - Optional: add token to blacklist

USER MIGRATION:
17. POST /api/v1/auth/claim-account
    - Migrate existing user_id data to authenticated account
    - Input: old_user_id (from Phase 2), JWT token (from login)
    - Migrate all workout logs, plans, conversations to authenticated user
    - Delete old anonymous user record

SECURED USER ENDPOINTS (app/api/v1/endpoints/users.py):
1. GET /api/v1/users/me
   - Return current authenticated user profile (requires JWT)
   
2. PUT /api/v1/users/me
   - Update user profile (requires JWT)
   - Fields: age, weight_kg, height_cm, fitness_goals, workout_style, etc.
   
3. DELETE /api/v1/users/me
   - Delete user account (requires JWT)
   - Cascade delete all data
   
4. GET /api/v1/users/{user_id}
   - Get user by ID (requires JWT, admin or self only)

UPDATE EXISTING ENDPOINTS:
- Modify Phase 2 user endpoints to REQUIRE JWT authentication
- Change from /api/v1/users/{user_id}/plans to /api/v1/users/me/plans
- Use get_current_user dependency to enforce authentication
- Maintain backward compatibility temporarily with optional auth

SECURITY IMPLEMENTATION:
- JWT tokens: Access (15min) + Refresh (30 days)
- Telegram auth: Verify data hash using HMAC-SHA256(data, SHA256(bot_token))
- SMS/Email codes: 6-digit numeric, rate-limited (max 3 per hour)
- Google OAuth: Use google-auth library, verify ID token
- Password hashing: bcrypt via passlib
- Rate limiting: 5 login attempts per minute per IP
- CORS: Whitelist frontend origins
- Prevent account enumeration: same response for existing/non-existing users

THIRD-PARTY INTEGRATIONS:
- Telegram Bot API: Verify Telegram login data
- Twilio/AWS SNS: Send SMS verification codes
- SendGrid/AWS SES: Send email verification codes
- Google OAuth 2.0: Google sign-in flow
- Store all API keys in environment variables

ENVIRONMENT VARIABLES (.env):
- JWT_SECRET_KEY, JWT_REFRESH_SECRET_KEY, JWT_ALGORITHM
- TELEGRAM_BOT_TOKEN, TELEGRAM_BOT_USERNAME
- TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, TWILIO_PHONE_NUMBER
- SENDGRID_API_KEY, EMAIL_FROM_ADDRESS, EMAIL_FROM_NAME
- GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET, GOOGLE_REDIRECT_URI

=== PART 2: ADVANCED MULTI-AGENT AI SYSTEM ===

NEW DEPENDENCIES:
Add to requirements.txt:
- langgraph>=0.0.20 (for multi-agent workflows)
- langchain-experimental>=0.0.20
- anthropic>=0.7.0 (optional: Claude integration)
- redis>=5.0.0 (for agent state management)

NEW MODELS (app/models/):
- agent_execution.py
  - Fields: id, user_id, agent_type, input_data (JSON), output_data (JSON), status, execution_time, created_at
- plan_generation_log.py
  - Fields: id, user_id, generated_plan_id, generation_parameters (JSON), ai_reasoning (text), created_at
- feedback.py
  - Fields: id, user_id, agent_type, feedback_type (positive/negative), feedback_text, created_at

NEW SCHEMAS (app/schemas/):
- agent_execution.py
- plan_generation.py
- feedback.py
- multi_agent_request.py

SPECIALIZED AI AGENTS (app/ai/agents/):
1. workout_planner_agent.py
   - Expert in creating structured workout plans
   - Considers periodization, progressive overload
   - Generates multi-week programs
   
2. exercise_selector_agent.py
   - Specializes in choosing optimal exercises
   - Considers muscle balance, recovery
   - Avoids overtraining specific muscle groups
   
3. progress_analyst_agent.py
   - Analyzes workout logs and user progress
   - Identifies plateaus and suggests adjustments
   - Calculates fitness metrics and trends
   
4. nutrition_advisor_agent.py
   - Provides basic nutrition guidance
   - Suggests macros based on fitness goals
   - Complements workout recommendations
   
5. injury_prevention_agent.py
   - Identifies risky exercise combinations
   - Suggests warm-up and cool-down routines
   - Recommends modifications for limitations
   
6. motivation_coach_agent.py
   - Provides encouragement and accountability
   - Analyzes adherence patterns
   - Suggests strategies to maintain consistency

MULTI-AGENT ORCHESTRATION (app/ai/orchestration/):
- agent_coordinator.py
  - Routes requests to appropriate agents
  - Manages multi-agent workflows with LangGraph
  - Aggregates results from multiple agents
  
- workflow_definitions.py
  - Define complex workflows (e.g., full plan generation)
  - Example: User request → Progress Analyst → Exercise Selector → Workout Planner → Injury Prevention → Final Plan
  
- state_manager.py
  - Manage agent execution state in Redis
  - Handle long-running agent processes
  - Support workflow pause/resume

ADVANCED AI ENDPOINTS (app/api/v1/endpoints/ai_agents.py):
1. POST /api/v1/ai/agents/generate-plan
   - Full workout plan generation using multiple agents
   - Input: duration (weeks), days_per_week, goals, constraints
   - Workflow: Progress analysis → Exercise selection → Plan structure → Safety review
   - Output: Complete workout_plan with plan_exercises, AI reasoning
   - Save to database as user's custom plan
   
2. POST /api/v1/ai/agents/optimize-current-plan
   - Analyze user's current plan and suggest optimizations
   - Use progress_analyst_agent + workout_planner_agent
   - Output: Suggested modifications with reasoning
   
3. POST /api/v1/ai/agents/check-injury-risk
   - Input: planned exercises or current plan
   - Output: Risk assessment, suggested modifications
   - Use injury_prevention_agent
   
4. POST /api/v1/ai/agents/nutrition-guidance
   - Input: user goals, workout intensity
   - Output: Basic nutrition recommendations (calories, macros)
   - Use nutrition_advisor_agent
   
5. POST /api/v1/ai/agents/motivation-boost
   - Input: user's recent activity (or lack thereof)
   - Output: Personalized motivational message, tips
   - Use motivation_coach_agent
   
6. POST /api/v1/ai/agents/adaptive-workout
   - Generate today's workout based on recent performance
   - Consider recovery, energy levels, progress
   - Use multiple agents for comprehensive planning
   
7. GET /api/v1/ai/agents/executions
   - List all agent executions for user
   - Show agent type, status, execution time
   
8. GET /api/v1/ai/agents/executions/{execution_id}
   - Get detailed execution results
   - Include agent reasoning and decision process

AGENT FEEDBACK ENDPOINTS (app/api/v1/endpoints/ai_feedback.py):
1. POST /api/v1/ai/feedback
   - Submit feedback on AI recommendations
   - Input: agent_type, feedback_type, feedback_text, execution_id
   - Used to improve future recommendations
   
2. GET /api/v1/ai/feedback/stats
   - Admin endpoint: Get feedback statistics
   - Track agent performance over time

LANGGRAPH WORKFLOWS:
- Full Plan Generation Workflow:
  1. Start → Load user context
  2. Progress Analyst agent (if user has history)
  3. Exercise Selector agent
  4. Workout Planner agent
  5. Injury Prevention agent (safety check)
  6. Validate plan against database constraints
  7. Return final plan
  
- Adaptive Workout Workflow:
  1. Start → Load recent workouts
  2. Progress Analyst (check recovery needs)
  3. Exercise Selector (choose today's exercises)
  4. Motivation Coach (add encouraging message)
  5. Return workout + motivation
  
- Workflow State Transitions:
  - Use StateGraph from langgraph
  - Define conditional edges based on agent outputs
  - Handle failures and retries

ADVANCED AGENT FEATURES:
- Agent Collaboration:
  - Agents can query each other's outputs
  - Shared context across agent executions
  - Consensus mechanism for critical decisions
  
- Learning & Adaptation:
  - Store successful recommendations
  - Learn from user feedback
  - Adjust agent behavior over time
  
- Explainability:
  - Each agent logs reasoning process
  - Provide "why" for each recommendation
  - Show decision tree for complex plans

PERFORMANCE & SCALING:
- Async agent execution for long-running tasks
- WebSocket support for real-time agent updates
- Background jobs with Celery for plan generation
- Agent execution queue management
- Caching for repeated agent queries

SAFETY & VALIDATION:
- Validate all AI-generated plans
  - Check exercise IDs exist
  - Verify sets/reps are realistic
  - Ensure rest days are included
  
- Content filtering:
  - Reject inappropriate user inputs
  - Validate AI outputs for safety
  
- Rate limiting:
  - Limit agent executions per user per day
  - Prevent abuse of expensive operations

MONITORING & ANALYTICS:
- Track agent execution times
- Monitor success/failure rates
- Log token usage per agent
- User satisfaction metrics (feedback)
- A/B testing framework for agent improvements

REDIS STATE MANAGEMENT:
- Store active workflow states
- Handle distributed agent execution
- Session management for long conversations
- Cache frequent agent queries

ERROR HANDLING:
- Graceful degradation if agents fail
- Fallback to simpler agents or rule-based systems
- User-friendly error messages
- Retry logic with exponential backoff

TESTING:
- Mock all LLM calls in tests
- Test each agent independently
- Test multi-agent workflows end-to-end
- Test state persistence in Redis
- Load testing for concurrent agent executions
- Test feedback loop integration

CONFIGURATION:
- Agent-specific settings in .env
- Model selection per agent (some can use cheaper models)
- Workflow timeout settings
- Redis connection settings
- Agent execution limits

DOCUMENTATION:
- Document each agent's purpose and capabilities
- Provide workflow diagrams (Mermaid/PlantUML)
- API documentation with agent examples
- Best practices for agent usage
- Troubleshooting guide
```

### Phase 4 Deliverables
✅ **AUTHENTICATION (PRIORITY)**:
  - Multi-provider authentication (Telegram, SMS, Email, Google)
  - JWT access & refresh token mechanism
  - User can link multiple auth methods to one account
  - Verification code system for SMS/Email
  - Account migration from anonymous to authenticated
  - All user data now secured behind authentication
✅ **ADVANCED AI**:
  - Multiple specialized AI agents functional
  - Multi-agent orchestration with LangGraph
  - Automated workout plan generation
  - Injury prevention and safety checks
  - Nutrition guidance integration
  - Motivation and coaching features
  - Agent feedback and learning system
✅ All endpoints tested with pytest
✅ **Frontend Integration Test**: Full auth flow, migrate account, use advanced AI features from `/MovoAI/`

### Frontend Testing Checklist Phase 4
**Authentication:**
- [ ] User can login via Telegram (Telegram WebApp auto-login)
- [ ] User can login via SMS code
- [ ] User can login via Email code
- [ ] User can login via Google OAuth
- [ ] User can link additional auth methods to account
- [ ] User can set primary auth method
- [ ] User can unlink auth methods (keeping at least one)
- [ ] User can migrate anonymous account data after login
- [ ] Access token expires and refreshes correctly
- [ ] Rate limiting works (code sending, login attempts)

**Advanced AI:**
- [ ] User can generate complete workout plan via AI
- [ ] Generated plan appears in user's secured plans
- [ ] User receives injury prevention warnings
- [ ] Nutrition guidance is accessible and helpful
- [ ] Motivation coach provides timely encouragement
- [ ] User can provide feedback on AI recommendations
- [ ] All agents respond within acceptable time
- [ ] Multi-week plans are coherent and progressive
- [ ] AI explanations are clear and actionable

---

## 📋 Development Guidelines

### Environment Setup
```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt

# Setup database connection
cp .env.example .env
# Edit .env with database credentials pointing to /Zitan/database/

# Run database migrations
alembic upgrade head

# Start development server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Testing Strategy
- **Unit Tests**: Test individual functions and classes
- **Integration Tests**: Test API endpoints with database
- **Frontend Integration**: Manual testing with `/MovoAI/` frontend after each phase
- **Load Testing**: Test concurrent users (Phase 4)

### API Versioning
- All endpoints under `/api/v1/`
- Future versions can be added without breaking changes

### Database Management
- Use Alembic for migrations
- Never modify `/Zitan/database/schema.sql` directly
- Create migration files for schema changes
- Reference existing tables from schema.sql

### Code Quality
- Use Black for code formatting
- Use Flake8 for linting
- Use MyPy for type checking
- Maintain >80% test coverage
- Document all public APIs

### Security Best Practices
- Store secrets in `.env` file (never commit)
- Use parameterized queries (SQLAlchemy ORM)
- Implement rate limiting on AI endpoints
- Validate all user inputs
- Use HTTPS in production
- Implement CSRF protection for state-changing operations

### Performance Optimization
- Use database indexing on foreign keys
- Implement caching for exercise library
- Use connection pooling for database
- Implement pagination for large datasets
- Use async operations for AI calls
- Monitor query performance with logging

---

## 🚀 Deployment Checklist

### Pre-Production
- [ ] All tests passing
- [ ] API documentation complete
- [ ] Environment variables configured
- [ ] Database migrations applied
- [ ] CORS configured correctly
- [ ] Rate limiting enabled
- [ ] Logging configured
- [ ] Error tracking setup (Sentry)

### Production
- [ ] HTTPS enabled
- [ ] Database backups configured
- [ ] Monitoring setup (CPU, memory, response times)
- [ ] Auto-scaling configured
- [ ] Health check endpoint verified
- [ ] OpenAI API rate limits configured
- [ ] Redis cluster setup (Phase 4)

---

## 📊 Success Metrics

### Phase 1
- User registration success rate > 95%
- API response time < 200ms (95th percentile)
- JWT token validation working 100%

### Phase 2
- Exercise search response time < 300ms
- Workout plan retrieval < 500ms
- Workout log creation success rate > 99%

### Phase 3
- AI response time < 3s (95th percentile)
- AI recommendation accuracy (user feedback) > 75%
- Conversation context maintained across 10+ messages

### Phase 4
- Full plan generation time < 10s
- Multi-agent workflow success rate > 90%
- Agent execution cost < $0.10 per plan
- User satisfaction with AI (feedback) > 80%

---

## 🔄 Iteration & Feedback Loop

After each phase:
1. **Deploy to staging** and test with frontend
2. **Collect user feedback** from `/MovoAI/` integration
3. **Measure performance** against success metrics
4. **Refine and optimize** before moving to next phase
5. **Document lessons learned**

---

## 📞 Integration Points

### Frontend (`/MovoAI/`)
- Base API URL: `http://localhost:8000` (dev) or production URL
- Authentication: JWT token in `Authorization: Bearer <token>` header
- WebSocket: `/ws` endpoint for real-time AI chat (Phase 3+)
- Error handling: Structured JSON errors with status codes

### Database (`/Zitan/database/`)
- PostgreSQL connection string in `.env`
- Read existing tables, don't modify schema directly
- Use foreign keys to maintain referential integrity

---

## 📝 Notes

- **Incremental Development**: Each phase builds on previous ones
- **Frontend Testing**: Critical to test with actual frontend after each phase
- **AI Costs**: Monitor OpenAI API usage closely in Phases 3 & 4
- **Scalability**: Design with horizontal scaling in mind
- **Documentation**: Keep README and API docs updated throughout

---

## 🎯 Final Outcome

By the end of Phase 4, you will have:
- ✅ Complete user management system
- ✅ Full workout and exercise management
- ✅ AI-powered recommendations and coaching
- ✅ Multi-agent system for complex fitness planning
- ✅ Production-ready FastAPI backend
- ✅ Fully tested and integrated with `/MovoAI/` frontend
- ✅ Scalable architecture for future enhancements

**Total Estimated Timeline**: 8-12 weeks (2-3 weeks per phase)

---

*This plan can be adjusted based on team size, priorities, and specific requirements. Each phase can be further broken down into smaller sprints if needed.*

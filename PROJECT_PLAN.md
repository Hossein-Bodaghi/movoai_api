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

## 🔵 PHASE 1: Foundation & User Management APIs

### Objective
Establish the core backend infrastructure and implement complete user authentication and profile management.

### AI Prompt for Phase 1

```
Create a FastAPI backend project at /movoai_api/ with the following requirements:

PROJECT STRUCTURE:
- app/
  - main.py (FastAPI application entry point)
  - config.py (Database connection, environment variables)
  - dependencies.py (Shared dependencies like DB sessions)
  - models/
    - user.py (SQLAlchemy User model)
  - schemas/
    - user.py (Pydantic schemas for User)
  - api/
    - v1/
      - endpoints/
        - users.py (User CRUD endpoints)
      - api.py (API router aggregator)
  - database/
    - session.py (Database session management)
    - base.py (SQLAlchemy declarative base)
  - core/
    - security.py (Password hashing, JWT token handling)
    - config.py (Settings management with pydantic-settings)
- tests/
  - test_users.py (Unit tests for user endpoints)
- .env.example (Template for environment variables)
- requirements.txt (Update with SQLAlchemy, passlib, python-jose)
- README.md (Setup instructions)

DATABASE CONNECTION:
- Connect to PostgreSQL database at /Zitan/database/
- Use the existing 'users' table from schema.sql
- Implement connection pooling
- Add database migrations support (Alembic)

AUTHENTICATION ARCHITECTURE:
- Support multiple authentication providers: Telegram, SMS, Email, Google OAuth
- Store user authentication methods in 'user_auth_methods' table:
  - id, user_id, auth_provider (telegram/sms/email/google), auth_identifier (telegram_id/phone/email/google_id), is_verified, created_at
- Allow users to link multiple auth methods to same account
- Primary user identification via internal user_id (not tied to any provider)
- JWT tokens contain user_id (provider-agnostic)

NEW TABLES TO ADD:
1. user_auth_methods:
   - id (PK), user_id (FK to users), auth_provider (enum), auth_identifier (unique per provider), 
   - auth_data (JSON: refresh_tokens, etc.), is_verified (boolean), is_primary (boolean), created_at, updated_at
   
2. verification_codes:
   - id (PK), identifier (phone/email), code (6-digit), code_type (sms/email), 
   - expires_at, attempts (int), verified (boolean), created_at

USER MANAGEMENT ENDPOINTS:
1. POST /api/v1/auth/telegram/login
   - Authenticate with Telegram (auto-login via Telegram Web App)
   - Input: telegram_id, telegram_username, telegram_first_name, telegram_auth_date, telegram_hash
   - Verify Telegram data signature
   - If user exists (by telegram_id), return JWT token
   - If new user, create user + user_auth_method record, return JWT token
   
2. POST /api/v1/auth/telegram/link
   - Link Telegram to existing account (requires JWT)
   - Verify Telegram data, add to user_auth_methods
   
3. POST /api/v1/auth/phone/send-code
   - Send SMS verification code
   - Input: phone_number
   - Generate 6-digit code, send via SMS provider (Twilio/etc)
   - Store in verification_codes table with 5-minute expiry
   
4. POST /api/v1/auth/phone/verify-code
   - Verify SMS code and login/register
   - Input: phone_number, code
   - If code valid and user exists, return JWT token
   - If code valid and new user, create user + user_auth_method, return JWT token
   
5. POST /api/v1/auth/phone/link
   - Link phone number to existing account (requires JWT)
   - Send verification code first, then verify
   
6. POST /api/v1/auth/email/send-code
   - Send email verification code
   - Input: email
   - Generate 6-digit code, send via email provider (SendGrid/etc)
   - Store in verification_codes table with 10-minute expiry
   
7. POST /api/v1/auth/email/verify-code
   - Verify email code and login/register
   - Input: email, code
   - If code valid and user exists, return JWT token
   - If code valid and new user, create user + user_auth_method, return JWT token
   
8. POST /api/v1/auth/email/link
   - Link email to existing account (requires JWT)
   
9. GET /api/v1/auth/google/login
   - Redirect to Google OAuth consent screen
   - Use OAuth2 flow with google-auth library
   
10. GET /api/v1/auth/google/callback
    - Handle Google OAuth callback
    - Exchange code for Google user info
    - If user exists (by google_id), return JWT token
    - If new user, create user + user_auth_method, return JWT token
    
11. POST /api/v1/auth/google/link
    - Link Google account to existing account (requires JWT)
    
12. GET /api/v1/auth/methods
    - List all auth methods linked to current user
    - Requires JWT authentication
    
13. DELETE /api/v1/auth/methods/{method_id}
    - Unlink authentication method (must have at least one remaining)
    - Requires JWT authentication
    
14. POST /api/v1/auth/methods/{method_id}/set-primary
    - Set primary authentication method
    - Requires JWT authentication
    
15. POST /api/v1/auth/refresh
    - Refresh JWT access token using refresh token
    - Return new access token
    
16. POST /api/v1/auth/logout
    - Invalidate refresh token
    - Optional: add token to blacklist
   
17. GET /api/v1/users/me
    - Return current authenticated user profile
    - Require JWT authentication
   
18. PUT /api/v1/users/me
    - Update user profile (age, weight_kg, fitness_goals, workout_style, etc.)
    - Require JWT authentication
   
19. DELETE /api/v1/users/me
    - Soft delete or hard delete user account
    - Cascade delete all user_auth_methods
    - Require JWT authentication
   
20. GET /api/v1/users/{user_id}
    - Get user by ID (admin or self only)
   
SECURITY:
- Implement JWT token-based authentication (access token + refresh token)
  - Access token: Short-lived (15 minutes), contains user_id only
  - Refresh token: Long-lived (30 days), stored in httpOnly cookie or secure storage
- Telegram authentication: Verify data hash using bot token
  - Validate telegram_auth_date (not older than 1 day)
  - Verify hash = HMAC-SHA256(data, SHA256(bot_token))
- SMS/Email codes: 6-digit numeric, rate-limited (max 3 per hour per identifier)
- Google OAuth: Use google-auth library, verify ID token
- Add middleware for CORS (allow frontend origin at /MovoAI/)
- Input validation with Pydantic models
- SQL injection protection via SQLAlchemy ORM
- Rate limiting: 5 login attempts per minute per IP
- Prevent account enumeration: same response for existing/non-existing users

ERROR HANDLING:
- Custom exception handlers for 400, 401, 404, 422, 500
- Structured JSON error responses
- Logging for all errors

TESTING:
- Write pytest tests for all endpoints
- Mock database connections
- Test authentication flows
- Test input validation

DOCUMENTATION:
- Auto-generated OpenAPI docs at /docs
- Add detailed descriptions for all endpoints
- Include example requests/responses

THIRD-PARTY INTEGRATIONS:
- Telegram Bot API: For verifying Telegram login data
- Twilio/SNS: For sending SMS verification codes
- SendGrid/SES: For sending email verification codes
- Google OAuth 2.0: For Google sign-in
- Store API keys and secrets in environment variables

DEPLOYMENT READINESS:
- Environment variable configuration (.env file):
  - DATABASE_URL, JWT_SECRET_KEY, JWT_REFRESH_SECRET_KEY
  - TELEGRAM_BOT_TOKEN, TELEGRAM_BOT_USERNAME
  - TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, TWILIO_PHONE_NUMBER
  - SENDGRID_API_KEY, EMAIL_FROM_ADDRESS
  - GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET, GOOGLE_REDIRECT_URI
- Docker support (optional Dockerfile)
- Health check endpoint: GET /health
- Logging configuration (structured JSON logs)
```

### Phase 1 Deliverables
✅ Multi-provider authentication system (Telegram, SMS, Email, Google)  
✅ JWT access & refresh token mechanism  
✅ User can link multiple auth methods to one account  
✅ Verification code system for SMS/Email  
✅ User profile CRUD operations  
✅ Database connection established  
✅ API documentation accessible at `/docs`  
✅ Unit tests passing for all auth flows  
✅ **Frontend Integration Test**: Login with each provider, link accounts, view/edit profile from `/MovoAI/`

### Frontend Testing Checklist Phase 1
- [ ] User can login via Telegram (auto-login)
- [ ] User can login via SMS code
- [ ] User can login via Email code
- [ ] User can login via Google OAuth
- [ ] User can link additional auth methods to account
- [ ] User can set primary auth method
- [ ] User can unlink auth methods (keeping at least one)
- [ ] User profile displays correctly
- [ ] User can update profile information
- [ ] Access token expires and refreshes correctly
- [ ] Error messages display properly for each auth flow
- [ ] Rate limiting works (code sending, login attempts)

---

## 🟢 PHASE 2: Workflow Management APIs

### Objective
Implement workout plan management, exercise library access, and user workout plan assignment/tracking.

### AI Prompt for Phase 2

```
Extend the FastAPI backend at /movoai_api/ to add workout workflow management:

NEW MODELS (app/models/):
- workout_plan.py (SQLAlchemy model for workout_plans table)
- exercise.py (SQLAlchemy model for exercises table)
- plan_exercise.py (SQLAlchemy model for plan_exercises table)
- user_plan.py (SQLAlchemy model for user_plans table)
- workout_log.py (SQLAlchemy model for user_workout_logs table)

NEW SCHEMAS (app/schemas/):
- workout_plan.py (Pydantic schemas for plans)
- exercise.py (Pydantic schemas for exercises)
- plan_exercise.py (Pydantic schemas for plan-exercise relationships)
- user_plan.py (Pydantic schemas for user plans)
- workout_log.py (Pydantic schemas for workout logs)

EXERCISE LIBRARY ENDPOINTS (app/api/v1/endpoints/exercises.py):
1. GET /api/v1/exercises
   - List all exercises with pagination
   - Query parameters: difficulty, goal, muscles, equipment
   - Support English and French (exercise_en, exercise_fr)
   - Return: id, exercise_en/fr, difficulty, goal, muscles, instructions, equipments, gif URLs
   
2. GET /api/v1/exercises/{exercise_id}
   - Get single exercise details
   - Include male_gif_urls and female_gif_urls
   
3. GET /api/v1/exercises/search
   - Search exercises by name, muscle group, equipment
   - Full-text search capability
   
4. GET /api/v1/exercises/filter
   - Advanced filtering: difficulty, goal, muscles[], equipment[]
   - Support multiple muscle groups and equipment types

WORKOUT PLAN ENDPOINTS (app/api/v1/endpoints/workout_plans.py):
1. GET /api/v1/workout-plans
   - List all template workout plans (is_template=true)
   - Include plan name, description (EN/FR), exercise count
   
2. GET /api/v1/workout-plans/{plan_id}
   - Get detailed plan with all exercises
   - Return: plan details + list of plan_exercises with exercise info
   - Include day_number, week_number, sets, reps, duration, rest, order
   
3. POST /api/v1/workout-plans
   - Create custom workout plan (admin/trainer only)
   - Require: name_en, description_en, created_by_user_id
   
4. PUT /api/v1/workout-plans/{plan_id}
   - Update workout plan details
   
5. DELETE /api/v1/workout-plans/{plan_id}
   - Delete workout plan (cascade to plan_exercises)
   
6. POST /api/v1/workout-plans/{plan_id}/exercises
   - Add exercise to plan
   - Require: exercise_id, day_number, week_number, sets, reps, duration_seconds, rest_seconds, order_in_day

USER WORKOUT PLAN ENDPOINTS (app/api/v1/endpoints/user_plans.py):
1. GET /api/v1/users/me/plans
   - Get all workout plans assigned to current user
   - Filter by status: active, completed, paused
   
2. POST /api/v1/users/me/plans
   - Assign workout plan to current user
   - Require: plan_id, start_date
   - Set status to 'active'
   
3. GET /api/v1/users/me/plans/{user_plan_id}
   - Get detailed user plan with progress
   - Include workout logs for each exercise
   
4. PUT /api/v1/users/me/plans/{user_plan_id}
   - Update user plan status (active, completed, paused)
   
5. DELETE /api/v1/users/me/plans/{user_plan_id}
   - Remove plan from user

WORKOUT LOGGING ENDPOINTS (app/api/v1/endpoints/workout_logs.py):
1. POST /api/v1/workout-logs
   - Log completed workout
   - Require: plan_exercise_id, date_performed, sets_completed, reps_completed, duration_seconds_completed
   - Automatically associate with current user
   
2. GET /api/v1/workout-logs
   - Get user's workout history
   - Query params: start_date, end_date, plan_exercise_id
   
3. GET /api/v1/users/me/progress
   - Get workout progress statistics
   - Return: total workouts, exercises completed, workout streak, weekly summary
   
4. PUT /api/v1/workout-logs/{log_id}
   - Edit workout log entry
   
5. DELETE /api/v1/workout-logs/{log_id}
   - Delete workout log entry

BUSINESS LOGIC:
- Validate exercise exists before adding to plan
- Ensure user can only access their own plans and logs
- Calculate workout completion percentage
- Track workout streaks and statistics
- Support multi-week workout plans

PERFORMANCE OPTIMIZATIONS:
- Eager loading for related entities (plans with exercises)
- Database indexing on foreign keys
- Pagination for large result sets
- Caching for exercise library (rarely changes)

TESTING:
- Test CRUD operations for all new endpoints
- Test cascading deletes (plan deletion)
- Test user authorization (users can't access others' plans)
- Test workout log statistics calculations
- Integration tests with database

DOCUMENTATION:
- Update OpenAPI docs with new endpoints
- Add request/response examples for complex queries
- Document filtering and search parameters
```

### Phase 2 Deliverables
✅ Exercise library accessible with search/filter  
✅ Workout plan CRUD operations  
✅ User can be assigned workout plans  
✅ Workout logging functionality  
✅ Progress tracking and statistics  
✅ All endpoints tested with pytest  
✅ **Frontend Integration Test**: Browse exercises, view plans, assign plan, log workout from `/MovoAI/`

### Frontend Testing Checklist Phase 2
- [ ] User can browse exercise library
- [ ] User can filter exercises by muscle group, difficulty
- [ ] User can view workout plan details
- [ ] User can be assigned a workout plan
- [ ] User can log completed workouts
- [ ] User can view workout history and progress
- [ ] Multi-week plans display correctly

---

## 🟡 PHASE 3: AI Agent Foundation & Integration

### Objective
Integrate LangChain for AI-powered workout recommendations, implement conversation management, and create intelligent fitness coaching capabilities.

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

AI RECOMMENDATION ENDPOINTS (app/api/v1/endpoints/ai_recommendations.py):
1. POST /api/v1/ai/recommend-workout
   - Input: user preferences, goals, available equipment, time constraints
   - Output: Personalized workout plan with exercises
   - Use LangChain to analyze user profile and generate recommendations
   - Save recommendation to database
   
2. POST /api/v1/ai/analyze-progress
   - Input: user_id, date_range
   - Output: AI-generated progress analysis, insights, suggestions
   - Analyze workout logs and provide feedback
   
3. POST /api/v1/ai/suggest-exercises
   - Input: target muscles, difficulty, equipment
   - Output: List of exercises with AI-generated reasoning
   - Use vector similarity search on exercise embeddings

AI CONVERSATION ENDPOINTS (app/api/v1/endpoints/ai_chat.py):
1. POST /api/v1/ai/chat
   - Input: user message
   - Output: AI assistant response
   - Maintain conversation context
   - Save conversation to database
   - Support multi-turn conversations
   
2. GET /api/v1/ai/conversations
   - Get user's conversation history
   - Pagination support
   
3. GET /api/v1/ai/conversations/{conversation_id}
   - Get specific conversation thread
   
4. DELETE /api/v1/ai/conversations/{conversation_id}
   - Delete conversation history
   
5. POST /api/v1/ai/session/start
   - Start new AI coaching session
   - Return session_id
   
6. POST /api/v1/ai/session/{session_id}/end
   - End AI coaching session
   - Save session summary

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
- [ ] User can chat with AI fitness coach
- [ ] AI provides relevant workout recommendations
- [ ] AI analyzes user progress and provides feedback
- [ ] Conversation context is maintained
- [ ] AI suggests exercises based on goals
- [ ] Recommendations are saved and accessible
- [ ] AI responses are timely and relevant

---

## 🟣 PHASE 4: Advanced AI Agents & Multi-Agent System

### Objective
Implement specialized AI agents for different fitness domains, create a multi-agent orchestration system, and add advanced features like plan generation, injury prevention, and nutrition guidance.

### AI Prompt for Phase 4

```
Extend the FastAPI backend at /movoai_api/ to create a sophisticated multi-agent AI system:

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
✅ Multiple specialized AI agents functional  
✅ Multi-agent orchestration with LangGraph  
✅ Automated workout plan generation  
✅ Injury prevention and safety checks  
✅ Nutrition guidance integration  
✅ Motivation and coaching features  
✅ Agent feedback and learning system  
✅ All advanced AI endpoints tested  
✅ **Frontend Integration Test**: Generate full plan, get safety checks, receive nutrition advice, use motivation coach from `/MovoAI/`

### Frontend Testing Checklist Phase 4
- [ ] User can generate complete workout plan via AI
- [ ] Generated plan appears in user's plans
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

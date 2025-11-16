# MovoAI API - Phase 1

FastAPI backend for MovoAI Fitness Application with multi-provider authentication.

## Features

✅ **Multi-Provider Authentication**
- Telegram auto-login
- SMS verification (via Twilio)
- Email verification (via SendGrid)
- Google OAuth 2.0

✅ **User Management**
- User profile CRUD operations
- Multiple authentication methods per user
- Account linking and unlinking

✅ **Security**
- JWT access and refresh tokens
- Rate limiting
- Input validation
- CORS support

✅ **Database**
- PostgreSQL with SQLAlchemy ORM
- Alembic migrations
- Connection pooling

## Tech Stack

- **Framework**: FastAPI 0.116.1
- **Database**: PostgreSQL + SQLAlchemy
- **Authentication**: JWT (python-jose)
- **Validation**: Pydantic v2
- **Testing**: pytest
- **SMS**: Twilio
- **Email**: SendGrid
- **OAuth**: Google OAuth 2.0

## Prerequisites

- Python 3.10+
- PostgreSQL 12+
- Twilio account (for SMS, optional)
- SendGrid account (for Email, optional)
- Google OAuth credentials (optional)
- Telegram Bot Token (for Telegram auth)

## Installation

### 1. Clone and Navigate

```bash
cd /movoai_api
```

### 2. Create Virtual Environment

```bash
python -m venv venv
source venv/bin/activate  # On Linux/Mac
# venv\Scripts\activate  # On Windows
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables

```bash
cp .env.example .env
```

Edit `.env` file with your configuration:

```env
# Database
DATABASE_URL=postgresql://postgres:password@localhost:5432/movoai

# JWT Secrets (generate secure keys)
JWT_SECRET_KEY=your-super-secret-jwt-key-change-this-in-production
JWT_REFRESH_SECRET_KEY=your-super-secret-refresh-key-change-this-in-production

# Telegram Bot (required for Telegram auth)
TELEGRAM_BOT_TOKEN=your-telegram-bot-token
TELEGRAM_BOT_USERNAME=your_bot_username

# Twilio (optional - for SMS)
TWILIO_ACCOUNT_SID=your-twilio-account-sid
TWILIO_AUTH_TOKEN=your-twilio-auth-token
TWILIO_PHONE_NUMBER=+1234567890

# SendGrid (optional - for Email)
SENDGRID_API_KEY=your-sendgrid-api-key
EMAIL_FROM_ADDRESS=noreply@movoai.com

# Google OAuth (optional)
GOOGLE_CLIENT_ID=your-google-client-id.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=your-google-client-secret
GOOGLE_REDIRECT_URI=http://localhost:8000/api/v1/auth/google/callback

# Application
FRONTEND_URL=http://localhost:5173
DEBUG=True
```

### 5. Setup Database

The application expects the existing database at `/Zitan/database/` with the `users` table already created from `schema.sql`.

Run migrations to create new auth tables:

```bash
alembic upgrade head
```

### 6. Run the Application

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Or using Python:

```bash
python -m app.main
```

The API will be available at: `http://localhost:8000`

## API Documentation

Once the server is running, access interactive API documentation:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI JSON**: http://localhost:8000/openapi.json

## API Endpoints Summary

### Authentication (`/api/v1/auth`)
- Telegram, SMS, Email, Google OAuth login
- Account linking
- Token refresh & logout
- Auth method management

### Users (`/api/v1/users`)
- Get/update/delete user profile
- View authentication methods

See full API documentation at `/docs` when server is running.

## Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html

# Run specific test file
pytest tests/test_auth.py
```

## Project Structure

```
movoai_api/
├── app/
│   ├── main.py                 # FastAPI application
│   ├── dependencies.py         # Shared dependencies
│   ├── api/v1/endpoints/       # API endpoints
│   ├── core/                   # Config & security
│   ├── database/               # Database session
│   ├── models/                 # SQLAlchemy models
│   ├── schemas/                # Pydantic schemas
│   └── services/               # External integrations
├── alembic/                    # Database migrations
├── tests/                      # Test files
├── .env.example               # Environment template
├── requirements.txt
├── PROJECT_PLAN.md            # Full 4-phase plan
└── README.md
```

## Quick Test

```bash
# Health check
curl http://localhost:8000/health

# View API docs
open http://localhost:8000/docs
```

## Next Steps

1. Configure `.env` with your credentials
2. Run database migrations
3. Start the server
4. Test with frontend at `/MovoAI/`
5. Proceed to Phase 2 (Workout Management)

See `PROJECT_PLAN.md` for complete roadmap.

---

**Phase 1 Status**: ✅ Complete and ready for frontend integration
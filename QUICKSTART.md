# MovoAI API - Quick Start Guide

This guide will help you get the Phase 1 backend running in minutes.

## Prerequisites Checklist

- [ ] Python 3.10 or higher installed
- [ ] PostgreSQL running (with existing database from `/Zitan/database/`)
- [ ] Git installed
- [ ] Terminal/Command line access

## 5-Minute Setup

### Step 1: Navigate to Project

```bash
cd /movoai_api
```

### Step 2: Run Setup Script

```bash
./setup.sh
```

This will:
- Create virtual environment
- Install all dependencies
- Create `.env` file from template

### Step 3: Configure Environment

Edit the `.env` file:

```bash
nano .env
```

**Minimum required configuration:**

```env
# Database - Point to your existing PostgreSQL database
DATABASE_URL=postgresql://postgres:password@localhost:5432/movoai

# JWT Secrets - Generate random secure strings
JWT_SECRET_KEY=change-this-to-a-random-secure-string
JWT_REFRESH_SECRET_KEY=change-this-to-another-random-secure-string

# Telegram Bot - Get from @BotFather on Telegram
TELEGRAM_BOT_TOKEN=your-bot-token-here
TELEGRAM_BOT_USERNAME=your_bot_username

# Frontend URL
FRONTEND_URL=http://localhost:5173
```

**Generate secure JWT secrets:**

```bash
# In Python
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

Run this twice to get two different secrets.

### Step 4: Run Database Migrations

```bash
source venv/bin/activate  # Activate virtual environment
alembic upgrade head
```

This creates the new authentication tables (`user_auth_methods`, `verification_codes`).

### Step 5: Start the Server

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Step 6: Test It Works

Open your browser:
- **API Docs**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

Or use curl:

```bash
curl http://localhost:8000/health
```

You should see:
```json
{
  "status": "healthy",
  "app": "MovoAI API",
  "version": "1.0.0"
}
```

## Testing Authentication

### Test Telegram Login (Simplified)

Since Telegram auth requires a real hash, test with email instead:

### Test Email Authentication

1. **Send verification code:**

```bash
curl -X POST http://localhost:8000/api/v1/auth/email/send-code \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com"}'
```

2. **Check terminal output** - In development mode (no SendGrid), the code is printed to console.

3. **Verify code and create user:**

```bash
curl -X POST http://localhost:8000/api/v1/auth/email/verify-code \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "code": "123456",
    "user_data": {
      "name": "Test User",
      "gender": "male",
      "age": 25,
      "daily_activity": "moderately_active",
      "fitness_level": "intermediate",
      "fitness_goals": ["weight_loss"],
      "height_cm": 175,
      "weight_kg": 75
    }
  }'
```

4. **Copy the access_token** from response.

5. **Get user profile:**

```bash
curl http://localhost:8000/api/v1/users/me \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN_HERE"
```

## Common Issues

### Issue: "Module not found" errors

**Solution:**
```bash
# Make sure virtual environment is activated
source venv/bin/activate
# Reinstall dependencies
pip install -r requirements.txt
```

### Issue: Database connection error

**Solution:**
```bash
# Check PostgreSQL is running
sudo systemctl status postgresql
# Verify DATABASE_URL in .env is correct
# Test connection
psql -U postgres -d movoai
```

### Issue: "Alembic not found"

**Solution:**
```bash
source venv/bin/activate
pip install alembic
```

### Issue: Port 8000 already in use

**Solution:**
```bash
# Use a different port
uvicorn app.main:app --reload --port 8001
```

## Development Workflow

### Daily Development

```bash
# 1. Activate environment
cd /movoai_api
source venv/bin/activate

# 2. Start server
uvicorn app.main:app --reload

# 3. Code changes auto-reload
# 4. View logs in terminal
# 5. Test at http://localhost:8000/docs
```

### Running Tests

```bash
# All tests
pytest

# Specific test file
pytest tests/test_auth.py

# With output
pytest -v

# With coverage
pytest --cov=app
```

### Database Operations

```bash
# View current migration
alembic current

# Create new migration
alembic revision --autogenerate -m "description"

# Apply migration
alembic upgrade head

# Rollback
alembic downgrade -1
```

## Integration with Frontend

### CORS Configuration

The API is configured to accept requests from:
- `http://localhost:5173` (Vite default)
- `http://localhost:3000` (React default)
- Your configured `FRONTEND_URL`

### Frontend Connection

In your frontend (`/MovoAI/`), configure the API base URL:

```typescript
// constants.ts or config file
export const API_BASE_URL = "http://localhost:8000/api/v1";
```

### Authentication Flow

1. **User clicks "Login with Email"**
2. Frontend sends email to `/auth/email/send-code`
3. User enters code from email
4. Frontend sends code to `/auth/email/verify-code` with user data (if new user)
5. Backend returns `access_token` and `refresh_token`
6. Frontend stores tokens (localStorage or secure cookie)
7. Frontend includes token in subsequent requests:
   ```
   Authorization: Bearer {access_token}
   ```

### Example Frontend Code

```typescript
// Send verification code
const sendCode = async (email: string) => {
  const response = await fetch(`${API_BASE_URL}/auth/email/send-code`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ email })
  });
  return response.json();
};

// Verify code and login
const verifyCode = async (email: string, code: string, userData?: any) => {
  const response = await fetch(`${API_BASE_URL}/auth/email/verify-code`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ email, code, user_data: userData })
  });
  const data = await response.json();
  // Store tokens
  localStorage.setItem('access_token', data.access_token);
  localStorage.setItem('refresh_token', data.refresh_token);
  return data;
};

// Get user profile
const getProfile = async () => {
  const token = localStorage.getItem('access_token');
  const response = await fetch(`${API_BASE_URL}/users/me`, {
    headers: { 'Authorization': `Bearer ${token}` }
  });
  return response.json();
};
```

## Next Steps

1. ✅ Backend running
2. ✅ Authentication working
3. ✅ API documentation available
4. 🔄 Test with frontend at `/MovoAI/`
5. 🔄 Implement Telegram Web App integration
6. 🔄 Configure SMS (Twilio) for production
7. ➡️ Proceed to Phase 2 (Workout Management)

## Support

- **API Documentation**: http://localhost:8000/docs
- **Full README**: `/movoai_api/README.md`
- **Project Plan**: `/movoai_api/PROJECT_PLAN.md`

## Environment Variables Reference

### Required
- `DATABASE_URL` - PostgreSQL connection string
- `JWT_SECRET_KEY` - JWT signing key
- `JWT_REFRESH_SECRET_KEY` - Refresh token signing key
- `TELEGRAM_BOT_TOKEN` - Telegram bot token

### Optional (for production)
- `TWILIO_ACCOUNT_SID` - Twilio account SID
- `TWILIO_AUTH_TOKEN` - Twilio auth token
- `TWILIO_PHONE_NUMBER` - Twilio phone number
- `SENDGRID_API_KEY` - SendGrid API key
- `GOOGLE_CLIENT_ID` - Google OAuth client ID
- `GOOGLE_CLIENT_SECRET` - Google OAuth secret

### Application
- `FRONTEND_URL` - Frontend URL for CORS
- `DEBUG` - Enable debug mode (True/False)

---

**You're all set!** 🚀

Your Phase 1 backend is ready for frontend integration.

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

## Key Points

- **Tokens**: Access (15min), Refresh (30 days), Login (5min, single-use)
- **Rate limits**: 3 login codes/hour, 3 verification attempts/token
- **Error 401**: Refresh token, then retry
- **Bot**: `@MovoKioBot` - user sends `/login` to get code

See `examples/telegram_login.html` for working example.

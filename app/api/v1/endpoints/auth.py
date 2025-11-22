"""
Authentication endpoints - Telegram, SMS, Email, Google OAuth
"""
from datetime import datetime, timedelta
from typing import Dict
import secrets
import hashlib
import hmac
import json
import urllib.parse
import string
import random
from fastapi import APIRouter, Depends, HTTPException, status, Query, BackgroundTasks
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_

from app.database.session import get_db
from app.core.security import (
    verify_telegram_auth,
    generate_verification_code,
    create_access_token,
    create_refresh_token,
    decode_refresh_token
)
from app.core.config import settings
from app.models.user import User
from app.models.auth_method import UserAuthMethod
from app.models.verification_code import VerificationCode
from app.schemas.auth import (
    TelegramAuthRequest,
    TelegramAuthResponse,
    TelegramAutoLogin,
    TelegramTokenRequest,
    TelegramTokenVerify,
    PhoneSendCodeRequest,
    PhoneVerifyCodeRequest,
    PhoneAuthResponse,
    EmailSendCodeRequest,
    EmailVerifyCodeRequest,
    EmailAuthResponse,
    GoogleAuthResponse,
    AuthMethodResponse,
    CodeSentResponse,
    MessageResponse,
    Token,
    TokenRefresh,
)
from app.schemas.user import UserCreate, UserResponse
from app.services.external import sms_service, email_service, google_oauth_service
from app.dependencies import get_current_user

router = APIRouter()


def create_user_with_auth_method(
    db: Session,
    user_data: UserCreate,
    auth_provider: str,
    auth_identifier: str,
    auth_data: Dict = None
) -> User:
    """Helper function to create user with auth method"""
    # Create user
    referral_code = generate_referral_code(db)
    user = User(
        telegram_id=None,  # Will be set if auth_provider is telegram
        referral_code=referral_code,
        **user_data.model_dump()
    )
    db.add(user)
    db.flush()  # Get user.user_id
    
    # Update telegram_id if telegram auth
    if auth_provider == "telegram":
        user.telegram_id = int(auth_identifier)
    
    # Create auth method
    auth_method = UserAuthMethod(
        user_id=user.user_id,
        auth_provider=auth_provider,
        auth_identifier=auth_identifier,
        auth_data=auth_data or {},
        is_verified=True,
        is_primary=True
    )
    db.add(auth_method)
    db.commit()
    db.refresh(user)
    
    return user


def get_or_create_user(
    db: Session,
    auth_provider: str,
    auth_identifier: str,
    user_data: UserCreate = None,
    auth_data: Dict = None
) -> tuple[User, bool]:
    """Get existing user or create new one. Returns (user, is_new_user)"""
    # Check if auth method exists
    auth_method = db.query(UserAuthMethod).filter(
        and_(
            UserAuthMethod.auth_provider == auth_provider,
            UserAuthMethod.auth_identifier == auth_identifier
        )
    ).first()
    
    if auth_method:
        # Existing user
        return auth_method.user, False
    
    # New user
    if not user_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User data required for new user registration"
        )
    
    user = create_user_with_auth_method(db, user_data, auth_provider, auth_identifier, auth_data)
    return user, True


def generate_tokens(user_id: int) -> Dict[str, str]:
    """Generate access and refresh tokens"""
    access_token = create_access_token({"user_id": user_id})
    refresh_token = create_refresh_token({"user_id": user_id})
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }


def generate_referral_code(db: Session, length: int = 8) -> str:
    """Generate a unique referral code"""
    characters = string.ascii_uppercase + string.digits
    while True:
        code = ''.join(random.choices(characters, k=length))
        # Check if code already exists
        existing = db.query(User).filter(User.referral_code == code).first()
        if not existing:
            return code


def validate_telegram_webapp_data(init_data: str, bot_token: str) -> bool:
    """
    Validates Telegram WebApp initData using HMAC-SHA256.
    https://core.telegram.org/bots/webapps#validating-data-received-via-the-mini-app
    """
    try:
        print(f"DEBUG: Validating init_data: {init_data[:100]}...")  # Log first 100 chars
        
        # Parse init_data
        params = dict(param.split('=', 1) for param in init_data.split('&'))
        
        # URL-decode the values
        for key in params:
            params[key] = urllib.parse.unquote(params[key])
        
        if 'hash' not in params:
            print("DEBUG: No hash in params")
            return False
        
        received_hash = params.pop('hash')
        print(f"DEBUG: Received hash: {received_hash}")
        
        # Create data-check-string
        data_check_string = '\n'.join(f"{k}={v}" for k, v in sorted(params.items()))
        print(f"DEBUG: Data check string: {data_check_string[:200]}...")
        
        # Calculate hash
        secret_key = hmac.new("WebAppData".encode(), bot_token.encode(), hashlib.sha256).digest()
        calculated_hash = hmac.new(secret_key, data_check_string.encode(), hashlib.sha256).hexdigest()
        print(f"DEBUG: Calculated hash: {calculated_hash}")
        
        result = calculated_hash == received_hash
        print(f"DEBUG: Hash match: {result}")
        
        return result
    except Exception as e:
        print(f"DEBUG: Exception in validation: {e}")
        return False


def parse_telegram_init_data(init_data: str) -> dict:
    """Parse Telegram WebApp initData and extract user info."""
    try:
        params = dict(param.split('=', 1) for param in init_data.split('&'))
        
        if 'user' in params:
            user_json = urllib.parse.unquote(params['user'])
            return json.loads(user_json)
        
        return {}
    except Exception:
        return {}


async def send_telegram_message(chat_id: int, text: str, reply_markup: dict = None):
    """Helper function to send messages via Telegram Bot API"""
    import httpx
    
    url = f"https://api.telegram.org/bot{settings.TELEGRAM_BOT_TOKEN}/sendMessage"
    
    payload = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "Markdown"
    }
    
    if reply_markup:
        payload["reply_markup"] = reply_markup
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=payload)
            return response.status_code == 200
    except Exception as e:
        print(f"Error sending Telegram message: {e}")
        return False


# =============== Telegram Authentication ===============
@router.post("/telegram/login", response_model=TelegramAuthResponse)
async def telegram_login(
    auth_request: TelegramAuthRequest,
    user_data: UserCreate = None,
    db: Session = Depends(get_db)
):
    """
    Authenticate or register user via Telegram
    """
    # Verify Telegram data
    telegram_data = auth_request.model_dump()
    if not verify_telegram_auth(telegram_data):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Telegram authentication data"
        )
    
    telegram_id = str(auth_request.id)
    auth_data = {
        "username": auth_request.username,
        "first_name": auth_request.first_name,
        "last_name": auth_request.last_name,
        "photo_url": auth_request.photo_url
    }
    
    # Get or create user
    user, is_new = get_or_create_user(
        db=db,
        auth_provider="telegram",
        auth_identifier=telegram_id,
        user_data=user_data,
        auth_data=auth_data
    )
    
    # Generate tokens
    tokens = generate_tokens(user.user_id)
    
    return TelegramAuthResponse(
        user=UserResponse.model_validate(user),
        is_new_user=is_new,
        **tokens
    )


@router.post("/telegram/link", response_model=MessageResponse)
async def telegram_link(
    auth_request: TelegramAuthRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Link Telegram account to existing user
    """
    # Verify Telegram data
    telegram_data = auth_request.model_dump()
    if not verify_telegram_auth(telegram_data):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Telegram authentication data"
        )
    
    telegram_id = str(auth_request.id)
    
    # Check if telegram already linked
    existing = db.query(UserAuthMethod).filter(
        and_(
            UserAuthMethod.auth_provider == "telegram",
            UserAuthMethod.auth_identifier == telegram_id
        )
    ).first()
    
    if existing:
        if existing.user_id == current_user.user_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Telegram already linked to your account"
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Telegram already linked to another account"
            )
    
    # Link Telegram to user
    auth_method = UserAuthMethod(
        user_id=current_user.user_id,
        auth_provider="telegram",
        auth_identifier=telegram_id,
        auth_data={
            "username": auth_request.username,
            "first_name": auth_request.first_name,
            "last_name": auth_request.last_name,
            "photo_url": auth_request.photo_url
        },
        is_verified=True,
        is_primary=False
    )
    
    # Update user telegram_id if not set
    if not current_user.telegram_id:
        current_user.telegram_id = auth_request.id
    
    db.add(auth_method)
    db.commit()
    
    return MessageResponse(message="Telegram account linked successfully")


@router.post("/telegram/auto-login", response_model=TelegramAuthResponse)
async def telegram_auto_login(
    request: TelegramAutoLogin,
    db: Session = Depends(get_db)
):
    """
    Automatic login when user opens web app from Telegram (Mini App).
    Validates Telegram WebApp initData to ensure authenticity.
    """
    # Validate Telegram WebApp data
    if not validate_telegram_webapp_data(request.init_data, settings.TELEGRAM_BOT_TOKEN):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Telegram authentication"
        )
    
    # Parse init_data to get user info
    user_data_dict = parse_telegram_init_data(request.init_data)
    if not user_data_dict:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Could not parse Telegram user data"
        )
    
    telegram_id = str(user_data_dict.get("id"))
    username = user_data_dict.get("username")
    first_name = user_data_dict.get("first_name", "")
    last_name = user_data_dict.get("last_name", "")
    
    # Get or create user
    user = db.query(User).filter(User.telegram_id == telegram_id).first()
    is_new = False
    
    if not user:
        # Create new user (profile will be completed later)
        referral_code = generate_referral_code(db)
        user = User(
            telegram_id=int(telegram_id),
            referral_code=referral_code,
            is_active=True
        )
        db.add(user)
        db.flush()
        
        # Create auth method
        auth_method = UserAuthMethod(
            user_id=user.user_id,
            auth_provider="telegram",
            auth_identifier=telegram_id,
            auth_data={
                "username": username,
                "first_name": first_name,
                "last_name": last_name
            },
            is_verified=True,
            is_primary=True
        )
        db.add(auth_method)
        db.commit()
        db.refresh(user)
        is_new = True
    
    # Generate JWT tokens
    tokens = generate_tokens(user.user_id)
    
    return TelegramAuthResponse(
        user=UserResponse.model_validate(user),
        is_new_user=is_new,
        **tokens
    )


@router.post("/telegram/request-token")
async def telegram_request_token(
    request: TelegramTokenRequest,
    db: Session = Depends(get_db)
):
    """
    Called by Telegram bot when user sends /login command.
    Generates a short-lived token that user can use on web.
    """
    telegram_id = request.telegram_id
    
    # Check if user exists, create if not
    user = db.query(User).filter(User.telegram_id == telegram_id).first()
    if not user:
        referral_code = generate_referral_code(db)
        user = User(
            telegram_id=int(telegram_id),
            referral_code=referral_code,
            is_active=True
        )
        db.add(user)
        db.flush()
        
        # Create auth method
        auth_method = UserAuthMethod(
            user_id=user.user_id,
            auth_provider="telegram",
            auth_identifier=telegram_id,
            auth_data={
                "username": request.username,
                "first_name": request.first_name
            },
            is_verified=True,
            is_primary=True
        )
        db.add(auth_method)
        db.commit()
    
    # Generate random 6-character token
    login_token = secrets.token_urlsafe(6)[:6].upper()
    
    # Store in verification_code table
    verification = VerificationCode(
        identifier=telegram_id,
        code=login_token,
        code_type="telegram",
        expires_at=datetime.utcnow() + timedelta(minutes=5)
    )
    db.add(verification)
    db.commit()
    
    return {
        "token": login_token,
        "expires_in": 300  # 5 minutes
    }


@router.post("/telegram/verify-token", response_model=TelegramAuthResponse)
async def telegram_verify_token(
    request: TelegramTokenVerify,
    db: Session = Depends(get_db)
):
    """
    Web app calls this endpoint with the token from Telegram.
    Returns JWT tokens if valid.
    """
    # Find valid verification code
    verification = db.query(VerificationCode).filter(
        and_(
            VerificationCode.code == request.token.upper(),
            VerificationCode.code_type == "telegram",
            VerificationCode.verified == False,
            VerificationCode.expires_at > datetime.utcnow()
        )
    ).order_by(VerificationCode.created_at.desc()).first()
    
    if not verification:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired token"
        )
    
    # Check attempts
    if verification.attempts >= settings.MAX_CODE_ATTEMPTS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Too many attempts"
        )
    
    verification.attempts += 1
    db.commit()
    
    # Get user by telegram_id
    telegram_id = verification.identifier
    user = db.query(User).filter(User.telegram_id == telegram_id).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Mark token as used
    verification.verified = True
    db.commit()
    
    # Generate JWT tokens
    tokens = generate_tokens(user.user_id)
    
    return TelegramAuthResponse(
        user=UserResponse.model_validate(user),
        is_new_user=False,
        **tokens
    )


@router.post("/telegram/webhook")
async def telegram_webhook(
    update: dict,
    db: Session = Depends(get_db)
):
    """
    Webhook for Telegram bot to receive messages.
    Handles user registration and token requests.
    """
    try:
        if "message" not in update:
            return {"ok": True}
        
        message = update["message"]
        telegram_user = message.get("from", {})
        text = message.get("text", "")
        chat_id = message.get("chat", {}).get("id")
        
        telegram_id = str(telegram_user.get("id"))
        username = telegram_user.get("username")
        first_name = telegram_user.get("first_name", "User")
        
        # Handle /start command - register user
        if text.startswith("/start"):
            user = db.query(User).filter(User.telegram_id == telegram_id).first()
            
            if not user:
                referral_code = generate_referral_code(db)
                user = User(
                    telegram_id=int(telegram_id),
                    referral_code=referral_code,
                    is_active=True
                )
                db.add(user)
                db.flush()
                
                # Create auth method
                auth_method = UserAuthMethod(
                    user_id=user.user_id,
                    auth_provider="telegram",
                    auth_identifier=telegram_id,
                    auth_data={
                        "username": username,
                        "first_name": first_name
                    },
                    is_verified=True,
                    is_primary=True
                )
                db.add(auth_method)
                db.commit()
            
            # Send welcome message with web app button
            await send_telegram_message(
                chat_id,
                f"Welcome {first_name}! 🎉\n\n"
                f"Choose how to access MovoAI:\n"
                f"• Tap the button below to open the app directly\n"
                f"• Or use /login to get a token for web browser",
                reply_markup={
                    "inline_keyboard": [[
                        {
                            "text": "Open MovoAI App",
                            "web_app": {"url": f"{settings.FRONTEND_URL}"}
                        }
                    ]]
                }
            )
        
        # Handle /login command - generate token
        elif text.startswith("/login"):
            user = db.query(User).filter(User.telegram_id == telegram_id).first()
            
            if not user:
                referral_code = generate_referral_code(db)
                user = User(
                    telegram_id=int(telegram_id),
                    referral_code=referral_code,
                    is_active=True
                )
                db.add(user)
                db.flush()
                
                # Create auth method
                auth_method = UserAuthMethod(
                    user_id=user.user_id,
                    auth_provider="telegram",
                    auth_identifier=telegram_id,
                    auth_data={
                        "username": username,
                        "first_name": first_name
                    },
                    is_verified=True,
                    is_primary=True
                )
                db.add(auth_method)
                db.commit()
            
            # Generate token
            login_token = secrets.token_urlsafe(6)[:6].upper()
            
            verification = VerificationCode(
                identifier=telegram_id,
                code=login_token,
                code_type="telegram",
                expires_at=datetime.utcnow() + timedelta(minutes=5)
            )
            db.add(verification)
            db.commit()
            
            # Send token to user
            await send_telegram_message(
                chat_id,
                f"🔐 Your login token:\n\n"
                f"`{login_token}`\n\n"
                f"Enter this on {settings.FRONTEND_URL} within 5 minutes.\n"
                f"This token can only be used once."
            )
        
        return {"ok": True}
        
    except Exception as e:
        print(f"Webhook error: {e}")
        return {"ok": False}


# =============== Phone/SMS Authentication ===============
@router.post("/phone/send-code", response_model=CodeSentResponse)
async def phone_send_code(
    request: PhoneSendCodeRequest,
    db: Session = Depends(get_db)
):
    """
    Send verification code via SMS
    """
    phone_number = request.phone_number
    
    # Check rate limiting
    one_hour_ago = datetime.utcnow() - timedelta(hours=1)
    recent_codes = db.query(VerificationCode).filter(
        and_(
            VerificationCode.identifier == phone_number,
            VerificationCode.code_type == "sms",
            VerificationCode.created_at >= one_hour_ago
        )
    ).count()
    
    if recent_codes >= settings.MAX_CODES_PER_HOUR:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"Maximum {settings.MAX_CODES_PER_HOUR} codes per hour exceeded"
        )
    
    # Generate code
    code = generate_verification_code()
    expires_at = datetime.utcnow() + timedelta(minutes=settings.CODE_EXPIRY_MINUTES_SMS)
    
    # Save to database
    verification = VerificationCode(
        identifier=phone_number,
        code=code,
        code_type="sms",
        expires_at=expires_at
    )
    db.add(verification)
    db.commit()
    
    # Send SMS
    success = await sms_service.send_verification_code(phone_number, code)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to send SMS"
        )
    
    return CodeSentResponse(
        message="Verification code sent successfully",
        expires_in_seconds=settings.CODE_EXPIRY_MINUTES_SMS * 60
    )


@router.post("/phone/verify-code", response_model=PhoneAuthResponse)
async def phone_verify_code(
    request: PhoneVerifyCodeRequest,
    db: Session = Depends(get_db)
):
    """
    Verify SMS code and login/register user
    """
    phone_number = request.phone_number
    code = request.code
    
    # Find latest valid code
    verification = db.query(VerificationCode).filter(
        and_(
            VerificationCode.identifier == phone_number,
            VerificationCode.code_type == "sms",
            VerificationCode.code == code,
            VerificationCode.expires_at > datetime.utcnow(),
            VerificationCode.verified == False
        )
    ).order_by(VerificationCode.created_at.desc()).first()
    
    if not verification:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired verification code"
        )
    
    # Check attempts
    if verification.attempts >= settings.MAX_CODE_ATTEMPTS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Maximum verification attempts exceeded"
        )
    
    verification.attempts += 1
    
    # Verify code
    if verification.code != code:
        db.commit()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid verification code"
        )
    
    # Mark as verified
    verification.verified = True
    db.commit()
    
    # Get or create user
    user, is_new = get_or_create_user(
        db=db,
        auth_provider="sms",
        auth_identifier=phone_number,
        user_data=request.user_data
    )
    
    # Generate tokens
    tokens = generate_tokens(user.user_id)
    
    return PhoneAuthResponse(
        user=UserResponse.model_validate(user),
        is_new_user=is_new,
        **tokens
    )


@router.post("/phone/link", response_model=MessageResponse)
async def phone_link(
    request: PhoneVerifyCodeRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Link phone number to existing account
    """
    # Verify code (similar to phone_verify_code)
    phone_number = request.phone_number
    code = request.code
    
    verification = db.query(VerificationCode).filter(
        and_(
            VerificationCode.identifier == phone_number,
            VerificationCode.code_type == "sms",
            VerificationCode.code == code,
            VerificationCode.expires_at > datetime.utcnow(),
            VerificationCode.verified == False
        )
    ).order_by(VerificationCode.created_at.desc()).first()
    
    if not verification or verification.code != code:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired verification code"
        )
    
    verification.verified = True
    db.commit()
    
    # Check if phone already linked
    existing = db.query(UserAuthMethod).filter(
        and_(
            UserAuthMethod.auth_provider == "sms",
            UserAuthMethod.auth_identifier == phone_number
        )
    ).first()
    
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Phone number already linked to an account"
        )
    
    # Link phone to user
    auth_method = UserAuthMethod(
        user_id=current_user.user_id,
        auth_provider="sms",
        auth_identifier=phone_number,
        is_verified=True,
        is_primary=False
    )
    db.add(auth_method)
    db.commit()
    
    return MessageResponse(message="Phone number linked successfully")


# =============== Email Authentication ===============
@router.post("/email/send-code", response_model=CodeSentResponse)
async def email_send_code(
    request: EmailSendCodeRequest,
    db: Session = Depends(get_db)
):
    """
    Send verification code via email
    """
    email = request.email
    
    # Check rate limiting
    one_hour_ago = datetime.utcnow() - timedelta(hours=1)
    recent_codes = db.query(VerificationCode).filter(
        and_(
            VerificationCode.identifier == email,
            VerificationCode.code_type == "email",
            VerificationCode.created_at >= one_hour_ago
        )
    ).count()
    
    if recent_codes >= settings.MAX_CODES_PER_HOUR:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"Maximum {settings.MAX_CODES_PER_HOUR} codes per hour exceeded"
        )
    
    # Generate code
    code = generate_verification_code()
    expires_at = datetime.utcnow() + timedelta(minutes=settings.CODE_EXPIRY_MINUTES_EMAIL)
    
    # Save to database
    verification = VerificationCode(
        identifier=email,
        code=code,
        code_type="email",
        expires_at=expires_at
    )
    db.add(verification)
    db.commit()
    
    # Send email
    success = await email_service.send_verification_code(email, code)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to send email"
        )
    
    return CodeSentResponse(
        message="Verification code sent successfully",
        expires_in_seconds=settings.CODE_EXPIRY_MINUTES_EMAIL * 60
    )


@router.post("/email/verify-code", response_model=EmailAuthResponse)
async def email_verify_code(
    request: EmailVerifyCodeRequest,
    db: Session = Depends(get_db)
):
    """
    Verify email code and login/register user
    """
    email = request.email
    code = request.code
    
    # Find latest valid code
    verification = db.query(VerificationCode).filter(
        and_(
            VerificationCode.identifier == email,
            VerificationCode.code_type == "email",
            VerificationCode.code == code,
            VerificationCode.expires_at > datetime.utcnow(),
            VerificationCode.verified == False
        )
    ).order_by(VerificationCode.created_at.desc()).first()
    
    if not verification:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired verification code"
        )
    
    # Check attempts
    if verification.attempts >= settings.MAX_CODE_ATTEMPTS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Maximum verification attempts exceeded"
        )
    
    verification.attempts += 1
    
    # Verify code
    if verification.code != code:
        db.commit()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid verification code"
        )
    
    # Mark as verified
    verification.verified = True
    db.commit()
    
    # Get or create user
    user, is_new = get_or_create_user(
        db=db,
        auth_provider="email",
        auth_identifier=email,
        user_data=request.user_data
    )
    
    # Generate tokens
    tokens = generate_tokens(user.user_id)
    
    return EmailAuthResponse(
        user=UserResponse.model_validate(user),
        is_new_user=is_new,
        **tokens
    )


@router.post("/email/link", response_model=MessageResponse)
async def email_link(
    request: EmailVerifyCodeRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Link email to existing account
    """
    email = request.email
    code = request.code
    
    # Verify code
    verification = db.query(VerificationCode).filter(
        and_(
            VerificationCode.identifier == email,
            VerificationCode.code_type == "email",
            VerificationCode.code == code,
            VerificationCode.expires_at > datetime.utcnow(),
            VerificationCode.verified == False
        )
    ).order_by(VerificationCode.created_at.desc()).first()
    
    if not verification or verification.code != code:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired verification code"
        )
    
    verification.verified = True
    db.commit()
    
    # Check if email already linked
    existing = db.query(UserAuthMethod).filter(
        and_(
            UserAuthMethod.auth_provider == "email",
            UserAuthMethod.auth_identifier == email
        )
    ).first()
    
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already linked to an account"
        )
    
    # Link email to user
    auth_method = UserAuthMethod(
        user_id=current_user.user_id,
        auth_provider="email",
        auth_identifier=email,
        is_verified=True,
        is_primary=False
    )
    db.add(auth_method)
    db.commit()
    
    return MessageResponse(message="Email linked successfully")


# =============== Google OAuth Authentication ===============
@router.get("/google/login")
async def google_login():
    """
    Redirect to Google OAuth consent screen
    """
    if not settings.GOOGLE_CLIENT_ID:
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail="Google OAuth not configured"
        )
    
    # Build Google OAuth URL
    google_oauth_url = (
        f"https://accounts.google.com/o/oauth2/v2/auth?"
        f"client_id={settings.GOOGLE_CLIENT_ID}&"
        f"redirect_uri={settings.GOOGLE_REDIRECT_URI}&"
        f"response_type=code&"
        f"scope=openid%20email%20profile&"
        f"access_type=offline"
    )
    
    return RedirectResponse(url=google_oauth_url)


@router.get("/google/callback", response_model=GoogleAuthResponse)
async def google_callback(
    code: str = Query(...),
    user_data: UserCreate = None,
    db: Session = Depends(get_db)
):
    """
    Handle Google OAuth callback
    Note: In production, this should exchange code for token server-side
    For now, we'll accept the Google ID token directly
    """
    # In a real implementation, exchange code for access_token and id_token
    # For this example, we'll expect the frontend to send the id_token as 'code'
    google_user = await google_oauth_service.verify_token(code)
    
    if not google_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Google authentication"
        )
    
    google_id = google_user['google_id']
    auth_data = {
        "email": google_user.get('email'),
        "name": google_user.get('name'),
        "picture": google_user.get('picture'),
        "email_verified": google_user.get('email_verified')
    }
    
    # Get or create user
    user, is_new = get_or_create_user(
        db=db,
        auth_provider="google",
        auth_identifier=google_id,
        user_data=user_data,
        auth_data=auth_data
    )
    
    # Generate tokens
    tokens = generate_tokens(user.user_id)
    
    return GoogleAuthResponse(
        user=UserResponse.model_validate(user),
        is_new_user=is_new,
        **tokens
    )


@router.post("/google/link", response_model=MessageResponse)
async def google_link(
    id_token: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Link Google account to existing user
    """
    google_user = await google_oauth_service.verify_token(id_token)
    
    if not google_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Google authentication"
        )
    
    google_id = google_user['google_id']
    
    # Check if Google account already linked
    existing = db.query(UserAuthMethod).filter(
        and_(
            UserAuthMethod.auth_provider == "google",
            UserAuthMethod.auth_identifier == google_id
        )
    ).first()
    
    if existing:
        if existing.user_id == current_user.user_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Google account already linked to your account"
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Google account already linked to another account"
            )
    
    # Link Google to user
    auth_method = UserAuthMethod(
        user_id=current_user.user_id,
        auth_provider="google",
        auth_identifier=google_id,
        auth_data={
            "email": google_user.get('email'),
            "name": google_user.get('name'),
            "picture": google_user.get('picture')
        },
        is_verified=True,
        is_primary=False
    )
    db.add(auth_method)
    db.commit()
    
    return MessageResponse(message="Google account linked successfully")


# =============== Token Management ===============
@router.post("/refresh", response_model=Token)
async def refresh_token(
    request: TokenRefresh,
    db: Session = Depends(get_db)
):
    """
    Refresh access token using refresh token
    """
    payload = decode_refresh_token(request.refresh_token)
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )
    
    user_id = payload.get("user_id")
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload"
        )
    
    # Verify user exists
    user = db.query(User).filter(User.user_id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )
    
    # Generate new tokens
    tokens = generate_tokens(user_id)
    
    return Token(**tokens)


@router.post("/logout", response_model=MessageResponse)
async def logout(
    current_user: User = Depends(get_current_user)
):
    """
    Logout user (client should delete tokens)
    In production, add refresh token to blacklist
    """
    return MessageResponse(message="Logged out successfully")


# =============== Auth Method Management ===============
@router.get("/methods", response_model=list[AuthMethodResponse])
async def get_auth_methods(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get all authentication methods for current user
    """
    auth_methods = db.query(UserAuthMethod).filter(
        UserAuthMethod.user_id == current_user.id
    ).all()
    
    return [AuthMethodResponse.model_validate(am) for am in auth_methods]


@router.delete("/methods/{method_id}", response_model=MessageResponse)
async def delete_auth_method(
    method_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Remove authentication method (must have at least one remaining)
    """
    # Get auth method
    auth_method = db.query(UserAuthMethod).filter(
        and_(
            UserAuthMethod.id == method_id,
            UserAuthMethod.user_id == current_user.id
        )
    ).first()
    
    if not auth_method:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Authentication method not found"
        )
    
    # Check if user has other auth methods
    other_methods = db.query(UserAuthMethod).filter(
        and_(
            UserAuthMethod.user_id == current_user.user_id,
            UserAuthMethod.id != method_id
        )
    ).count()
    
    if other_methods == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot remove last authentication method"
        )
    
    # If removing primary method, set another as primary
    if auth_method.is_primary:
        new_primary = db.query(UserAuthMethod).filter(
            and_(
                UserAuthMethod.user_id == current_user.user_id,
                UserAuthMethod.id != method_id
            )
        ).first()
        if new_primary:
            new_primary.is_primary = True
    
    db.delete(auth_method)
    db.commit()
    
    return MessageResponse(message="Authentication method removed successfully")


@router.post("/methods/{method_id}/set-primary", response_model=MessageResponse)
async def set_primary_auth_method(
    method_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Set authentication method as primary
    """
    # Get auth method
    auth_method = db.query(UserAuthMethod).filter(
        and_(
            UserAuthMethod.id == method_id,
            UserAuthMethod.user_id == current_user.id
        )
    ).first()
    
    if not auth_method:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Authentication method not found"
        )
    
    # Remove primary from all other methods
    db.query(UserAuthMethod).filter(
        UserAuthMethod.user_id == current_user.user_id
    ).update({"is_primary": False})
    
    # Set as primary
    auth_method.is_primary = True
    db.commit()
    
    return MessageResponse(message="Primary authentication method updated")

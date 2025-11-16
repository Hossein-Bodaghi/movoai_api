"""
Third-party service integrations
"""
from typing import Optional
from twilio.rest import Client as TwilioClient
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from google.oauth2 import id_token
from google.auth.transport import requests as google_requests

from app.core.config import settings


class SMSService:
    """Service for sending SMS via Twilio"""
    
    def __init__(self):
        if settings.TWILIO_ACCOUNT_SID and settings.TWILIO_AUTH_TOKEN:
            self.client = TwilioClient(
                settings.TWILIO_ACCOUNT_SID,
                settings.TWILIO_AUTH_TOKEN
            )
            self.from_number = settings.TWILIO_PHONE_NUMBER
        else:
            self.client = None
    
    async def send_sms(self, to_number: str, message: str) -> bool:
        """Send SMS to phone number"""
        if not self.client:
            print(f"[SMS MOCK] Would send to {to_number}: {message}")
            return True
        
        try:
            message = self.client.messages.create(
                body=message,
                from_=self.from_number,
                to=to_number
            )
            return message.sid is not None
        except Exception as e:
            print(f"Error sending SMS: {e}")
            return False
    
    async def send_verification_code(self, phone_number: str, code: str) -> bool:
        """Send verification code via SMS"""
        message = f"Your MovoAI verification code is: {code}. Valid for {settings.CODE_EXPIRY_MINUTES_SMS} minutes."
        return await self.send_sms(phone_number, message)


class EmailService:
    """Service for sending emails via SendGrid"""
    
    def __init__(self):
        if settings.SENDGRID_API_KEY:
            self.client = SendGridAPIClient(settings.SENDGRID_API_KEY)
        else:
            self.client = None
    
    async def send_email(self, to_email: str, subject: str, html_content: str) -> bool:
        """Send email"""
        if not self.client:
            print(f"[EMAIL MOCK] Would send to {to_email}: {subject}")
            return True
        
        try:
            message = Mail(
                from_email=(settings.EMAIL_FROM_ADDRESS, settings.EMAIL_FROM_NAME),
                to_emails=to_email,
                subject=subject,
                html_content=html_content
            )
            response = self.client.send(message)
            return response.status_code in [200, 201, 202]
        except Exception as e:
            print(f"Error sending email: {e}")
            return False
    
    async def send_verification_code(self, email: str, code: str) -> bool:
        """Send verification code via email"""
        subject = "Your MovoAI Verification Code"
        html_content = f"""
        <html>
        <body>
            <h2>MovoAI Verification Code</h2>
            <p>Your verification code is:</p>
            <h1 style="color: #4CAF50; letter-spacing: 5px;">{code}</h1>
            <p>This code will expire in {settings.CODE_EXPIRY_MINUTES_EMAIL} minutes.</p>
            <p>If you didn't request this code, please ignore this email.</p>
        </body>
        </html>
        """
        return await self.send_email(email, subject, html_content)


class GoogleOAuthService:
    """Service for Google OAuth authentication"""
    
    @staticmethod
    async def verify_token(token: str) -> Optional[dict]:
        """Verify Google ID token and return user info"""
        if not settings.GOOGLE_CLIENT_ID:
            return None
        
        try:
            idinfo = id_token.verify_oauth2_token(
                token,
                google_requests.Request(),
                settings.GOOGLE_CLIENT_ID
            )
            
            # Verify issuer
            if idinfo['iss'] not in ['accounts.google.com', 'https://accounts.google.com']:
                return None
            
            return {
                'google_id': idinfo['sub'],
                'email': idinfo.get('email'),
                'name': idinfo.get('name'),
                'picture': idinfo.get('picture'),
                'email_verified': idinfo.get('email_verified', False)
            }
        except Exception as e:
            print(f"Error verifying Google token: {e}")
            return None


# Service instances
sms_service = SMSService()
email_service = EmailService()
google_oauth_service = GoogleOAuthService()

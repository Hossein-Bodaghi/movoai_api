"""
Tests for authentication endpoints
"""
import pytest
from fastapi import status
from unittest.mock import patch, AsyncMock


def test_telegram_login_invalid_hash(client, sample_user_data):
    """Test Telegram login with invalid hash"""
    telegram_data = {
        "id": 123456789,
        "first_name": "Test",
        "last_name": "User",
        "username": "testuser",
        "auth_date": 1234567890,
        "hash": "invalid_hash"
    }
    
    response = client.post("/api/v1/auth/telegram/login", json=telegram_data)
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_phone_send_code(client):
    """Test sending SMS verification code"""
    with patch('app.services.external.sms_service.send_verification_code', new_callable=AsyncMock, return_value=True):
        response = client.post("/api/v1/auth/phone/send-code", json={
            "phone_number": "+1234567890"
        })
        assert response.status_code == status.HTTP_200_OK
        assert "expires_in_seconds" in response.json()


def test_phone_verify_code_invalid(client, sample_user_data):
    """Test verifying invalid SMS code"""
    response = client.post("/api/v1/auth/phone/verify-code", json={
        "phone_number": "+1234567890",
        "code": "000000",
        "user_data": sample_user_data
    })
    assert response.status_code == status.HTTP_400_BAD_REQUEST


def test_email_send_code(client):
    """Test sending email verification code"""
    with patch('app.services.external.email_service.send_verification_code', new_callable=AsyncMock, return_value=True):
        response = client.post("/api/v1/auth/email/send-code", json={
            "email": "test@example.com"
        })
        assert response.status_code == status.HTTP_200_OK
        assert "expires_in_seconds" in response.json()


def test_email_verify_code_invalid(client, sample_user_data):
    """Test verifying invalid email code"""
    response = client.post("/api/v1/auth/email/verify-code", json={
        "email": "test@example.com",
        "code": "000000",
        "user_data": sample_user_data
    })
    assert response.status_code == status.HTTP_400_BAD_REQUEST


def test_refresh_token_invalid(client):
    """Test refresh token with invalid token"""
    response = client.post("/api/v1/auth/refresh", json={
        "refresh_token": "invalid_token"
    })
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_get_auth_methods_unauthorized(client):
    """Test getting auth methods without authentication"""
    response = client.get("/api/v1/auth/methods")
    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_google_login_not_configured(client):
    """Test Google login when not configured"""
    # This test assumes Google OAuth is not configured in test environment
    with patch('app.core.config.settings.GOOGLE_CLIENT_ID', None):
        response = client.get("/api/v1/auth/google/login")
        assert response.status_code == status.HTTP_501_NOT_IMPLEMENTED

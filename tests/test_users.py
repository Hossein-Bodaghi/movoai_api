"""
Tests for user endpoints
"""
import pytest
from fastapi import status


def test_health_check(client):
    """Test health check endpoint"""
    response = client.get("/health")
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["status"] == "healthy"


def test_root_endpoint(client):
    """Test root endpoint"""
    response = client.get("/")
    assert response.status_code == status.HTTP_200_OK
    assert "message" in response.json()


def test_get_current_user_unauthorized(client):
    """Test getting current user without authentication"""
    response = client.get("/api/v1/users/me")
    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_update_user_unauthorized(client, sample_user_data):
    """Test updating user without authentication"""
    response = client.put("/api/v1/users/me", json={"age": 30})
    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_delete_user_unauthorized(client):
    """Test deleting user without authentication"""
    response = client.delete("/api/v1/users/me")
    assert response.status_code == status.HTTP_403_FORBIDDEN

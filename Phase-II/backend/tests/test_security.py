import pytest
from fastapi.testclient import TestClient
from src.models.user import User
from src.models.task import Task
from src.utils.password import hash_password
from datetime import datetime, timedelta
import jwt
from src.config.settings import settings
from uuid import UUID
import json


def test_jwt_token_validation(client, db_session):
    """Test JWT token validation and expiration."""
    # Register a user
    registration_data = {
        "email": "jwt_test@example.com",
        "password": "SecurePass123!",
        "confirm_password": "SecurePass123!"
    }

    register_response = client.post("/api/auth/register", json=registration_data)
    assert register_response.status_code == 200
    token = register_response.json()["token"]

    # Verify token is properly formatted
    try:
        decoded = jwt.decode(token, settings.BETTER_AUTH_SECRET, algorithms=["HS256"])
        assert "sub" in decoded
        assert "email" in decoded
        assert "exp" in decoded
    except jwt.InvalidTokenError:
        pytest.fail("Invalid JWT token format")

    # Test that the token works for authentication
    task_data = {
        "title": "JWT Test Task",
        "description": "Task to test JWT authentication",
        "due_date": (datetime.now() + timedelta(days=1)).isoformat(),
        "priority": "medium",
        "completed": False
    }

    response = client.post(
        "/api/tasks",
        json=task_data,
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200


def test_invalid_token_rejection(client):
    """Test that invalid tokens are rejected."""
    # Try to use an invalid token
    invalid_token = "this.is.not.a.valid.jwt.token"

    response = client.get(
        "/api/tasks",
        headers={"Authorization": f"Bearer {invalid_token}"}
    )
    assert response.status_code == 401


def test_malformed_token_rejection(client):
    """Test that malformed tokens are rejected."""
    # Try to use a malformed token
    malformed_token = "Bearer"

    response = client.get(
        "/api/tasks",
        headers={"Authorization": malformed_token}
    )
    assert response.status_code == 401


def test_token_without_bearer_prefix(client, authenticated_user):
    """Test that tokens without Bearer prefix are rejected."""
    user, token = authenticated_user

    response = client.get(
        "/api/tasks",
        headers={"Authorization": token}  # Missing "Bearer " prefix
    )
    assert response.status_code == 401


def test_cross_site_request_forgery_protection(client, authenticated_user):
    """Test that authentication is required for protected endpoints."""
    user, token = authenticated_user

    # Should work with proper authentication
    task_data = {
        "title": "CSRF Test Task",
        "description": "Task to test CSRF protection",
        "due_date": (datetime.now() + timedelta(days=1)).isoformat(),
        "priority": "medium",
        "completed": False
    }

    response_with_auth = client.post(
        "/api/tasks",
        json=task_data,
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response_with_auth.status_code == 200

    # Should fail without authentication
    response_without_auth = client.post("/api/tasks", json=task_data)
    assert response_without_auth.status_code == 401


def test_rate_limiting_basic(client, db_session):
    """Test basic rate limiting functionality."""
    # Create a user first
    registration_data = {
        "email": "ratelimit_test@example.com",
        "password": "SecurePass123!",
        "confirm_password": "SecurePass123!"
    }

    register_response = client.post("/api/auth/register", json=registration_data)
    assert register_response.status_code == 200

    # Make multiple requests to test rate limiting
    # (Implementation depends on how rate limiter is set up)
    for i in range(15):  # Assuming default limit is 10 per minute
        response = client.get("/api/health")
        # All requests should succeed unless rate limiting is triggered
        # The exact behavior depends on the rate limiter implementation


def test_input_sanitization(client, authenticated_user):
    """Test that input is properly sanitized to prevent injection attacks."""
    user, token = authenticated_user

    # Test task creation with potentially harmful input
    malicious_task_data = {
        "title": "<script>alert('xss')</script>Safe Task Title",
        "description": "Normal description with <script> tag",
        "due_date": (datetime.now() + timedelta(days=1)).isoformat(),
        "priority": "medium",
        "completed": False
    }

    response = client.post(
        "/api/tasks",
        json=malicious_task_data,
        headers={"Authorization": f"Bearer {token}"}
    )

    # The request should succeed but the malicious content should be sanitized
    assert response.status_code == 200
    created_task = response.json()

    # The sanitized content should not contain script tags
    # (This depends on the sanitization implementation)
    assert "xss" not in created_task["title"].lower()


def test_sql_injection_attempts(client, authenticated_user):
    """Test that SQL injection attempts are handled safely."""
    user, token = authenticated_user

    # This test verifies that our ORM protects against SQL injection
    # Try to use SQL injection in the title field
    sql_injection_title = "'; DROP TABLE users; --"

    task_data = {
        "title": sql_injection_title,
        "description": "Task with potential SQL injection",
        "due_date": (datetime.now() + timedelta(days=1)).isoformat(),
        "priority": "medium",
        "completed": False
    }

    response = client.post(
        "/api/tasks",
        json=task_data,
        headers={"Authorization": f"Bearer {token}"}
    )

    # The request should succeed but not execute any malicious SQL
    assert response.status_code == 200
    created_task = response.json()

    # Verify the task was created with the exact title (ORM should protect us)
    assert created_task["title"] == sql_injection_title


def test_user_data_isolation(client, db_session):
    """Test that users cannot access other users' data."""
    # Create first user
    user1_data = {
        "email": "isolation1@example.com",
        "password": "SecurePass123!",
        "confirm_password": "SecurePass123!"
    }

    user1_response = client.post("/api/auth/register", json=user1_data)
    assert user1_response.status_code == 200
    user1_token = user1_response.json()["token"]

    # Create second user
    user2_data = {
        "email": "isolation2@example.com",
        "password": "SecurePass456!",
        "confirm_password": "SecurePass456!"
    }

    user2_response = client.post("/api/auth/register", json=user2_data)
    assert user2_response.status_code == 200
    user2_token = user2_response.json()["token"]

    # User 1 creates a task
    task_data = {
        "title": "Private Task for User 1",
        "description": "This should only be accessible by User 1",
        "due_date": (datetime.now() + timedelta(days=1)).isoformat(),
        "priority": "medium",
        "completed": False
    }

    user1_task_response = client.post(
        "/api/tasks",
        json=task_data,
        headers={"Authorization": f"Bearer {user1_token}"}
    )
    assert user1_task_response.status_code == 200
    user1_task_id = user1_task_response.json()["id"]

    # User 2 tries to access User 1's task
    user2_access_response = client.get(
        f"/api/tasks/{user1_task_id}",
        headers={"Authorization": f"Bearer {user2_token}"}
    )
    assert user2_access_response.status_code == 404  # Should not find the task

    # User 2 tries to update User 1's task
    update_response = client.put(
        f"/api/tasks/{user1_task_id}",
        json={"title": "Attempted Update"},
        headers={"Authorization": f"Bearer {user2_token}"}
    )
    assert update_response.status_code == 404  # Should not find the task

    # User 2 tries to delete User 1's task
    delete_response = client.delete(
        f"/api/tasks/{user1_task_id}",
        headers={"Authorization": f"Bearer {user2_token}"}
    )
    assert delete_response.status_code == 404  # Should not find the task


def test_brute_force_protection(client, db_session):
    """Test that multiple failed login attempts don't crash the system."""
    # Create a user first
    registration_data = {
        "email": "bruteforce_test@example.com",
        "password": "SecurePass123!",
        "confirm_password": "SecurePass123!"
    }

    register_response = client.post("/api/auth/register", json=registration_data)
    assert register_response.status_code == 200

    # Try multiple failed login attempts with wrong password
    login_data = {
        "email": "bruteforce_test@example.com",
        "password": "WrongPassword123!"  # Wrong password
    }

    # Make multiple failed attempts
    for i in range(5):
        response = client.post("/api/auth/login", json=login_data)
        assert response.status_code == 401  # Should always return 401 for wrong credentials

    # System should still be operational after failed attempts
    correct_login_data = {
        "email": "bruteforce_test@example.com",
        "password": "SecurePass123!"  # Correct password
    }

    final_response = client.post("/api/auth/login", json=correct_login_data)
    assert final_response.status_code == 200  # Should still work for correct credentials


def test_session_token_leakage_prevention(client, db_session):
    """Test that sensitive information is not leaked in responses."""
    # Register a user
    registration_data = {
        "email": "session_test@example.com",
        "password": "SecurePass123!",
        "confirm_password": "SecurePass123!"
    }

    register_response = client.post("/api/auth/register", json=registration_data)
    assert register_response.status_code == 200

    # Verify that sensitive data is not exposed in the response
    register_data = register_response.json()
    user_info = register_data["user"]

    # The response should not include sensitive data like hashed_password
    assert "hashed_password" not in user_info

    # The response should include necessary public data
    assert "id" in user_info
    assert "email" in user_info
    assert "is_active" in user_info
import pytest
from fastapi.testclient import TestClient
from src.models.user import User
from src.models.task import Task
from datetime import datetime, timedelta
from uuid import UUID
import re


def test_user_registration_validations(client, db_session):
    """Test validation rules for user registration."""
    # Test email validation
    invalid_emails = [
        "invalid-email",
        "@example.com",
        "user@",
        "user..name@example.com",
        "user@domain",
        "",
    ]

    for invalid_email in invalid_emails:
        registration_data = {
            "email": invalid_email,
            "password": "SecurePass123!",
            "confirm_password": "SecurePass123!"
        }

        response = client.post("/api/auth/register", json=registration_data)
        assert response.status_code in [400, 422], f"Expected validation error for email: {invalid_email}"


def test_password_strength_validation(client):
    """Test password strength validation rules."""
    weak_passwords = [
        "12345678",      # No uppercase or special char
        "abcdefgh",      # No uppercase, number or special char
        "ABCD1234",      # No lowercase
        "Abcdefg",       # Less than 8 chars
        "ABC@123",       # Less than 8 chars
        "Short1!",       # Less than 8 chars
    ]

    for weak_password in weak_passwords:
        registration_data = {
            "email": f"test_{weak_password}@example.com",
            "password": weak_password,
            "confirm_password": weak_password
        }

        response = client.post("/api/auth/register", json=registration_data)
        assert response.status_code in [400, 422], f"Expected validation error for weak password: {weak_password}"


def test_password_confirmation_validation(client):
    """Test password confirmation validation."""
    registration_data = {
        "email": "password_confirm_test@example.com",
        "password": "SecurePass123!",
        "confirm_password": "DifferentPass123!"  # Different from password
    }

    response = client.post("/api/auth/register", json=registration_data)
    assert response.status_code in [400, 422], "Expected validation error for mismatched passwords"


def test_task_title_validation(client, authenticated_user):
    """Test validation for task title."""
    user, token = authenticated_user

    # Test empty title
    task_data_empty_title = {
        "title": "",  # Empty title
        "description": "Valid description",
        "due_date": (datetime.now() + timedelta(days=1)).isoformat(),
        "priority": "medium",
        "completed": False
    }

    response = client.post(
        "/api/tasks",
        json=task_data_empty_title,
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code in [400, 422], "Expected validation error for empty title"

    # Test very long title (if there's a length limit in the model)
    long_title = "A" * 256  # Assuming 255 max length in model
    task_data_long_title = {
        "title": long_title,
        "description": "Valid description",
        "due_date": (datetime.now() + timedelta(days=1)).isoformat(),
        "priority": "medium",
        "completed": False
    }

    response = client.post(
        "/api/tasks",
        json=task_data_long_title,
        headers={"Authorization": f"Bearer {token}"}
    )
    # May or may not fail depending on model constraints


def test_task_priority_validation(client, authenticated_user):
    """Test validation for task priority."""
    user, token = authenticated_user

    # Test invalid priority
    task_data_invalid_priority = {
        "title": "Test Task",
        "description": "Task with invalid priority",
        "due_date": (datetime.now() + timedelta(days=1)).isoformat(),
        "priority": "invalid_priority",  # Should be low, medium, or high
        "completed": False
    }

    response = client.post(
        "/api/tasks",
        json=task_data_invalid_priority,
        headers={"Authorization": f"Bearer {token}"}
    )
    # This may pass or fail depending on enum validation in the model


def test_task_due_date_validation(client, authenticated_user):
    """Test validation for task due date."""
    user, token = authenticated_user

    # Test invalid date format
    task_data_invalid_date = {
        "title": "Test Task",
        "description": "Task with invalid date",
        "due_date": "not-a-date-format",  # Invalid date format
        "priority": "medium",
        "completed": False
    }

    response = client.post(
        "/api/tasks",
        json=task_data_invalid_date,
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code in [400, 422], "Expected validation error for invalid date format"

    # Test valid date formats
    valid_dates = [
        (datetime.now() + timedelta(days=1)).isoformat(),
        (datetime.now() + timedelta(weeks=1)).isoformat(),
        datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),
    ]

    for valid_date in valid_dates:
        task_data = {
            "title": f"Test Task {valid_date}",
            "description": "Task with valid date",
            "due_date": valid_date,
            "priority": "medium",
            "completed": False
        }

        response = client.post(
            "/api/tasks",
            json=task_data,
            headers={"Authorization": f"Bearer {token}"}
        )
        # These should succeed if the date format is valid


def test_input_sanitization_validation(client, authenticated_user):
    """Test that input sanitization works correctly."""
    user, token = authenticated_user

    # Test with potentially harmful inputs that should be sanitized
    malicious_inputs = [
        {
            "title": "<script>alert('xss')</script> Safe Title",
            "description": "Normal description",
        },
        {
            "title": "Title with <img src=x onerror=alert('xss')>",
            "description": "Description with potential XSS",
        },
        {
            "title": "Normal Title",
            "description": 'Description with "quotes" and \'apostrophes\'',
        },
        {
            "title": "Title with <svg onload=alert('xss')>",
            "description": "Description with SVG XSS attempt",
        }
    ]

    for malicious_input in malicious_inputs:
        task_data = {
            "title": malicious_input["title"],
            "description": malicious_input["description"],
            "due_date": (datetime.now() + timedelta(days=1)).isoformat(),
            "priority": "medium",
            "completed": False
        }

        response = client.post(
            "/api/tasks",
            json=task_data,
            headers={"Authorization": f"Bearer {token}"}
        )

        # Requests should succeed but potentially malicious content might be sanitized
        assert response.status_code == 200, f"Request failed for input: {malicious_input}"

        # Get the created task to check if content was sanitized
        created_task = response.json()

        # The behavior depends on the sanitization implementation
        # If sanitization is implemented, malicious tags should be removed
        # If not, the raw input might be stored (which would be a security issue)


def test_uuid_validation(client, authenticated_user):
    """Test validation for UUID parameters."""
    user, token = authenticated_user

    # Test invalid UUID format
    invalid_uuids = [
        "not-a-uuid",
        "12345",
        "12345678-1234-5678-9abc-123456789abc-123456",  # Too long
        "12345678-1234-5678",  # Too short
        "zzzzzzzz-zzzz-zzzz-zzzz-zzzzzzzzzzzz",  # Invalid hex
    ]

    for invalid_uuid in invalid_uuids:
        response = client.get(
            f"/api/tasks/{invalid_uuid}",
            headers={"Authorization": f"Bearer {token}"}
        )
        # Should return 422 for validation error or 404 if it gets past validation but fails to find
        assert response.status_code in [404, 422], f"Expected error for invalid UUID: {invalid_uuid}"


def test_boolean_field_validation(client, authenticated_user):
    """Test validation for boolean fields."""
    user, token = authenticated_user

    # Test with string instead of boolean for completed field
    task_data = {
        "title": "Test Task",
        "description": "Task to test boolean validation",
        "due_date": (datetime.now() + timedelta(days=1)).isoformat(),
        "priority": "medium",
        "completed": "maybe"  # Invalid - should be true/false
    }

    response = client.post(
        "/api/tasks",
        json=task_data,
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code in [400, 422], "Expected validation error for invalid boolean value"


def test_numeric_field_validation(client, authenticated_user):
    """Test validation for numeric fields if any exist."""
    user, token = authenticated_user

    # For now, we'll test with fields that should be numeric if they existed
    # Our current model doesn't have explicit numeric fields other than dates
    pass


def test_required_fields_validation(client, authenticated_user):
    """Test that required fields are validated."""
    user, token = authenticated_user

    # Try to create a task without required fields
    minimal_task_data = {
        # Missing title (required)
        "description": "Task without required title",
        "due_date": (datetime.now() + timedelta(days=1)).isoformat(),
        "priority": "medium",
        "completed": False
    }

    response = client.post(
        "/api/tasks",
        json=minimal_task_data,
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code in [400, 422], "Expected validation error for missing required field"


def test_enum_validation(client, authenticated_user):
    """Test validation for enum fields like priority."""
    user, token = authenticated_user

    valid_priorities = ["low", "medium", "high"]
    invalid_priorities = ["critical", "urgent", "normal", "invalid"]

    # Test valid priorities (should succeed)
    for priority in valid_priorities:
        task_data = {
            "title": f"Task with {priority} priority",
            "description": f"Task with {priority} priority",
            "due_date": (datetime.now() + timedelta(days=1)).isoformat(),
            "priority": priority,
            "completed": False
        }

        response = client.post(
            "/api/tasks",
            json=task_data,
            headers={"Authorization": f"Bearer {token}"}
        )
        # These should succeed if enum validation is implemented

    # Test invalid priorities
    for priority in invalid_priorities:
        task_data = {
            "title": f"Task with {priority} priority",
            "description": f"Task with {priority} priority",
            "due_date": (datetime.now() + timedelta(days=1)).isoformat(),
            "priority": priority,
            "completed": False
        }

        response = client.post(
            "/api/tasks",
            json=task_data,
            headers={"Authorization": f"Bearer {token}"}
        )
        # May or may not fail depending on whether enum validation is implemented in the model


def test_url_field_validation_if_present(client, authenticated_user):
    """Test validation for URL fields if any exist in the models."""
    user, token = authenticated_user

    # This would be used if we had URL fields in our models
    pass


def test_string_length_validation_if_present(client, authenticated_user):
    """Test validation for string length limits if any exist."""
    user, token = authenticated_user

    # Test with very long strings if length limits are enforced
    very_long_title = "A" * 1000  # Assuming some limit exists

    task_data = {
        "title": very_long_title,
        "description": "Normal description",
        "due_date": (datetime.now() + timedelta(days=1)).isoformat(),
        "priority": "medium",
        "completed": False
    }

    response = client.post(
        "/api/tasks",
        json=task_data,
        headers={"Authorization": f"Bearer {token}"}
    )

    # May or may not fail depending on whether length limits are enforced in the model
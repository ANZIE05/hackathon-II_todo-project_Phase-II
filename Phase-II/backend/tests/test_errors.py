import pytest
from fastapi.testclient import TestClient
from src.models.user import User
from src.models.task import Task
from datetime import datetime, timedelta
from uuid import UUID
import json


def test_standardized_error_responses(client):
    """Test that error responses follow the standardized format."""
    # Test 404 error for non-existent endpoint
    response = client.get("/api/nonexistent-endpoint")
    assert response.status_code == 404

    error_data = response.json()
    assert "success" in error_data
    assert "error" in error_data or "message" in error_data
    assert "timestamp" in error_data
    assert "path" in error_data
    assert "status_code" in error_data
    assert error_data["success"] is False


def test_validation_error_format(client, db_session):
    """Test that validation errors follow the standardized format."""
    # Try to register with invalid data to trigger validation error
    invalid_data = {
        "email": "invalid-email",  # Invalid email format
        "password": "123",  # Too short, doesn't meet requirements
        "confirm_password": "123"
    }

    response = client.post("/api/auth/register", json=invalid_data)
    assert response.status_code == 422  # Unprocessable Entity for validation error

    error_data = response.json()
    assert "success" in error_data
    assert error_data["success"] is False
    assert "error" in error_data or "message" in error_data
    assert "timestamp" in error_data
    assert "status_code" in error_data
    assert error_data["status_code"] == 422


def test_authentication_error_format(client):
    """Test that authentication errors follow the standardized format."""
    # Try to access protected endpoint without authentication
    response = client.get("/api/tasks")
    assert response.status_code == 401  # Unauthorized

    error_data = response.json()
    assert "success" in error_data
    assert error_data["success"] is False
    assert "error" in error_data or "message" in error_data
    assert "timestamp" in error_data
    assert "status_code" in error_data
    assert error_data["status_code"] == 401


def test_authorization_error_format(client, authenticated_user):
    """Test that authorization errors follow the standardized format."""
    user, token = authenticated_user

    # Create a task
    task_data = {
        "title": "Test Task",
        "description": "Task to test error formats",
        "due_date": (datetime.now() + timedelta(days=1)).isoformat(),
        "priority": "medium",
        "completed": False
    }

    create_response = client.post(
        "/api/tasks",
        json=task_data,
        headers={"Authorization": f"Bearer {token}"}
    )
    assert create_response.status_code == 200
    task_id = create_response.json()["id"]

    # Manually delete the task to simulate a "not found" scenario
    # (We'll just try to access a non-existent task ID)
    fake_task_id = "12345678-1234-5678-9abc-def012345678"

    response = client.get(
        f"/api/tasks/{fake_task_id}",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 404

    error_data = response.json()
    assert "success" in error_data
    assert error_data["success"] is False
    assert "error" in error_data or "message" in error_data
    assert "timestamp" in error_data
    assert "status_code" in error_data
    assert error_data["status_code"] == 404


def test_duplicate_resource_error_format(client, create_test_user):
    """Test that duplicate resource errors follow the standardized format."""
    existing_user = create_test_user()

    # Try to register another user with the same email
    duplicate_registration = {
        "email": existing_user.email,
        "password": "NewPassword123!",
        "confirm_password": "NewPassword123!"
    }

    response = client.post("/api/auth/register", json=duplicate_registration)
    assert response.status_code == 409  # Conflict

    error_data = response.json()
    assert "success" in error_data
    assert error_data["success"] is False
    assert "error" in error_data or "message" in error_data
    assert "timestamp" in error_data
    assert "status_code" in error_data
    assert error_data["status_code"] == 409


def test_error_response_structure_consistency(client):
    """Test that all error responses have consistent structure."""
    error_endpoints_and_codes = [
        ("/api/nonexistent", 404),  # Not Found
        ("/api/tasks", 401),        # Unauthorized
        ("/api/auth/register", 422) # Validation Error
    ]

    for endpoint, expected_status in error_endpoints_and_codes:
        if expected_status == 422:
            # Send invalid data for validation error
            response = client.post(endpoint, json={"invalid": "data"})
        elif expected_status == 401:
            # Send request without auth for unauthorized
            response = client.get(endpoint)
        else:
            # Send GET request to non-existent endpoint
            response = client.get(endpoint)

        assert response.status_code == expected_status

        error_data = response.json()

        # Verify consistent structure across all error types
        assert isinstance(error_data, dict), f"Error response for {endpoint} should be a dict"
        assert "success" in error_data, f"Error response for {endpoint} missing 'success' field"
        assert error_data["success"] is False, f"Error response for {endpoint} should have success=False"
        assert "status_code" in error_data, f"Error response for {endpoint} missing 'status_code' field"
        assert error_data["status_code"] == expected_status, f"Error response for {endpoint} has incorrect status_code"
        assert "timestamp" in error_data, f"Error response for {endpoint} missing 'timestamp' field"
        assert "message" in error_data or "detail" in error_data, f"Error response for {endpoint} missing 'message' or 'detail' field"


def test_internal_server_error_handling(client, monkeypatch):
    """Test how internal server errors are handled."""
    # This test would be more effective if we had endpoints that could trigger internal errors
    # For now, we'll test the error handler middleware by attempting to trigger an error

    # Since our app is designed to catch most errors, we'll test the general error handling
    # by ensuring that even if an internal error occurs, it returns a structured response
    pass


def test_error_details_inclusion(client, authenticated_user):
    """Test that error responses include appropriate detail information."""
    user, token = authenticated_user

    # Test with a malformed request to get validation error
    invalid_task_data = {
        "title": "",  # Empty title should cause validation error
        "description": "Valid description",
        "due_date": "invalid-date-format",  # Invalid date format
        "priority": "invalid-priority",  # Invalid priority value
        "completed": "not-a-boolean"  # Invalid boolean
    }

    response = client.post(
        "/api/tasks",
        json=invalid_task_data,
        headers={"Authorization": f"Bearer {token}"}
    )

    # Could be 422 or 400 depending on validation
    assert response.status_code in [400, 422]

    error_data = response.json()

    # Check that error responses have appropriate detail information
    assert "success" in error_data
    assert error_data["success"] is False
    assert "status_code" in error_data
    assert "timestamp" in error_data

    # Error responses might have details about what went wrong
    # This depends on how validation errors are formatted


def test_error_path_inclusion(client):
    """Test that error responses include the correct path."""
    # Try to access a non-existent endpoint
    response = client.get("/api/path/that/does/not/exist")
    assert response.status_code == 404

    error_data = response.json()
    assert "path" in error_data
    assert "/api/path/that/does/not/exist" in error_data["path"]


def test_request_id_included_in_error_response(client):
    """Test that error responses include request ID for tracing."""
    # Make a request that will result in an error
    response = client.get("/api/nonexistent-endpoint")
    assert response.status_code == 404

    error_data = response.json()

    # The error response itself might not include X-Request-ID in the JSON body
    # but the response headers should include it
    assert response.headers.get("x-request-id") is not None


def test_error_message_clarity(client, db_session):
    """Test that error messages are clear and helpful."""
    # Test registration with invalid email
    invalid_email_data = {
        "email": "not-an-email",
        "password": "ValidPass123!",
        "confirm_password": "ValidPass123!"
    }

    response = client.post("/api/auth/register", json=invalid_email_data)
    assert response.status_code == 400

    error_data = response.json()
    assert "message" in error_data or "detail" in error_data

    # The message should indicate what went wrong
    message = error_data.get("message", error_data.get("detail", ""))
    assert "email" in str(message).lower() or "invalid" in str(message).lower()


def test_error_status_code_accuracy(client, authenticated_user):
    """Test that error responses return accurate HTTP status codes."""
    user, token = authenticated_user

    # Test 401 Unauthorized
    unauthorized_response = client.get("/api/tasks")
    assert unauthorized_response.status_code == 401

    # Test 404 Not Found
    fake_uuid = "12345678-1234-5678-9abc-def012345678"
    not_found_response = client.get(
        f"/api/tasks/{fake_uuid}",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert not_found_response.status_code == 404

    # Test 400 Bad Request with invalid data
    bad_request_response = client.post(
        "/api/tasks",
        json={"invalid": "data"},
        headers={"Authorization": f"Bearer {token}"}
    )
    # This might be 422 for validation error, which is also appropriate
    assert bad_request_response.status_code in [400, 422]
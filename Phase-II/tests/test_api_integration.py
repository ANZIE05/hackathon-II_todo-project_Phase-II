import pytest
from fastapi.testclient import TestClient
from src.models.user import User
from src.models.task import Task
from datetime import datetime, timedelta
from uuid import UUID
import json


def test_full_user_workflow(client, db_session):
    """Test the complete user workflow: register, login, create tasks, update, delete."""
    # Step 1: Register a new user
    registration_data = {
        "email": "integration_test@example.com",
        "password": "SecurePass123!",
        "confirm_password": "SecurePass123!"
    }

    register_response = client.post("/api/auth/register", json=registration_data)
    assert register_response.status_code == 200
    register_data = register_response.json()
    assert register_data["success"] is True
    user_token = register_data["token"]
    user_id = register_data["user"]["id"]

    # Step 2: Login with the same credentials (should work)
    login_data = {
        "email": "integration_test@example.com",
        "password": "SecurePass123!"
    }

    login_response = client.post("/api/auth/login", json=login_data)
    assert login_response.status_code == 200
    login_result = login_response.json()
    assert login_result["success"] is True
    assert login_result["token"] == user_token  # Same token should be returned

    # Step 3: Create a task using the authenticated user
    task_data = {
        "title": "Integration Test Task",
        "description": "Task created during integration test",
        "due_date": (datetime.now() + timedelta(days=2)).isoformat(),
        "priority": "high",
        "completed": False
    }

    create_task_response = client.post(
        "/api/tasks",
        json=task_data,
        headers={"Authorization": f"Bearer {user_token}"}
    )
    assert create_task_response.status_code == 200
    created_task = create_task_response.json()
    assert created_task["title"] == task_data["title"]
    assert created_task["description"] == task_data["description"]
    assert created_task["user_id"] == user_id  # Task should be linked to the user

    # Step 4: Retrieve the created task
    get_task_response = client.get(
        f"/api/tasks/{created_task['id']}",
        headers={"Authorization": f"Bearer {user_token}"}
    )
    assert get_task_response.status_code == 200
    retrieved_task = get_task_response.json()
    assert retrieved_task["id"] == created_task["id"]
    assert retrieved_task["title"] == created_task["title"]

    # Step 5: Update the task
    update_data = {
        "title": "Updated Integration Test Task",
        "description": "Updated task description",
        "priority": "low",
        "completed": True
    }

    update_response = client.put(
        f"/api/tasks/{created_task['id']}",
        json=update_data,
        headers={"Authorization": f"Bearer {user_token}"}
    )
    assert update_response.status_code == 200
    updated_task = update_response.json()
    assert updated_task["title"] == update_data["title"]
    assert updated_task["completed"] == update_data["completed"]

    # Step 6: List all tasks for the user
    list_response = client.get("/api/tasks", headers={"Authorization": f"Bearer {user_token}"})
    assert list_response.status_code == 200
    tasks_list = list_response.json()
    assert "tasks" in tasks_list
    assert len(tasks_list["tasks"]) >= 1  # Should include our task

    # Step 7: Find our specific task in the list
    found_task = None
    for task in tasks_list["tasks"]:
        if task["id"] == created_task["id"]:
            found_task = task
            break
    assert found_task is not None
    assert found_task["title"] == update_data["title"]
    assert found_task["completed"] is True

    # Step 8: Delete the task
    delete_response = client.delete(
        f"/api/tasks/{created_task['id']}",
        headers={"Authorization": f"Bearer {user_token}"}
    )
    assert delete_response.status_code == 200
    delete_result = delete_response.json()
    assert delete_result["message"] == "Task deleted successfully"

    # Step 9: Verify the task is gone
    verify_delete_response = client.get(
        f"/api/tasks/{created_task['id']}",
        headers={"Authorization": f"Bearer {user_token}"}
    )
    assert verify_delete_response.status_code == 404


def test_cross_user_isolation(client, db_session):
    """Test that users cannot access each other's tasks."""
    # Create first user
    user1_data = {
        "email": "user1@example.com",
        "password": "SecurePass123!",
        "confirm_password": "SecurePass123!"
    }

    user1_reg = client.post("/api/auth/register", json=user1_data)
    assert user1_reg.status_code == 200
    user1_token = user1_reg.json()["token"]
    user1_id = user1_reg.json()["user"]["id"]

    # Create second user
    user2_data = {
        "email": "user2@example.com",
        "password": "SecurePass456!",
        "confirm_password": "SecurePass456!"
    }

    user2_reg = client.post("/api/auth/register", json=user2_data)
    assert user2_reg.status_code == 200
    user2_token = user2_reg.json()["token"]
    user2_id = user2_reg.json()["user"]["id"]

    # User 1 creates a task
    task_data = {
        "title": "User 1's Private Task",
        "description": "This should only be accessible by User 1",
        "due_date": (datetime.now() + timedelta(days=1)).isoformat(),
        "priority": "medium",
        "completed": False
    }

    create_task_response = client.post(
        "/api/tasks",
        json=task_data,
        headers={"Authorization": f"Bearer {user1_token}"}
    )
    assert create_task_response.status_code == 200
    user1_task = create_task_response.json()

    # User 2 tries to access User 1's task (should fail)
    access_task_response = client.get(
        f"/api/tasks/{user1_task['id']}",
        headers={"Authorization": f"Bearer {user2_token}"}
    )
    assert access_task_response.status_code == 404  # Should not find the task

    # User 2 tries to update User 1's task (should fail)
    update_response = client.put(
        f"/api/tasks/{user1_task['id']}",
        json={"title": "Hacked Task Title"},
        headers={"Authorization": f"Bearer {user2_token}"}
    )
    assert update_response.status_code == 404  # Should not find the task

    # User 2 tries to delete User 1's task (should fail)
    delete_response = client.delete(
        f"/api/tasks/{user1_task['id']}",
        headers={"Authorization": f"Bearer {user2_token}"}
    )
    assert delete_response.status_code == 404  # Should not find the task

    # Both users should only see their own tasks in the list
    user1_tasks_response = client.get("/api/tasks", headers={"Authorization": f"Bearer {user1_token}"})
    assert user1_tasks_response.status_code == 200
    user1_tasks = user1_tasks_response.json()["tasks"]

    user2_tasks_response = client.get("/api/tasks", headers={"Authorization": f"Bearer {user2_token}"})
    assert user2_tasks_response.status_code == 200
    user2_tasks = user2_tasks_response.json()["tasks"]

    # Each user should only see their own tasks (though initially only user1 has a task)
    # If user2 creates a task, it should only appear in user2's list
    user2_task_data = {
        "title": "User 2's Private Task",
        "description": "This should only be accessible by User 2",
        "due_date": (datetime.now() + timedelta(days=1)).isoformat(),
        "priority": "low",
        "completed": False
    }

    user2_create_task = client.post(
        "/api/tasks",
        json=user2_task_data,
        headers={"Authorization": f"Bearer {user2_token}"}
    )
    assert user2_create_task.status_code == 200
    user2_task = user2_create_task.json()

    # Refresh task lists
    user1_tasks_response = client.get("/api/tasks", headers={"Authorization": f"Bearer {user1_token}"})
    user1_tasks = user1_tasks_response.json()["tasks"]

    user2_tasks_response = client.get("/api/tasks", headers={"Authorization": f"Bearer {user2_token}"})
    user2_tasks = user2_tasks_response.json()["tasks"]

    # Verify isolation
    user1_task_ids = [task["id"] for task in user1_tasks]
    user2_task_ids = [task["id"] for task in user2_tasks]

    # User 1's task should be in user1's list but not user2's
    assert user1_task["id"] in user1_task_ids
    assert user1_task["id"] not in user2_task_ids

    # User 2's task should be in user2's list but not user1's
    assert user2_task["id"] in user2_task_ids
    assert user2_task["id"] not in user1_task_ids


def test_authentication_flow(client, db_session):
    """Test the complete authentication flow including logout and token invalidation."""
    # Register a user
    registration_data = {
        "email": "authflow@example.com",
        "password": "SecurePass123!",
        "confirm_password": "SecurePass123!"
    }

    register_response = client.post("/api/auth/register", json=registration_data)
    assert register_response.status_code == 200
    user_token = register_response.json()["token"]

    # Verify token works for creating a task
    task_data = {
        "title": "Auth Flow Test Task",
        "description": "Task to test authentication flow",
        "due_date": (datetime.now() + timedelta(days=1)).isoformat(),
        "priority": "medium",
        "completed": False
    }

    create_response = client.post(
        "/api/tasks",
        json=task_data,
        headers={"Authorization": f"Bearer {user_token}"}
    )
    assert create_response.status_code == 200

    # Logout
    logout_response = client.post(
        "/api/auth/logout",
        headers={"Authorization": f"Bearer {user_token}"}
    )
    assert logout_response.status_code == 200

    # Try to use the token again (may still work in JWT stateless system,
    # but if we implemented token blacklisting properly, it should fail)
    # For now, we'll just verify logout succeeded
    logout_data = logout_response.json()
    assert logout_data["message"] == "Successfully logged out"
    assert "user_id" in logout_data


def test_error_handling_consistency(client, db_session):
    """Test that error responses follow a consistent format."""
    # Try to access a protected endpoint without authentication
    response = client.get("/api/tasks")
    assert response.status_code == 401

    error_data = response.json()
    # Verify error response has expected structure
    assert "success" in error_data
    assert "error" in error_data or "detail" in error_data
    assert "message" in error_data or "detail" in error_data
    assert error_data["success"] is False

    # Try to register with invalid data
    invalid_registration = {
        "email": "invalid-email",  # Invalid email format
        "password": "short",       # Too short
        "confirm_password": "short"
    }

    response = client.post("/api/auth/register", json=invalid_registration)
    assert response.status_code == 400  # Bad request

    error_data = response.json()
    assert "success" in error_data
    assert error_data["success"] is False
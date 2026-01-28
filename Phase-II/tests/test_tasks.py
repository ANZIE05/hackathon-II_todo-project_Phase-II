import pytest
from fastapi.testclient import TestClient
from src.models.task import Task
from src.models.user import User
from datetime import datetime, timedelta
from uuid import UUID
import json


def test_create_task_success(client, authenticated_user):
    """Test successful task creation."""
    user, token = authenticated_user

    task_data = {
        "title": "Test Task",
        "description": "This is a test task",
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
    response_data = response.json()
    assert response_data["title"] == task_data["title"]
    assert response_data["description"] == task_data["description"]
    assert response_data["priority"] == task_data["priority"]
    assert response_data["completed"] == task_data["completed"]
    assert "id" in response_data


def test_create_task_unauthorized(client):
    """Test task creation without authentication."""
    task_data = {
        "title": "Test Task",
        "description": "This is a test task",
        "due_date": (datetime.now() + timedelta(days=1)).isoformat(),
        "priority": "medium",
        "completed": False
    }

    response = client.post("/api/tasks", json=task_data)

    assert response.status_code == 401  # Unauthorized


def test_list_tasks_success(client, authenticated_user, create_test_task):
    """Test successful task listing."""
    user, token = authenticated_user

    # Create a few tasks for the user
    task1 = create_test_task(user_id=user.id, title="Task 1")
    task2 = create_test_task(user_id=user.id, title="Task 2")

    response = client.get("/api/tasks", headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == 200
    response_data = response.json()
    assert "tasks" in response_data
    assert len(response_data["tasks"]) >= 2  # At least the 2 we created

    # Check that the tasks belong to the correct user
    task_ids = [task["id"] for task in response_data["tasks"]]
    assert str(task1.id) in task_ids
    assert str(task2.id) in task_ids


def test_list_tasks_unauthorized(client):
    """Test task listing without authentication."""
    response = client.get("/api/tasks")

    assert response.status_code == 401  # Unauthorized


def test_get_task_success(client, authenticated_user, create_test_task):
    """Test successful task retrieval."""
    user, token = authenticated_user
    task = create_test_task(user_id=user.id)

    response = client.get(f"/api/tasks/{task.id}", headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == 200
    response_data = response.json()
    assert response_data["id"] == str(task.id)
    assert response_data["title"] == task.title


def test_get_task_unauthorized(client, create_test_task):
    """Test task retrieval without authentication."""
    user, token = authenticated_user
    task = create_test_task(user_id=user.id)

    response = client.get(f"/api/tasks/{task.id}")

    assert response.status_code == 401  # Unauthorized


def test_get_task_not_found(client, authenticated_user):
    """Test retrieving a non-existent task."""
    user, token = authenticated_user

    fake_task_id = "12345678-1234-5678-9abc-def012345678"

    response = client.get(f"/api/tasks/{fake_task_id}", headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == 404  # Not found


def test_get_task_different_user(client, db_session, authenticated_user, create_test_task):
    """Test retrieving a task that belongs to a different user."""
    user1, token1 = authenticated_user

    # Create another user and task
    from src.models.user import User
    from src.utils.password import hash_password
    user2_data = {
        "email": "another@example.com",
        "hashed_password": hash_password("AnotherPass123!"),
        "is_active": True
    }
    user2 = User(**user2_data)
    db_session.add(user2)
    db_session.commit()
    db_session.refresh(user2)

    # Create a task for user2
    task_for_user2 = create_test_task(user_id=user2.id, title="Task for User 2")

    # Try to access user2's task with user1's token
    response = client.get(
        f"/api/tasks/{task_for_user2.id}",
        headers={"Authorization": f"Bearer {token1}"}
    )

    assert response.status_code == 404  # Not found (actually 403 in some implementations)


def test_update_task_success(client, authenticated_user, create_test_task):
    """Test successful task update."""
    user, token = authenticated_user
    task = create_test_task(user_id=user.id)

    update_data = {
        "title": "Updated Task Title",
        "description": "Updated description",
        "priority": "high",
        "completed": True
    }

    response = client.put(
        f"/api/tasks/{task.id}",
        json=update_data,
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 200
    response_data = response.json()
    assert response_data["title"] == update_data["title"]
    assert response_data["description"] == update_data["description"]
    assert response_data["priority"] == update_data["priority"]
    assert response_data["completed"] == update_data["completed"]


def test_update_task_unauthorized(client, create_test_task):
    """Test task update without authentication."""
    user, token = authenticated_user
    task = create_test_task(user_id=user.id)

    update_data = {
        "title": "Updated Task Title",
        "description": "Updated description"
    }

    response = client.put(f"/api/tasks/{task.id}", json=update_data)

    assert response.status_code == 401  # Unauthorized


def test_update_task_not_found(client, authenticated_user):
    """Test updating a non-existent task."""
    user, token = authenticated_user

    fake_task_id = "12345678-1234-5678-9abc-def012345678"

    update_data = {
        "title": "Updated Task Title",
        "description": "Updated description"
    }

    response = client.put(
        f"/api/tasks/{fake_task_id}",
        json=update_data,
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 404  # Not found


def test_complete_task_success(client, authenticated_user, create_test_task):
    """Test successfully marking a task as complete."""
    user, token = authenticated_user
    task = create_test_task(user_id=user.id, completed=False)

    patch_data = {"completed": True}

    response = client.patch(
        f"/api/tasks/{task.id}/complete",
        json=patch_data,
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 200
    response_data = response.json()
    assert response_data["completed"] is True


def test_delete_task_success(client, authenticated_user, create_test_task):
    """Test successful task deletion."""
    user, token = authenticated_user
    task = create_test_task(user_id=user.id)

    response = client.delete(
        f"/api/tasks/{task.id}",
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 200
    response_data = response.json()
    assert response_data["message"] == "Task deleted successfully"


def test_delete_task_unauthorized(client, create_test_task):
    """Test task deletion without authentication."""
    user, token = authenticated_user
    task = create_test_task(user_id=user.id)

    response = client.delete(f"/api/tasks/{task.id}")

    assert response.status_code == 401  # Unauthorized


def test_delete_task_not_found(client, authenticated_user):
    """Test deleting a non-existent task."""
    user, token = authenticated_user

    fake_task_id = "12345678-1234-5678-9abc-def012345678"

    response = client.delete(
        f"/api/tasks/{fake_task_id}",
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 404  # Not found
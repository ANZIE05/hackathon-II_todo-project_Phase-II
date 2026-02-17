import pytest
import time
from fastapi.testclient import TestClient
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading
from src.models.user import User
from src.models.task import Task
from datetime import datetime, timedelta
import statistics


def test_health_endpoint_performance(client):
    """Test the performance of the health endpoint."""
    start_time = time.time()

    # Make multiple requests to the health endpoint
    for _ in range(100):
        response = client.get("/api/health")
        assert response.status_code == 200

    end_time = time.time()
    total_time = end_time - start_time
    avg_time = total_time / 100

    # Assert that average response time is under 100ms
    assert avg_time < 0.1, f"Average response time {avg_time:.3f}s exceeds 100ms threshold"


def test_concurrent_auth_requests(client, db_session):
    """Test performance under concurrent authentication requests."""
    def register_and_login():
        # Register a user
        email = f"perf_test_{threading.current_thread().ident}@example.com"
        reg_data = {
            "email": email,
            "password": "SecurePass123!",
            "confirm_password": "SecurePass123!"
        }

        reg_response = client.post("/api/auth/register", json=reg_data)
        assert reg_response.status_code == 200

        # Login the user
        login_data = {
            "email": email,
            "password": "SecurePass123!"
        }

        login_response = client.post("/api/auth/login", json=login_data)
        assert login_response.status_code == 200

        return login_response.json()["token"]

    # Run multiple registrations and logins concurrently
    start_time = time.time()
    thread_count = 10

    with ThreadPoolExecutor(max_workers=thread_count) as executor:
        futures = [executor.submit(register_and_login) for _ in range(thread_count)]

        # Wait for all to complete
        results = []
        for future in as_completed(futures):
            try:
                token = future.result(timeout=10)  # 10 second timeout per thread
                results.append(token)
            except Exception as e:
                pytest.fail(f"Thread failed with error: {e}")

    end_time = time.time()
    total_time = end_time - start_time

    # Assert that all concurrent operations completed within reasonable time
    assert len(results) == thread_count, "All threads should have completed successfully"
    assert total_time < 10.0, f"All concurrent operations took {total_time:.2f}s, expected under 10s"


def test_task_crud_performance(client, authenticated_user):
    """Test performance of task CRUD operations."""
    user, token = authenticated_user

    # Measure creation performance
    start_time = time.time()

    task_ids = []
    for i in range(50):
        task_data = {
            "title": f"Performance Test Task {i}",
            "description": f"Task {i} for performance testing",
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
        task_ids.append(response.json()["id"])

    creation_time = time.time() - start_time

    # Measure retrieval performance
    start_time = time.time()
    for task_id in task_ids[:10]:  # Test with first 10 tasks
        response = client.get(
            f"/api/tasks/{task_id}",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 200

    retrieval_time = time.time() - start_time

    # Measure list performance
    start_time = time.time()
    response = client.get(
        "/api/tasks",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    list_response = response.json()

    list_time = time.time() - start_time

    # Verify we got all tasks back
    assert len(list_response["tasks"]) >= 50

    # Assertions for performance thresholds
    avg_creation_time = creation_time / 50
    avg_retrieval_time = retrieval_time / 10

    assert avg_creation_time < 0.5, f"Average task creation time {avg_creation_time:.3f}s exceeds 500ms"
    assert avg_retrieval_time < 0.2, f"Average task retrieval time {avg_retrieval_time:.3f}s exceeds 200ms"
    assert list_time < 1.0, f"Task list operation took {list_time:.3f}s, exceeds 1s threshold"


def test_multiple_users_concurrent_tasks(client, db_session):
    """Test performance with multiple users creating tasks concurrently."""
    # First, create multiple users
    users_and_tokens = []
    for i in range(5):
        reg_data = {
            "email": f"multi_user_{i}@example.com",
            "password": "SecurePass123!",
            "confirm_password": "SecurePass123!"
        }

        reg_response = client.post("/api/auth/register", json=reg_data)
        assert reg_response.status_code == 200
        token = reg_response.json()["token"]

        users_and_tokens.append((f"multi_user_{i}@example.com", token))

    def create_tasks_for_user(user_idx):
        """Function to create tasks for a specific user."""
        _, token = users_and_tokens[user_idx]
        results = []

        for j in range(10):
            task_data = {
                "title": f"Multi-user Task {user_idx}-{j}",
                "description": f"Task {j} for user {user_idx}",
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
            results.append(response.json()["id"])

        return results

    # Run task creation concurrently for all users
    start_time = time.time()

    with ThreadPoolExecutor(max_workers=5) as executor:
        futures = [executor.submit(create_tasks_for_user, i) for i in range(5)]

        all_created_tasks = []
        for future in as_completed(futures):
            try:
                task_ids = future.result(timeout=30)  # 30 second timeout
                all_created_tasks.extend(task_ids)
            except Exception as e:
                pytest.fail(f"Concurrent task creation failed: {e}")

    end_time = time.time()
    total_time = end_time - start_time

    # Verify all tasks were created
    assert len(all_created_tasks) == 50  # 5 users * 10 tasks each

    # Check total time threshold
    assert total_time < 15.0, f"Creating 50 tasks across 5 users took {total_time:.2f}s, expected under 15s"


def test_single_request_timing(client, authenticated_user):
    """Test the timing of individual requests to establish baseline."""
    user, token = authenticated_user

    # Measure various operations
    timings = {}

    # Health check
    start = time.time()
    response = client.get("/api/health")
    timings['health'] = time.time() - start
    assert response.status_code == 200

    # Create a task
    task_data = {
        "title": "Timing Test Task",
        "description": "Task for timing test",
        "due_date": (datetime.now() + timedelta(days=1)).isoformat(),
        "priority": "medium",
        "completed": False
    }

    start = time.time()
    response = client.post(
        "/api/tasks",
        json=task_data,
        headers={"Authorization": f"Bearer {token}"}
    )
    timings['create_task'] = time.time() - start
    assert response.status_code == 200
    task_id = response.json()["id"]

    # Get the task
    start = time.time()
    response = client.get(
        f"/api/tasks/{task_id}",
        headers={"Authorization": f"Bearer {token}"}
    )
    timings['get_task'] = time.time() - start
    assert response.status_code == 200

    # Update the task
    update_data = {
        "title": "Updated Timing Test Task",
        "completed": True
    }

    start = time.time()
    response = client.put(
        f"/api/tasks/{task_id}",
        json=update_data,
        headers={"Authorization": f"Bearer {token}"}
    )
    timings['update_task'] = time.time() - start
    assert response.status_code == 200

    # Print timing results for analysis
    print("\nIndividual Request Timings:")
    for operation, timing in timings.items():
        print(f"  {operation}: {timing:.3f}s")

    # Assert reasonable performance for individual operations
    assert timings['health'] < 0.05, f"Health check too slow: {timings['health']:.3f}s"
    assert timings['create_task'] < 0.5, f"Task creation too slow: {timings['create_task']:.3f}s"
    assert timings['get_task'] < 0.2, f"Task retrieval too slow: {timings['get_task']:.3f}s"
    assert timings['update_task'] < 0.5, f"Task update too slow: {timings['update_task']:.3f}s"
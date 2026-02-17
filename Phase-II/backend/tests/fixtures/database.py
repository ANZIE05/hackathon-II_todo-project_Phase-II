import pytest
from datetime import datetime, timedelta
from src.models.user import User
from src.models.task import Task
from src.services.user_service import UserService
from src.services.task_service import TaskService
from src.utils.password import hash_password
from uuid import UUID, uuid4
from sqlmodel import Session


@pytest.fixture
def sample_user_data():
    """Sample user data for testing."""
    return {
        "email": "test@example.com",
        "password": "TestPass123!",
        "hashed_password": hash_password("TestPass123!")
    }


@pytest.fixture
def create_test_user(db_session, sample_user_data):
    """Create a test user in the database."""
    def _create_test_user(email=None, password=None):
        user_data = {
            "email": email or sample_user_data["email"],
            "hashed_password": hash_password(password or sample_user_data["password"]),
            "is_active": True
        }

        user = User(**user_data)
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)

        return user

    return _create_test_user


@pytest.fixture
def sample_task_data():
    """Sample task data for testing."""
    return {
        "title": "Test Task",
        "description": "This is a test task",
        "due_date": datetime.now() + timedelta(days=1),
        "priority": "medium",
        "completed": False
    }


@pytest.fixture
def create_test_task(db_session):
    """Create a test task in the database."""
    def _create_test_task(user_id, title=None, description=None, due_date=None, priority=None, completed=None):
        task_data = {
            "title": title or "Test Task",
            "description": description or "This is a test task",
            "due_date": due_date or (datetime.now() + timedelta(days=1)),
            "priority": priority or "medium",
            "completed": completed or False,
            "user_id": user_id
        }

        task = Task(**task_data)
        db_session.add(task)
        db_session.commit()
        db_session.refresh(task)

        return task

    return _create_test_task


@pytest.fixture
def authenticated_user(client, create_test_user):
    """Create an authenticated user and return their token."""
    user = create_test_user()

    # Register and login to get token
    response = client.post("/api/auth/login", json={
        "email": user.email,
        "password": "TestPass123!"
    })

    assert response.status_code == 200
    token = response.json()["token"]

    return user, token
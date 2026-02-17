import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlmodel import SQLModel
from alembic.config import Config
from alembic import command
from alembic.script import ScriptDirectory
from alembic.runtime.migration import MigrationContext
from contextlib import ExitStack
import tempfile
import os
from pathlib import Path

from main import app
from src.database.connection import engine, get_session
from src.config.settings import settings


@pytest.fixture(scope="session")
def db_engine():
    """Create a test database engine."""
    # Use an in-memory SQLite database for testing
    test_db_url = "sqlite:///./test_todo_app.db"  # Changed from in-memory to file for transaction support

    engine = create_engine(test_db_url, connect_args={"check_same_thread": False})

    # Create all tables
    SQLModel.metadata.create_all(bind=engine)

    yield engine

    # Cleanup
    engine.dispose()


@pytest.fixture(scope="function")
def db_session(db_engine):
    """Create a test database session with rollback capability."""
    connection = db_engine.connect()
    transaction = connection.begin()

    # Bind the session to the connection
    session = sessionmaker(bind=connection, autocommit=False, autoflush=False)()

    # Override the get_session dependency
    def override_get_session():
        return session

    app.dependency_overrides[get_session] = override_get_session

    yield session

    # Rollback the transaction after the test
    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture(scope="function")
def client(db_session):
    """Create a test client with database session."""
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture(scope="session")
def test_settings():
    """Override settings for testing."""
    # Create temporary database file
    temp_db = tempfile.NamedTemporaryFile(delete=False, suffix=".db")
    temp_db.close()

    # Override database URL
    original_db_url = settings.NEON_DB_URL
    settings.NEON_DB_URL = f"sqlite:///{temp_db.name}"

    yield settings

    # Cleanup
    os.unlink(temp_db.name)
    settings.NEON_DB_URL = original_db_url


def pytest_configure(config):
    """Configure pytest settings."""
    config.addinivalue_line(
        "markers", "integration: mark test as integration test"
    )
    config.addinivalue_line(
        "markers", "unit: mark test as unit test"
    )
    config.addinivalue_line(
        "markers", "e2e: mark test as end-to-end test"
    )
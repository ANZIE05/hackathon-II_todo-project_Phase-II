"""
Environment-specific configuration for the Todo Application Backend.
"""

from pydantic import BaseModel
from typing import Optional
from src.config.settings import settings


class EnvironmentConfig(BaseModel):
    """
    Configuration settings for different environments.
    """
    environment: str
    debug: bool
    database_url: str
    secret_key: str
    jwt_expiration_hours: int
    allowed_origins: list
    redis_url: Optional[str] = None

    class Config:
        arbitrary_types_allowed = True


def get_environment_config() -> EnvironmentConfig:
    """
    Get configuration based on the current environment.

    Returns:
        EnvironmentConfig: Configuration for the current environment
    """
    env = settings.ENVIRONMENT.lower()

    if env == "development":
        return EnvironmentConfig(
            environment="development",
            debug=True,
            database_url=settings.NEON_DB_URL,
            secret_key=settings.BETTER_AUTH_SECRET,
            jwt_expiration_hours=settings.JWT_EXPIRATION_HOURS,
            allowed_origins=settings.allowed_origins_list,
            redis_url=settings.REDIS_URL
        )
    elif env == "testing":
        return EnvironmentConfig(
            environment="testing",
            debug=True,
            database_url="sqlite:///./test.db",  # Override for tests
            secret_key="test-secret-key-change-in-production",
            jwt_expiration_hours=1,  # Short expiration for testing
            allowed_origins=["http://localhost:3000", "http://localhost:8080"],
            redis_url=None  # No Redis for testing
        )
    elif env == "staging":
        return EnvironmentConfig(
            environment="staging",
            debug=False,
            database_url=settings.NEON_DB_URL,
            secret_key=settings.BETTER_AUTH_SECRET,
            jwt_expiration_hours=settings.JWT_EXPIRATION_HOURS,
            allowed_origins=["https://staging.todoapp.com"],
            redis_url=settings.REDIS_URL
        )
    elif env == "production":
        return EnvironmentConfig(
            environment="production",
            debug=False,
            database_url=settings.NEON_DB_URL,
            secret_key=settings.BETTER_AUTH_SECRET,
            jwt_expiration_hours=settings.JWT_EXPIRATION_HOURS,
            allowed_origins=["https://todoapp.com", "https://www.todoapp.com"],
            redis_url=settings.REDIS_URL
        )
    else:
        # Default to development config
        return EnvironmentConfig(
            environment="development",
            debug=True,
            database_url=settings.NEON_DB_URL,
            secret_key=settings.BETTER_AUTH_SECRET,
            jwt_expiration_hours=settings.JWT_EXPIRATION_HOURS,
            allowed_origins=settings.allowed_origins_list,
            redis_url=settings.REDIS_URL
        )


def is_development() -> bool:
    """
    Check if the current environment is development.

    Returns:
        bool: True if development environment
    """
    return settings.is_development


def is_production() -> bool:
    """
    Check if the current environment is production.

    Returns:
        bool: True if production environment
    """
    return settings.is_production


def is_testing() -> bool:
    """
    Check if the current environment is testing.

    Returns:
        bool: True if testing environment
    """
    return settings.ENVIRONMENT.lower() == "testing"


def is_staging() -> bool:
    """
    Check if the current environment is staging.

    Returns:
        bool: True if staging environment
    """
    return settings.ENVIRONMENT.lower() == "staging"
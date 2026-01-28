"""
Startup checks for the Todo Application Backend.
This module performs essential checks before the application starts serving traffic.
"""

import asyncio
import sys
import logging
from typing import List, Tuple
from sqlalchemy import text
from sqlmodel import Session
from src.database.connection import get_session
from src.config.settings import settings
from src.services.user_service import UserService


logger = logging.getLogger(__name__)


class StartupCheckError(Exception):
    """
    Exception raised when a startup check fails.
    """
    pass


async def check_database_connection() -> Tuple[bool, str]:
    """
    Check if the application can connect to the database.

    Returns:
        Tuple[bool, str]: (success, message)
    """
    try:
        # Try to get a session and execute a simple query
        session_generator = get_session()
        session = next(session_generator)

        try:
            # Execute a simple query to test the connection
            result = session.exec(text("SELECT 1"))
            result.fetchone()

            logger.info("Database connection check passed")
            return True, "Database connection successful"
        finally:
            session.close()
    except Exception as e:
        logger.error(f"Database connection check failed: {str(e)}")
        return False, f"Database connection failed: {str(e)}"


async def check_required_settings() -> Tuple[bool, str]:
    """
    Check if all required settings are properly configured.

    Returns:
        Tuple[bool, str]: (success, message)
    """
    required_settings = [
        "NEON_DB_URL",
        "BETTER_AUTH_SECRET",
    ]

    missing_settings = []
    for setting_name in required_settings:
        setting_value = getattr(settings, setting_name, None)
        if not setting_value:
            missing_settings.append(setting_name)

    if missing_settings:
        error_msg = f"Missing required settings: {', '.join(missing_settings)}"
        logger.error(error_msg)
        return False, error_msg

    # Check if auth secret is strong enough (at least 32 characters)
    if len(settings.BETTER_AUTH_SECRET) < 32:
        warning_msg = "WARNING: BETTER_AUTH_SECRET should be at least 32 characters for security"
        logger.warning(warning_msg)

    logger.info("Required settings check passed")
    return True, "All required settings are configured"


async def check_database_migrations() -> Tuple[bool, str]:
    """
    Check if database migrations are up to date.

    Returns:
        Tuple[bool, str]: (success, message)
    """
    try:
        # Try to get a session and check if tables exist
        session_generator = get_session()
        session = next(session_generator)

        try:
            # Try to query the users table (or any table) to ensure it exists
            result = session.exec(text("SELECT COUNT(*) FROM user LIMIT 1"))
            result.fetchone()

            logger.info("Database migrations check passed")
            return True, "Database migrations are up to date"
        except Exception as e:
            # Table might not exist, meaning migrations haven't been run
            error_msg = f"Database migrations may not be up to date: {str(e)}"
            logger.error(error_msg)
            return False, error_msg
        finally:
            session.close()
    except Exception as e:
        logger.error(f"Database migrations check failed: {str(e)}")
        return False, f"Database migrations check failed: {str(e)}"


async def check_external_services() -> Tuple[bool, str]:
    """
    Check if external services are available (Redis, etc.).

    Returns:
        Tuple[bool, str]: (success, message)
    """
    checks_passed = []
    checks_failed = []

    # Check Redis if configured
    if settings.REDIS_URL:
        try:
            import redis
            redis_client = redis.from_url(settings.REDIS_URL)
            redis_client.ping()
            checks_passed.append("Redis connection successful")
            logger.info("Redis connection check passed")
        except ImportError:
            checks_passed.append("Redis not installed, skipping check")
            logger.info("Redis not installed, skipping check")
        except Exception as e:
            checks_failed.append(f"Redis connection failed: {str(e)}")
            logger.error(f"Redis connection check failed: {str(e)}")
    else:
        checks_passed.append("Redis not configured, skipping check")
        logger.info("Redis not configured, skipping check")

    if checks_failed:
        return False, "; ".join(checks_failed)
    else:
        return True, "; ".join(checks_passed)


async def run_startup_checks() -> bool:
    """
    Run all startup checks and return True if all pass.

    Returns:
        bool: True if all checks pass, False otherwise
    """
    logger.info("Starting startup checks...")

    checks = [
        ("Required Settings", check_required_settings),
        ("Database Connection", check_database_connection),
        ("Database Migrations", check_database_migrations),
        ("External Services", check_external_services),
    ]

    all_passed = True
    results = []

    for check_name, check_func in checks:
        logger.info(f"Running {check_name} check...")
        try:
            success, message = await check_func()
            results.append((check_name, success, message))
            if not success:
                all_passed = False
                logger.error(f"{check_name} check FAILED: {message}")
            else:
                logger.info(f"{check_name} check PASSED: {message}")
        except Exception as e:
            all_passed = False
            error_msg = f"Exception during {check_name} check: {str(e)}"
            results.append((check_name, False, error_msg))
            logger.error(error_msg)

    # Print summary
    logger.info("="*50)
    logger.info("STARTUP CHECKS SUMMARY")
    logger.info("="*50)

    for check_name, success, message in results:
        status = "PASS" if success else "FAIL"
        logger.info(f"{check_name}: [{status}] {message}")

    logger.info("="*50)

    if not all_passed:
        logger.error("One or more startup checks failed. Application cannot start.")
        return False

    logger.info("All startup checks passed. Application is ready to start.")
    return True


def perform_startup_checks_sync() -> bool:
    """
    Synchronous wrapper for startup checks.
    This is useful for running checks in a synchronous context.

    Returns:
        bool: True if all checks pass, False otherwise
    """
    try:
        # Check if there's already an event loop running (e.g., in FastAPI)
        try:
            loop = asyncio.get_running_loop()
            # If we get here, there's already a loop running
            # We can't run the async function in the same thread
            # So we'll create a new thread to run the checks
            import concurrent.futures
            with concurrent.futures.ThreadPoolExecutor() as executor:
                future = executor.submit(lambda: asyncio.run(run_startup_checks()))
                return future.result()
        except RuntimeError:
            # No event loop is running, we can create one safely
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                return loop.run_until_complete(run_startup_checks())
            finally:
                loop.close()
    except Exception as e:
        logger.error(f"Error running startup checks: {str(e)}")
        return False


if __name__ == "__main__":
    """
    Main entry point for running startup checks independently.
    """
    import argparse

    parser = argparse.ArgumentParser(description="Run startup checks for the Todo Application")
    parser.add_argument("--verbose", "-v", action="store_true", help="Enable verbose logging")

    args = parser.parse_args()

    if args.verbose:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.INFO)

    success = perform_startup_checks_sync()

    if not success:
        sys.exit(1)
    else:
        print("All startup checks passed!")
        sys.exit(0)
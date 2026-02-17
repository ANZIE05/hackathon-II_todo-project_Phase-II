from sqlmodel import Session
from contextlib import contextmanager
from typing import Generator
from src.database.connection import engine, get_session
from functools import wraps
from typing import Callable, Any


def get_db_session() -> Session:
    """
    Get a database session.

    Returns:
        Session: Database session
    """
    with Session(engine) as session:
        return session


@contextmanager
def get_db_context() -> Generator[Session, None, None]:
    """
    Get a database session with context manager.

    Yields:
        Session: Database session
    """
    session = get_db_session()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def db_transaction(func: Callable) -> Callable:
    """
    Decorator to wrap a function in a database transaction.

    Args:
        func: Function to decorate

    Returns:
        Callable: Decorated function
    """
    @wraps(func)
    def wrapper(*args, **kwargs) -> Any:
        with get_db_context() as session:
            # Inject the session as a keyword argument
            kwargs['db_session'] = session
            return func(*args, **kwargs)
    return wrapper


def get_session_with_retry(max_retries: int = 3):
    """
    Get a database session with retry logic.

    Args:
        max_retries: Maximum number of retry attempts

    Returns:
        Generator: Database session generator
    """
    for attempt in range(max_retries):
        try:
            yield from get_session()
            break
        except Exception as e:
            if attempt == max_retries - 1:
                raise e


def execute_query_with_retry(query_func, max_retries: int = 3):
    """
    Execute a query function with retry logic.

    Args:
        query_func: Function that executes the query
        max_retries: Maximum number of retry attempts

    Returns:
        Result of the query function
    """
    for attempt in range(max_retries):
        try:
            return query_func()
        except Exception as e:
            if attempt == max_retries - 1:
                raise e


class DatabaseManager:
    """
    Manager class for database operations with common utilities.
    """

    @staticmethod
    def get_session() -> Generator[Session, None, None]:
        """
        Get a database session.

        Yields:
            Session: Database session
        """
        yield from get_session()

    @staticmethod
    def get_session_context() -> Generator[Session, None, None]:
        """
        Get a database session with proper context management.

        Yields:
            Session: Database session
        """
        with Session(engine) as session:
            yield session

    @staticmethod
    def run_in_transaction(func, *args, **kwargs):
        """
        Run a function inside a database transaction.

        Args:
            func: Function to run
            *args: Arguments to pass to the function
            **kwargs: Keyword arguments to pass to the function

        Returns:
            Result of the function
        """
        with get_db_context() as session:
            return func(session, *args, **kwargs)


def init_db_tables():
    """
    Initialize all database tables.
    """
    from sqlmodel import SQLModel
    from src.models.user import User
    from src.models.task import Task

    SQLModel.metadata.create_all(bind=engine)


def drop_db_tables():
    """
    Drop all database tables (use with caution!).
    """
    from sqlmodel import SQLModel

    SQLModel.metadata.drop_all(bind=engine)
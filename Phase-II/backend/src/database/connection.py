from sqlmodel import create_engine, Session
from src.config.settings import settings
from typing import Generator
import os

# Create the database engine
engine = create_engine(
    settings.NEON_DB_URL,
    echo=settings.DEBUG,  # Log SQL statements in development
    pool_pre_ping=True,   # Verify connections before use
    pool_recycle=300,     # Recycle connections every 5 minutes
)


def get_session() -> Generator[Session, None, None]:
    """
    Get a database session.

    Yields:
        Session: Database session
    """
    with Session(engine) as session:
        yield session


def init_db() -> None:
    """
    Initialize the database by creating all tables.
    This function should be called during application startup.
    """
    from sqlmodel import SQLModel
    from src.models.user import User
    from src.models.task import Task

    # Create all tables
    SQLModel.metadata.create_all(engine)


if __name__ == "__main__":
    # Initialize the database when this module is run directly
    init_db()
    print("Database initialized successfully!")
from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, TYPE_CHECKING
from datetime import datetime
import uuid
from sqlalchemy import String
from pydantic import EmailStr
from enum import Enum
from src.database.base import BaseSQLModel

if TYPE_CHECKING:
    from src.models.task import Task


class UserRole(str, Enum):
    """
    Enum representing different user roles in the system.
    """
    ADMIN = "admin"
    USER = "user"


class UserBase(SQLModel):
    """
    Base class containing common fields for User model.
    """
    email: str = Field(unique=True, nullable=False, max_length=255)
    is_active: bool = Field(default=True)


class User(UserBase, BaseSQLModel, table=True):
    """
    User model representing a registered user account.

    Attributes:
        id: Unique identifier for the user (UUID)
        email: User's email address for authentication
        hashed_password: Securely hashed password using bcrypt
        is_active: Flag indicating if account is active
        created_at: Timestamp of account creation
        updated_at: Timestamp of last account update
        tasks: Relationship to associated tasks
    """
    # Fields from UserBase
    # email: EmailStr = Field(unique=True, nullable=False, max_length=255)
    # is_active: bool = Field(default=True)

    # Additional fields
    hashed_password: str = Field(nullable=False, max_length=255)

    # Relationship to tasks
    tasks: list["Task"] = Relationship(back_populates="user")


class UserRead(UserBase):
    """
    Schema for reading user data.
    """
    id: uuid.UUID
    created_at: datetime
    updated_at: datetime
    is_active: bool


class UserCreate(UserBase):
    """
    Schema for creating a new user.
    """
    password: str
    role: Optional[UserRole] = Field(default=UserRole.USER)


class UserUpdate(SQLModel):
    """
    Schema for updating user data.
    """
    email: Optional[str] = None
    is_active: Optional[bool] = None
    password: Optional[str] = None


class UserLogin(SQLModel):
    """
    Schema for user login credentials.
    """
    email: str
    password: str


class UserPublic(UserBase):
    """
    Public schema for user data (excludes sensitive information).
    """
    id: uuid.UUID
    created_at: datetime
    is_active: bool
from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, TYPE_CHECKING
from datetime import datetime
import uuid
from enum import Enum
from src.database.base import BaseSQLModel
from pydantic import validator

if TYPE_CHECKING:
    from src.models.user import User


class TaskPriority(str, Enum):
    """
    Enum representing different priority levels for tasks.
    """
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class TaskStatus(str, Enum):
    """
    Enum representing different statuses for tasks.
    """
    PENDING = "pending"
    COMPLETED = "completed"


class TaskBase(SQLModel):
    """
    Base class containing common fields for Task model.
    """
    title: str = Field(min_length=1, max_length=255, nullable=False)
    description: Optional[str] = Field(default=None)
    due_date: Optional[datetime] = Field(default=None)
    priority: TaskPriority = Field(default=TaskPriority.MEDIUM)
    completed: bool = Field(default=False)


class Task(TaskBase, BaseSQLModel, table=True):
    """
    Task model representing a user's todo item.

    Attributes:
        id: Unique identifier for the task (UUID)
        title: Task title or name
        description: Detailed description of the task
        due_date: Deadline for completing the task
        priority: Priority level of the task (low, medium, high)
        completed: Flag indicating if task is completed
        user_id: Reference to the user who owns this task
        created_at: Timestamp of task creation
        updated_at: Timestamp of last task update
        user: Relationship to the owning user
    """
    # Fields from TaskBase
    # title: str = Field(min_length=1, max_length=255, nullable=False)
    # description: Optional[str] = Field(default=None)
    # due_date: Optional[datetime] = Field(default=None)
    # priority: TaskPriority = Field(default=TaskPriority.MEDIUM)
    # completed: bool = Field(default=False)

    # Additional fields
    user_id: uuid.UUID = Field(foreign_key="user.id", nullable=False)

    # Relationship to user
    user: Optional["User"] = Relationship(back_populates="tasks")


class TaskRead(TaskBase):
    """
    Schema for reading task data.
    """
    id: uuid.UUID
    user_id: uuid.UUID
    created_at: datetime
    updated_at: datetime


class TaskCreate(TaskBase):
    """
    Schema for creating a new task.
    """
    pass


class TaskUpdate(SQLModel):
    """
    Schema for updating task data.
    """
    title: Optional[str] = None
    description: Optional[str] = None
    due_date: Optional[datetime] = None
    priority: Optional[TaskPriority] = None
    completed: Optional[bool] = None


class TaskPatch(SQLModel):
    """
    Schema for partially updating task data (e.g., for completing a task).
    """
    completed: Optional[bool] = None


class TaskFilter(SQLModel):
    """
    Schema for filtering tasks.
    """
    status: Optional[TaskStatus] = None
    priority: Optional[TaskPriority] = None
    user_id: Optional[uuid.UUID] = None
from sqlmodel import SQLModel
from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from enum import Enum
from uuid import UUID


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
    Base schema containing common fields for Task.
    """
    title: str
    description: Optional[str] = None
    due_date: Optional[datetime] = None
    priority: TaskPriority = TaskPriority.MEDIUM


class TaskCreate(TaskBase):
    """
    Schema for creating a new task.
    """
    title: str
    description: Optional[str] = None
    due_date: Optional[datetime] = None
    priority: TaskPriority = TaskPriority.MEDIUM
    completed: bool = False


class TaskUpdate(SQLModel):
    """
    Schema for updating task information.
    """
    title: Optional[str] = None
    description: Optional[str] = None
    due_date: Optional[datetime] = None
    priority: Optional[TaskPriority] = None
    completed: Optional[bool] = None


class TaskPatch(SQLModel):
    """
    Schema for partially updating task information (e.g., for completing a task).
    """
    completed: Optional[bool] = None


class TaskRead(TaskBase):
    """
    Schema for reading task information.
    """
    id: UUID
    user_id: UUID
    completed: bool
    created_at: datetime
    updated_at: datetime


class TaskFilter(BaseModel):
    """
    Schema for filtering tasks.
    """
    status: Optional[TaskStatus] = None
    priority: Optional[TaskPriority] = None
    limit: int = 100
    offset: int = 0
    sort: Optional[str] = None  # e.g., "created_at", "-due_date" for descending


class TaskListResponse(BaseModel):
    """
    Schema for task list response with pagination.
    """
    tasks: list[TaskRead]
    total: int
    page_info: dict


class TaskStats(BaseModel):
    """
    Schema for task statistics.
    """
    total: int
    completed: int
    pending: int
    overdue: int
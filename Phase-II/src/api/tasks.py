from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session
from typing import Optional
from src.database.connection import get_session
from src.schemas.task import TaskCreate, TaskUpdate, TaskPatch, TaskFilter
from src.services.task_service import TaskService
from src.repositories.task_repository import TaskRepository
from src.models.task import Task
from src.models.user import User
from src.utils.authz import verify_task_ownership
from src.api.deps import get_current_user, get_current_active_user
from src.utils.error_response import create_error_response, create_not_found_error, create_bad_request_error
from uuid import UUID


router = APIRouter(prefix="/tasks", tags=["Tasks"])


@router.post("/", response_model=Task)
def create_task(
    task_create: TaskCreate,
    db: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """
    Create a new task for the authenticated user.

    Args:
        task_create: Task creation data
        db: Database session
        current_user: Authenticated user

    Returns:
        Task: The created task object

    Raises:
        HTTPException: If task creation fails
    """
    # Create the task for the current user
    task = TaskService.create_task(db, task_create, current_user.id)

    if not task:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to create task"
        )

    return task


@router.get("/")
def list_tasks(
    db: Session = Depends(get_session),
    filters: Optional[TaskFilter] = None,
    current_user: User = Depends(get_current_user)
):
    """
    List tasks for the authenticated user with optional filtering.

    Args:
        db: Database session
        filters: Optional filters for the query
        current_user: Authenticated user

    Returns:
        dict: List of tasks and metadata
    """
    # Get tasks for the current user
    result = TaskService.get_tasks_by_user(db, current_user.id, filters)

    return {
        "tasks": result.tasks,
        "total": result.total,
        "page_info": result.page_info
    }


@router.get("/{task_id}", response_model=Task)
def get_task(
    task_id: UUID,
    db: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """
    Get a specific task by its ID.

    Args:
        task_id: Task ID
        db: Database session
        current_user: Authenticated user

    Returns:
        Task: The requested task object

    Raises:
        HTTPException: If task not found or user not authorized
    """
    # Get the task and verify ownership
    task = TaskService.get_task_by_id(db, task_id, current_user.id)

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found or access denied"
        )

    return task


@router.put("/{task_id}", response_model=Task)
def update_task(
    task_id: UUID,
    task_update: TaskUpdate,
    db: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """
    Update a task by its ID.

    Args:
        task_id: Task ID
        task_update: Task update data
        db: Database session
        current_user: Authenticated user

    Returns:
        Task: The updated task object

    Raises:
        HTTPException: If task not found, update fails, or user not authorized
    """
    # Update the task and verify ownership
    task = TaskService.update_task(db, task_id, task_update, current_user.id)

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found or access denied"
        )

    return task


@router.patch("/{task_id}/complete", response_model=Task)
def complete_task(
    task_id: UUID,
    task_patch: TaskPatch,
    db: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """
    Mark a task as completed.

    Args:
        task_id: Task ID
        task_patch: Task patch data (should contain completed=True)
        db: Database session
        current_user: Authenticated user

    Returns:
        Task: The updated task object

    Raises:
        HTTPException: If task not found, update fails, or user not authorized
    """
    # Patch the task to mark as completed
    task = TaskService.patch_task(db, task_id, task_patch, current_user.id)

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found or access denied"
        )

    return task


@router.delete("/{task_id}")
def delete_task(
    task_id: UUID,
    db: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """
    Delete a task by its ID.

    Args:
        task_id: Task ID
        db: Database session
        current_user: Authenticated user

    Returns:
        dict: Success message

    Raises:
        HTTPException: If task not found or user not authorized
    """
    # Delete the task and verify ownership
    success = TaskService.delete_task(db, task_id, current_user.id)

    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found or access denied"
        )

    return {"message": "Task deleted successfully"}


@router.patch("/{task_id}", response_model=Task)
def patch_task(
    task_id: UUID,
    task_patch: TaskPatch,
    db: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """
    Partially update a task by its ID.

    Args:
        task_id: Task ID
        task_patch: Task patch data
        db: Database session
        current_user: Authenticated user

    Returns:
        Task: The updated task object

    Raises:
        HTTPException: If task not found, update fails, or user not authorized
    """
    # Patch the task with provided data
    task = TaskService.patch_task(db, task_id, task_patch, current_user.id)

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found or access denied"
        )

    return task
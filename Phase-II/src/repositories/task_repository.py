from sqlmodel import Session, select
from typing import List, Optional
from src.models.task import Task
from src.models.user import User
from src.schemas.task import TaskCreate, TaskUpdate, TaskPatch
from uuid import UUID
from datetime import datetime


class TaskRepository:
    """
    Repository class for task-related database operations.
    Provides methods for CRUD operations on Task model with user-scoped queries.
    """

    @staticmethod
    def create_task(db: Session, task_create: TaskCreate, user_id: UUID) -> Optional[Task]:
        """
        Create a new task for a user.

        Args:
            db: Database session
            task_create: Task creation data
            user_id: ID of the user creating the task

        Returns:
            Task: The created task object if successful, None otherwise
        """
        # Create task data with user association
        task = Task(
            title=task_create.title,
            description=task_create.description,
            due_date=task_create.due_date,
            priority=task_create.priority,
            completed=task_create.completed,
            user_id=user_id
        )

        # Add to session and commit
        db.add(task)
        db.commit()
        db.refresh(task)

        return task

    @staticmethod
    def get_task_by_id(db: Session, task_id: UUID, user_id: UUID) -> Optional[Task]:
        """
        Retrieve a task by its ID, ensuring it belongs to the user.

        Args:
            db: Database session
            task_id: Task ID
            user_id: User ID (to ensure ownership)

        Returns:
            Task: The task object if found and owned by user, None otherwise
        """
        statement = select(Task).where(Task.id == task_id, Task.user_id == user_id)
        return db.exec(statement).first()

    @staticmethod
    def get_tasks_by_user(
        db: Session,
        user_id: UUID,
        skip: int = 0,
        limit: int = 100,
        completed: Optional[bool] = None,
        priority: Optional[str] = None
    ) -> List[Task]:
        """
        Retrieve all tasks for a specific user with optional filters.

        Args:
            db: Database session
            user_id: User ID
            skip: Number of records to skip
            limit: Maximum number of records to return
            completed: Filter by completion status
            priority: Filter by priority level

        Returns:
            List[Task]: List of tasks matching the criteria
        """
        statement = select(Task).where(Task.user_id == user_id)

        # Apply filters if provided
        if completed is not None:
            statement = statement.where(Task.completed == completed)

        if priority is not None:
            statement = statement.where(Task.priority == priority)

        # Apply pagination
        statement = statement.offset(skip).limit(limit)

        return db.exec(statement).all()

    @staticmethod
    def get_task_count_by_user(
        db: Session,
        user_id: UUID,
        completed: Optional[bool] = None,
        priority: Optional[str] = None
    ) -> int:
        """
        Get the count of tasks for a specific user with optional filters.

        Args:
            db: Database session
            user_id: User ID
            completed: Filter by completion status
            priority: Filter by priority level

        Returns:
            int: Count of tasks matching the criteria
        """
        statement = select(Task).where(Task.user_id == user_id)

        # Apply filters if provided
        if completed is not None:
            statement = statement.where(Task.completed == completed)

        if priority is not None:
            statement = statement.where(Task.priority == priority)

        return len(db.exec(statement).all())

    @staticmethod
    def update_task(db: Session, task_id: UUID, task_update: TaskUpdate, user_id: UUID) -> Optional[Task]:
        """
        Update a task's information, ensuring it belongs to the user.

        Args:
            db: Database session
            task_id: Task ID
            task_update: Task update data
            user_id: User ID (to ensure ownership)

        Returns:
            Task: The updated task object if successful, None otherwise
        """
        # Get the task and ensure it belongs to the user
        task = TaskRepository.get_task_by_id(db, task_id, user_id)
        if not task:
            return None

        # Update fields if they are provided
        update_data = task_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(task, field, value)

        # Update the timestamp
        task.updated_at = datetime.utcnow()

        db.add(task)
        db.commit()
        db.refresh(task)

        return task

    @staticmethod
    def patch_task(db: Session, task_id: UUID, task_patch: TaskPatch, user_id: UUID) -> Optional[Task]:
        """
        Partially update a task's information (e.g., for completing a task).

        Args:
            db: Database session
            task_id: Task ID
            task_patch: Task patch data
            user_id: User ID (to ensure ownership)

        Returns:
            Task: The updated task object if successful, None otherwise
        """
        # Get the task and ensure it belongs to the user
        task = TaskRepository.get_task_by_id(db, task_id, user_id)
        if not task:
            return None

        # Update fields if they are provided
        update_data = task_patch.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(task, field, value)

        # Update the timestamp
        task.updated_at = datetime.utcnow()

        db.add(task)
        db.commit()
        db.refresh(task)

        return task

    @staticmethod
    def delete_task(db: Session, task_id: UUID, user_id: UUID) -> bool:
        """
        Delete a task, ensuring it belongs to the user.

        Args:
            db: Database session
            task_id: Task ID
            user_id: User ID (to ensure ownership)

        Returns:
            bool: True if deletion was successful, False otherwise
        """
        # Get the task and ensure it belongs to the user
        task = TaskRepository.get_task_by_id(db, task_id, user_id)
        if not task:
            return False

        db.delete(task)
        db.commit()

        return True

    @staticmethod
    def get_completed_tasks_count(db: Session, user_id: UUID) -> int:
        """
        Get the count of completed tasks for a user.

        Args:
            db: Database session
            user_id: User ID

        Returns:
            int: Count of completed tasks
        """
        statement = select(Task).where(Task.user_id == user_id, Task.completed == True)
        return len(db.exec(statement).all())

    @staticmethod
    def get_pending_tasks_count(db: Session, user_id: UUID) -> int:
        """
        Get the count of pending tasks for a user.

        Args:
            db: Database session
            user_id: User ID

        Returns:
            int: Count of pending tasks
        """
        statement = select(Task).where(Task.user_id == user_id, Task.completed == False)
        return len(db.exec(statement).all())

    @staticmethod
    def get_overdue_tasks(db: Session, user_id: UUID) -> List[Task]:
        """
        Get all overdue tasks for a user.

        Args:
            db: Database session
            user_id: User ID

        Returns:
            List[Task]: List of overdue tasks
        """
        statement = select(Task).where(
            Task.user_id == user_id,
            Task.completed == False,
            Task.due_date < datetime.utcnow()
        ).order_by(Task.due_date)

        return db.exec(statement).all()

    @staticmethod
    def get_tasks_due_today(db: Session, user_id: UUID) -> List[Task]:
        """
        Get all tasks due today for a user.

        Args:
            db: Database session
            user_id: User ID

        Returns:
            List[Task]: List of tasks due today
        """
        from datetime import date
        today = date.today()

        statement = select(Task).where(
            Task.user_id == user_id,
            Task.completed == False,
            Task.due_date >= datetime.combine(today, datetime.min.time()),
            Task.due_date < datetime.combine(today, datetime.max.time()).replace(microsecond=999999)
        )

        return db.exec(statement).all()

    @staticmethod
    def bulk_delete_tasks(db: Session, task_ids: List[UUID], user_id: UUID) -> int:
        """
        Delete multiple tasks for a user.

        Args:
            db: Database session
            task_ids: List of task IDs to delete
            user_id: User ID (to ensure ownership)

        Returns:
            int: Number of tasks deleted
        """
        # Verify all tasks belong to the user
        statement = select(Task).where(Task.id.in_(task_ids), Task.user_id == user_id)
        user_tasks = db.exec(statement).all()

        # Get the IDs of tasks that actually belong to the user
        valid_task_ids = [task.id for task in user_tasks]

        if not valid_task_ids:
            return 0

        # Delete the tasks
        delete_statement = select(Task).where(Task.id.in_(valid_task_ids))
        tasks_to_delete = db.exec(delete_statement).all()

        for task in tasks_to_delete:
            db.delete(task)

        db.commit()
        return len(tasks_to_delete)
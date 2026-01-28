from sqlmodel import Session, select
from typing import List, Optional
from src.models.task import Task
from src.models.user import User
from src.schemas.task import TaskCreate, TaskUpdate, TaskPatch, TaskFilter, TaskListResponse, TaskStats
from src.database.service import DatabaseService
from uuid import UUID
from datetime import datetime


class TaskService:
    """
    Service class for task-related operations.
    Handles creation, retrieval, update, and deletion of tasks with user authorization.
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
        filters: Optional[TaskFilter] = None
    ) -> TaskListResponse:
        """
        Retrieve all tasks for a specific user with optional filters.

        Args:
            db: Database session
            user_id: User ID
            filters: Optional filters for the query

        Returns:
            TaskListResponse: Response containing tasks and metadata
        """
        statement = select(Task).where(Task.user_id == user_id)

        # Apply filters if provided
        if filters:
            if filters.status:
                if filters.status == "completed":
                    statement = statement.where(Task.completed == True)
                else:
                    statement = statement.where(Task.completed == False)

            if filters.priority:
                statement = statement.where(Task.priority == filters.priority)

        # Apply sorting
        if filters and filters.sort:
            if filters.sort.startswith('-'):
                # Descending order
                sort_field = getattr(Task, filters.sort[1:])
                statement = statement.order_by(sort_field.desc())
            else:
                # Ascending order
                sort_field = getattr(Task, filters.sort)
                statement = statement.order_by(sort_field)

        # Apply pagination
        statement = statement.offset(filters.offset if filters else 0).limit(filters.limit if filters else 100)

        tasks = db.exec(statement).all()

        # Get total count
        count_statement = select(Task).where(Task.user_id == user_id)
        if filters:
            if filters.status:
                if filters.status == "completed":
                    count_statement = count_statement.where(Task.completed == True)
                else:
                    count_statement = count_statement.where(Task.completed == False)
            if filters.priority:
                count_statement = count_statement.where(Task.priority == filters.priority)

        total = db.exec(count_statement).count()

        return TaskListResponse(
            tasks=tasks,
            total=total,
            page_info={
                "limit": filters.limit if filters else 100,
                "offset": filters.offset if filters else 0,
                "has_more": (filters.offset if filters else 0) + len(tasks) < total
            }
        )

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
        task = TaskService.get_task_by_id(db, task_id, user_id)
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
        task = TaskService.get_task_by_id(db, task_id, user_id)
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
        task = TaskService.get_task_by_id(db, task_id, user_id)
        if not task:
            return False

        db.delete(task)
        db.commit()

        return True

    @staticmethod
    def get_task_stats(db: Session, user_id: UUID) -> TaskStats:
        """
        Get statistics for a user's tasks.

        Args:
            db: Database session
            user_id: User ID

        Returns:
            TaskStats: Statistics about the user's tasks
        """
        # Total tasks
        total_stmt = select(Task).where(Task.user_id == user_id)
        total_tasks = len(db.exec(total_stmt).all())

        # Completed tasks
        completed_stmt = select(Task).where(Task.user_id == user_id, Task.completed == True)
        completed_tasks = len(db.exec(completed_stmt).all())

        # Pending tasks
        pending_tasks = total_tasks - completed_tasks

        # Overdue tasks (not completed and past due date)
        overdue_stmt = select(Task).where(
            Task.user_id == user_id,
            Task.completed == False,
            Task.due_date < datetime.utcnow()
        )
        overdue_tasks = len(db.exec(overdue_stmt).all())

        return TaskStats(
            total=total_tasks,
            completed=completed_tasks,
            pending=pending_tasks,
            overdue=overdue_tasks
        )

    @staticmethod
    def mark_task_completed(db: Session, task_id: UUID, user_id: UUID) -> Optional[Task]:
        """
        Mark a task as completed.

        Args:
            db: Database session
            task_id: Task ID
            user_id: User ID (to ensure ownership)

        Returns:
            Task: The updated task object if successful, None otherwise
        """
        return TaskService.patch_task(db, task_id, TaskPatch(completed=True), user_id)

    @staticmethod
    def mark_task_uncompleted(db: Session, task_id: UUID, user_id: UUID) -> Optional[Task]:
        """
        Mark a task as not completed.

        Args:
            db: Database session
            task_id: Task ID
            user_id: User ID (to ensure ownership)

        Returns:
            Task: The updated task object if successful, None otherwise
        """
        return TaskService.patch_task(db, task_id, TaskPatch(completed=False), user_id)

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
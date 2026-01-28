from sqlmodel import Session, select, func
from typing import List, Optional
from src.models.user import User, UserCreate, UserUpdate
from src.models.task import Task, TaskCreate, TaskUpdate, TaskFilter, TaskPriority, TaskStatus
from src.utils.password import hash_password
from uuid import UUID


class DatabaseService:
    """
    Service class for common database operations.
    Provides methods for CRUD operations on User and Task models.
    """

    @staticmethod
    def create_user(session: Session, user_create: UserCreate) -> User:
        """
        Create a new user in the database.

        Args:
            session: Database session
            user_create: User creation data

        Returns:
            User: The created user object
        """
        # Hash the password before storing
        hashed_password = hash_password(user_create.password)

        # Create user instance
        user = User(
            email=user_create.email,
            hashed_password=hashed_password,
            is_active=user_create.is_active if hasattr(user_create, 'is_active') else True
        )

        # Add to session and commit
        session.add(user)
        session.commit()
        session.refresh(user)

        return user

    @staticmethod
    def get_user_by_id(session: Session, user_id: UUID) -> Optional[User]:
        """
        Retrieve a user by their ID.

        Args:
            session: Database session
            user_id: User ID

        Returns:
            User: The user object if found, None otherwise
        """
        statement = select(User).where(User.id == user_id)
        return session.exec(statement).first()

    @staticmethod
    def get_user_by_email(session: Session, email: str) -> Optional[User]:
        """
        Retrieve a user by their email.

        Args:
            session: Database session
            email: User email

        Returns:
            User: The user object if found, None otherwise
        """
        statement = select(User).where(User.email == email)
        return session.exec(statement).first()

    @staticmethod
    def update_user(session: Session, user_id: UUID, user_update: UserUpdate) -> Optional[User]:
        """
        Update a user's information.

        Args:
            session: Database session
            user_id: User ID
            user_update: User update data

        Returns:
            User: The updated user object if successful, None otherwise
        """
        user = DatabaseService.get_user_by_id(session, user_id)
        if not user:
            return None

        # Update fields if they are provided
        update_data = user_update.dict(exclude_unset=True)
        if "password" in update_data:
            update_data["hashed_password"] = hash_password(update_data.pop("password"))

        for field, value in update_data.items():
            setattr(user, field, value)

        session.add(user)
        session.commit()
        session.refresh(user)

        return user

    @staticmethod
    def delete_user(session: Session, user_id: UUID) -> bool:
        """
        Delete a user from the database.

        Args:
            session: Database session
            user_id: User ID

        Returns:
            bool: True if deletion was successful, False otherwise
        """
        user = DatabaseService.get_user_by_id(session, user_id)
        if not user:
            return False

        session.delete(user)
        session.commit()
        return True

    @staticmethod
    def create_task(session: Session, task_create: TaskCreate, user_id: UUID) -> Task:
        """
        Create a new task for a user.

        Args:
            session: Database session
            task_create: Task creation data
            user_id: ID of the user creating the task

        Returns:
            Task: The created task object
        """
        task = Task.from_orm(task_create)
        task.user_id = user_id

        session.add(task)
        session.commit()
        session.refresh(task)

        return task

    @staticmethod
    def get_task_by_id(session: Session, task_id: UUID) -> Optional[Task]:
        """
        Retrieve a task by its ID.

        Args:
            session: Database session
            task_id: Task ID

        Returns:
            Task: The task object if found, None otherwise
        """
        statement = select(Task).where(Task.id == task_id)
        return session.exec(statement).first()

    @staticmethod
    def get_tasks_for_user(
        session: Session,
        user_id: UUID,
        filters: Optional[TaskFilter] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[Task]:
        """
        Retrieve tasks for a specific user with optional filters.

        Args:
            session: Database session
            user_id: ID of the user whose tasks to retrieve
            filters: Optional filters for the query
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List[Task]: List of tasks matching the criteria
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

        # Apply pagination
        statement = statement.offset(skip).limit(limit)

        return session.exec(statement).all()

    @staticmethod
    def update_task(session: Session, task_id: UUID, task_update: TaskUpdate) -> Optional[Task]:
        """
        Update a task's information.

        Args:
            session: Database session
            task_id: Task ID
            task_update: Task update data

        Returns:
            Task: The updated task object if successful, None otherwise
        """
        task = DatabaseService.get_task_by_id(session, task_id)
        if not task:
            return None

        # Update fields if they are provided
        update_data = task_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(task, field, value)

        session.add(task)
        session.commit()
        session.refresh(task)

        return task

    @staticmethod
    def delete_task(session: Session, task_id: UUID) -> bool:
        """
        Delete a task from the database.

        Args:
            session: Database session
            task_id: Task ID

        Returns:
            bool: True if deletion was successful, False otherwise
        """
        task = DatabaseService.get_task_by_id(session, task_id)
        if not task:
            return False

        session.delete(task)
        session.commit()
        return True

    @staticmethod
    def get_total_task_count(session: Session, user_id: UUID) -> int:
        """
        Get the total count of tasks for a user.

        Args:
            session: Database session
            user_id: ID of the user

        Returns:
            int: Total number of tasks for the user
        """
        statement = select(func.count(Task.id)).where(Task.user_id == user_id)
        return session.exec(statement).one()
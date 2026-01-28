from sqlmodel import Session, select
from typing import Optional
from src.models.user import User, UserCreate, UserUpdate
from src.models.task import Task
from src.utils.password import hash_password
from uuid import UUID


class UserRepository:
    """
    Repository class for user-related database operations.
    Provides methods for CRUD operations on User model.
    """

    @staticmethod
    def create_user(db: Session, user_create: UserCreate) -> Optional[User]:
        """
        Create a new user in the database.

        Args:
            db: Database session
            user_create: User creation data

        Returns:
            User: The created user object if successful, None otherwise
        """
        # Hash the password before storing
        hashed_password = hash_password(user_create.password)

        # Create user instance
        user = User(
            email=user_create.email,
            hashed_password=hashed_password,
            is_active=getattr(user_create, 'is_active', True)
        )

        # Add to session and commit
        db.add(user)
        db.commit()
        db.refresh(user)

        return user

    @staticmethod
    def get_user_by_id(db: Session, user_id: UUID) -> Optional[User]:
        """
        Retrieve a user by their ID.

        Args:
            db: Database session
            user_id: User ID

        Returns:
            User: The user object if found, None otherwise
        """
        statement = select(User).where(User.id == user_id)
        return db.exec(statement).first()

    @staticmethod
    def get_user_by_email(db: Session, email: str) -> Optional[User]:
        """
        Retrieve a user by their email.

        Args:
            db: Database session
            email: User email

        Returns:
            User: The user object if found, None otherwise
        """
        statement = select(User).where(User.email == email)
        return db.exec(statement).first()

    @staticmethod
    def get_users(db: Session, skip: int = 0, limit: int = 100) -> list[User]:
        """
        Retrieve a list of users.

        Args:
            db: Database session
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List[User]: List of users
        """
        statement = select(User).offset(skip).limit(limit)
        return db.exec(statement).all()

    @staticmethod
    def update_user(db: Session, user_id: UUID, user_update: UserUpdate) -> Optional[User]:
        """
        Update a user's information.

        Args:
            db: Database session
            user_id: User ID
            user_update: User update data

        Returns:
            User: The updated user object if successful, None otherwise
        """
        user = UserRepository.get_user_by_id(db, user_id)
        if not user:
            return None

        # Update fields if they are provided
        update_data = user_update.dict(exclude_unset=True)
        if "password" in update_data:
            update_data["hashed_password"] = hash_password(update_data.pop("password"))

        for field, value in update_data.items():
            setattr(user, field, value)

        db.add(user)
        db.commit()
        db.refresh(user)

        return user

    @staticmethod
    def delete_user(db: Session, user_id: UUID) -> bool:
        """
        Delete a user from the database.

        Args:
            db: Database session
            user_id: User ID

        Returns:
            bool: True if deletion was successful, False otherwise
        """
        user = UserRepository.get_user_by_id(db, user_id)
        if not user:
            return False

        # First delete all associated tasks
        task_statement = select(Task).where(Task.user_id == user_id)
        tasks = db.exec(task_statement).all()
        for task in tasks:
            db.delete(task)

        # Then delete the user
        db.delete(user)
        db.commit()
        return True

    @staticmethod
    def update_user_password(db: Session, user_id: UUID, new_password: str) -> bool:
        """
        Update a user's password.

        Args:
            db: Database session
            user_id: User ID
            new_password: New password

        Returns:
            bool: True if update was successful, False otherwise
        """
        user = UserRepository.get_user_by_id(db, user_id)
        if not user:
            return False

        user.hashed_password = hash_password(new_password)
        db.add(user)
        db.commit()
        db.refresh(user)

        return True

    @staticmethod
    def deactivate_user(db: Session, user_id: UUID) -> bool:
        """
        Deactivate a user account.

        Args:
            db: Database session
            user_id: User ID

        Returns:
            bool: True if update was successful, False otherwise
        """
        user = UserRepository.get_user_by_id(db, user_id)
        if not user:
            return False

        user.is_active = False
        db.add(user)
        db.commit()
        db.refresh(user)

        return True

    @staticmethod
    def activate_user(db: Session, user_id: UUID) -> bool:
        """
        Activate a user account.

        Args:
            db: Database session
            user_id: User ID

        Returns:
            bool: True if update was successful, False otherwise
        """
        user = UserRepository.get_user_by_id(db, user_id)
        if not user:
            return False

        user.is_active = True
        db.add(user)
        db.commit()
        db.refresh(user)

        return True

    @staticmethod
    def get_user_count(db: Session) -> int:
        """
        Get the total count of users.

        Args:
            db: Database session

        Returns:
            int: Total number of users
        """
        statement = select(User).where(User.is_active == True)
        return len(db.exec(statement).all())

    @staticmethod
    def get_user_with_tasks(db: Session, user_id: UUID) -> Optional[User]:
        """
        Retrieve a user with their associated tasks.

        Args:
            db: Database session
            user_id: User ID

        Returns:
            User: The user object with tasks if found, None otherwise
        """
        statement = select(User).where(User.id == user_id).join(Task)
        user = db.exec(statement).first()
        return user
from sqlmodel import Session
from typing import Optional
from src.models.user import User, UserCreate
from src.schemas.auth import RegisterRequest, LoginRequest
from src.utils.password import hash_password, verify_password
from src.utils.jwt import create_access_token
from src.database.service import DatabaseService
from datetime import timedelta


class UserService:
    """
    Service class for user-related operations.
    Handles registration, authentication, and user management.
    """

    @staticmethod
    def register_user(db: Session, user_data: RegisterRequest) -> Optional[dict]:
        """
        Register a new user.

        Args:
            db: Database session
            user_data: User registration data

        Returns:
            dict: User data and access token if registration is successful, None otherwise
        """
        # Check if user already exists
        existing_user = DatabaseService.get_user_by_email(db, user_data.email)
        if existing_user:
            return None  # User already exists

        # Create user data for database service
        user_create = UserCreate(
            email=user_data.email,
            password=user_data.password,
            is_active=True
        )

        # Create user in database
        user = DatabaseService.create_user(db, user_create)
        if not user:
            return None

        # Create access token
        token_data = {
            "sub": str(user.id),
            "email": user.email
        }
        access_token = create_access_token(data=token_data)

        return {
            "success": True,
            "token": access_token,
            "user": {
                "id": str(user.id),
                "email": user.email
            }
        }

    @staticmethod
    def authenticate_user(db: Session, login_data: LoginRequest) -> Optional[dict]:
        """
        Authenticate a user with email and password.

        Args:
            db: Database session
            login_data: User login data

        Returns:
            dict: User data and access token if authentication is successful, None otherwise
        """
        # Get user by email
        user = DatabaseService.get_user_by_email(db, login_data.email)
        if not user or not verify_password(login_data.password, user.hashed_password):
            return None

        # Check if user is active
        if not user.is_active:
            return None

        # Create access token
        token_data = {
            "sub": str(user.id),
            "email": user.email
        }
        access_token = create_access_token(data=token_data)

        return {
            "success": True,
            "token": access_token,
            "user": {
                "id": str(user.id),
                "email": user.email
            }
        }

    @staticmethod
    def get_user_by_id(db: Session, user_id: str) -> Optional[User]:
        """
        Get a user by their ID.

        Args:
            db: Database session
            user_id: User ID

        Returns:
            User: User object if found, None otherwise
        """
        return DatabaseService.get_user_by_id(db, user_id)

    @staticmethod
    def get_user_by_email(db: Session, email: str) -> Optional[User]:
        """
        Get a user by their email.

        Args:
            db: Database session
            email: User email

        Returns:
            User: User object if found, None otherwise
        """
        return DatabaseService.get_user_by_email(db, email)

    @staticmethod
    def update_user_password(db: Session, user_id: str, new_password: str) -> bool:
        """
        Update a user's password.

        Args:
            db: Database session
            user_id: User ID
            new_password: New password

        Returns:
            bool: True if successful, False otherwise
        """
        # Get the user
        user = DatabaseService.get_user_by_id(db, user_id)
        if not user:
            return False

        # Hash the new password
        hashed_password = hash_password(new_password)

        # Update the user's password
        user.hashed_password = hashed_password
        db.add(user)
        db.commit()
        db.refresh(user)

        return True

    @staticmethod
    def deactivate_user(db: Session, user_id: str) -> bool:
        """
        Deactivate a user account.

        Args:
            db: Database session
            user_id: User ID

        Returns:
            bool: True if successful, False otherwise
        """
        user = DatabaseService.get_user_by_id(db, user_id)
        if not user:
            return False

        user.is_active = False
        db.add(user)
        db.commit()
        db.refresh(user)

        return True

    @staticmethod
    def activate_user(db: Session, user_id: str) -> bool:
        """
        Activate a user account.

        Args:
            db: Database session
            user_id: User ID

        Returns:
            bool: True if successful, False otherwise
        """
        user = DatabaseService.get_user_by_id(db, user_id)
        if not user:
            return False

        user.is_active = True
        db.add(user)
        db.commit()
        db.refresh(user)

        return True

    @staticmethod
    def delete_user(db: Session, user_id: str) -> bool:
        """
        Delete a user account.

        Args:
            db: Database session
            user_id: User ID

        Returns:
            bool: True if successful, False otherwise
        """
        return DatabaseService.delete_user(db, user_id)

    @staticmethod
    def create_access_token_for_user(user: User) -> str:
        """
        Create an access token for a user.

        Args:
            user: User object

        Returns:
            str: Access token
        """
        token_data = {
            "sub": str(user.id),
            "email": user.email
        }
        return create_access_token(data=token_data)
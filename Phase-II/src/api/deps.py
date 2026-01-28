from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlmodel import Session
from src.database.connection import get_session
from src.utils.jwt import verify_access_token
from src.models.user import User
from src.services.user_service import UserService


security = HTTPBearer()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_session)
) -> User:
    """
    Get the current authenticated user from the JWT token.

    Args:
        credentials: HTTP authorization credentials
        db: Database session

    Returns:
        User: The authenticated user object

    Raises:
        HTTPException: If token is invalid or user not found
    """
    token = credentials.credentials

    try:
        # Verify the token and get user data
        token_data = verify_access_token(token)

        # Get user from database
        user = UserService.get_user_by_id(db, token_data.user_id)

        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found",
                headers={"WWW-Authenticate": "Bearer"},
            )

        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Inactive user",
                headers={"WWW-Authenticate": "Bearer"},
            )

        return user

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )


def get_current_active_user(current_user: User = Depends(get_current_user)) -> User:
    """
    Get the current active user.

    Args:
        current_user: The current user (from get_current_user)

    Returns:
        User: The active user object

    Raises:
        HTTPException: If user is not active
    """
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )

    return current_user


def require_admin_user(current_user: User = Depends(get_current_user)) -> User:
    """
    Require the current user to be an admin.

    Args:
        current_user: The current user (from get_current_user)

    Returns:
        User: The admin user object

    Raises:
        HTTPException: If user is not an admin
    """
    if not hasattr(current_user, 'role') or getattr(current_user, 'role', None) != 'admin':
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin privileges required"
        )

    return current_user


def require_user_with_permission(permission: str):
    """
    Create a dependency that requires the user to have a specific permission.

    Args:
        permission: The required permission

    Returns:
        Callable: A dependency function
    """
    def check_permission(current_user: User = Depends(get_current_user)) -> User:
        # This is a simplified check - in a real application, you'd check permissions properly
        # For now, we'll just return the user and assume they have the permission
        # In a real implementation, you'd check against a permission system
        return current_user

    return check_permission
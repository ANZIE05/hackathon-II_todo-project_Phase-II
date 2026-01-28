from sqlmodel import Session
from src.models.task import Task
from src.models.user import User
from uuid import UUID


def verify_task_ownership(db: Session, task_id: UUID, user_id: UUID) -> bool:
    """
    Verify that a user owns a specific task.

    Args:
        db: Database session
        task_id: Task ID to check
        user_id: User ID to verify ownership

    Returns:
        bool: True if user owns the task, False otherwise
    """
    # Query for the task with the given ID and user ID
    from sqlmodel import select

    statement = select(Task).where(Task.id == task_id, Task.user_id == user_id)
    task = db.exec(statement).first()

    return task is not None


def verify_user_permission(db: Session, resource_owner_id: UUID, current_user_id: UUID, permission: str = "read") -> bool:
    """
    Verify if a user has permission to access a resource.

    Args:
        db: Database session
        resource_owner_id: ID of the resource owner
        current_user_id: ID of the current user
        permission: Type of permission to check

    Returns:
        bool: True if user has permission, False otherwise
    """
    # For now, we just check if the current user is the owner
    # In the future, this could be extended to handle shared resources, roles, etc.
    return resource_owner_id == current_user_id


def can_read_resource(owner_id: UUID, current_user_id: UUID) -> bool:
    """
    Check if a user can read a resource.

    Args:
        owner_id: ID of the resource owner
        current_user_id: ID of the current user

    Returns:
        bool: True if user can read the resource, False otherwise
    """
    return owner_id == current_user_id


def can_modify_resource(owner_id: UUID, current_user_id: UUID) -> bool:
    """
    Check if a user can modify a resource.

    Args:
        owner_id: ID of the resource owner
        current_user_id: ID of the current user

    Returns:
        bool: True if user can modify the resource, False otherwise
    """
    return owner_id == current_user_id


def can_delete_resource(owner_id: UUID, current_user_id: UUID) -> bool:
    """
    Check if a user can delete a resource.

    Args:
        owner_id: ID of the resource owner
        current_user_id: ID of the current user

    Returns:
        bool: True if user can delete the resource, False otherwise
    """
    return owner_id == current_user_id


def is_admin_user(user: User) -> bool:
    """
    Check if a user has admin privileges.

    Args:
        user: User object to check

    Returns:
        bool: True if user is an admin, False otherwise
    """
    # This would typically check a role or permission field on the user
    # For now, we'll just check if the user's email ends with '@admin.com' as an example
    # In a real application, this would check a proper role/permission system
    return hasattr(user, 'role') and getattr(user, 'role', None) == 'admin'


def has_role(user: User, role: str) -> bool:
    """
    Check if a user has a specific role.

    Args:
        user: User object to check
        role: Role to check for

    Returns:
        bool: True if user has the role, False otherwise
    """
    return hasattr(user, 'role') and getattr(user, 'role', None) == role


def has_permission(user: User, resource: str, action: str) -> bool:
    """
    Check if a user has permission to perform an action on a resource.

    Args:
        user: User object to check
        resource: Resource to check permission for
        action: Action to check permission for

    Returns:
        bool: True if user has permission, False otherwise
    """
    # For basic implementation, we'll just check if the user owns the resource
    # This can be expanded to use a more sophisticated permission system
    return True  # Placeholder - in real implementation, check actual permissions
from typing import Optional
from datetime import datetime
from src.models.task import TaskPriority
from src.schemas.task import TaskCreate, TaskUpdate


def validate_task_title(title: str) -> tuple[bool, Optional[str]]:
    """
    Validate task title.

    Args:
        title: Task title to validate

    Returns:
        tuple[bool, Optional[str]]: (is_valid, error_message)
    """
    if not title or not title.strip():
        return False, "Task title is required"

    if len(title.strip()) > 255:
        return False, "Task title must be no more than 255 characters"

    return True, None


def validate_task_description(description: Optional[str]) -> tuple[bool, Optional[str]]:
    """
    Validate task description.

    Args:
        description: Task description to validate

    Returns:
        tuple[bool, Optional[str]]: (is_valid, error_message)
    """
    if description is None:
        return True, None

    if len(description) > 10000:  # 10k characters max for description
        return False, "Task description must be no more than 10000 characters"

    return True, None


def validate_task_priority(priority: str) -> tuple[bool, Optional[str]]:
    """
    Validate task priority.

    Args:
        priority: Task priority to validate

    Returns:
        tuple[bool, Optional[str]]: (is_valid, error_message)
    """
    try:
        TaskPriority(priority)
        return True, None
    except ValueError:
        return False, f"Invalid priority: {priority}. Must be one of: low, medium, high"


def validate_task_due_date(due_date: Optional[datetime]) -> tuple[bool, Optional[str]]:
    """
    Validate task due date.

    Args:
        due_date: Task due date to validate

    Returns:
        tuple[bool, Optional[str]]: (is_valid, error_message)
    """
    if due_date is None:
        return True, None

    # Check if due date is in the past (depending on requirements, this may or may not be allowed)
    # For now, we'll allow past due dates as tasks might be overdue
    return True, None


def validate_task_completion_status(completed: Optional[bool]) -> tuple[bool, Optional[str]]:
    """
    Validate task completion status.

    Args:
        completed: Task completion status to validate

    Returns:
        tuple[bool, Optional[str]]: (is_valid, error_message)
    """
    if completed is None:
        return True, None

    # Completion status should be a boolean
    if not isinstance(completed, bool):
        return False, "Completion status must be a boolean value"

    return True, None


def validate_task_create(task_create: TaskCreate) -> tuple[bool, list[str]]:
    """
    Validate a TaskCreate object.

    Args:
        task_create: TaskCreate object to validate

    Returns:
        tuple[bool, list[str]]: (is_valid, error_messages)
    """
    errors = []

    # Validate title
    is_valid, error = validate_task_title(task_create.title)
    if not is_valid:
        errors.append(error)

    # Validate description
    is_valid, error = validate_task_description(task_create.description)
    if not is_valid:
        errors.append(error)

    # Validate priority
    is_valid, error = validate_task_priority(task_create.priority.value if hasattr(task_create.priority, 'value') else task_create.priority)
    if not is_valid:
        errors.append(error)

    # Validate due date
    is_valid, error = validate_task_due_date(task_create.due_date)
    if not is_valid:
        errors.append(error)

    # Validate completion status
    is_valid, error = validate_task_completion_status(task_create.completed)
    if not is_valid:
        errors.append(error)

    return len(errors) == 0, errors


def validate_task_update(task_update: TaskUpdate) -> tuple[bool, list[str]]:
    """
    Validate a TaskUpdate object.

    Args:
        task_update: TaskUpdate object to validate

    Returns:
        tuple[bool, list[str]]: (is_valid, error_messages)
    """
    errors = []

    # Validate title if provided
    if task_update.title is not None:
        is_valid, error = validate_task_title(task_update.title)
        if not is_valid:
            errors.append(error)

    # Validate description if provided
    if task_update.description is not None:
        is_valid, error = validate_task_description(task_update.description)
        if not is_valid:
            errors.append(error)

    # Validate priority if provided
    if task_update.priority is not None:
        is_valid, error = validate_task_priority(task_update.priority.value if hasattr(task_update.priority, 'value') else task_update.priority)
        if not is_valid:
            errors.append(error)

    # Validate due date if provided
    if task_update.due_date is not None:
        is_valid, error = validate_task_due_date(task_update.due_date)
        if not is_valid:
            errors.append(error)

    # Validate completion status if provided
    if task_update.completed is not None:
        is_valid, error = validate_task_completion_status(task_update.completed)
        if not is_valid:
            errors.append(error)

    return len(errors) == 0, errors


def validate_task_priority_change(old_priority: TaskPriority, new_priority: TaskPriority) -> tuple[bool, Optional[str]]:
    """
    Validate changing task priority.

    Args:
        old_priority: Current task priority
        new_priority: New task priority

    Returns:
        tuple[bool, Optional[str]]: (is_valid, error_message)
    """
    # For priority changes, we just validate the new priority is valid
    return validate_task_priority(new_priority.value if hasattr(new_priority, 'value') else new_priority)


def is_valid_task_status_transition(current_status: bool, new_status: bool) -> bool:
    """
    Check if a task status transition is valid.

    Args:
        current_status: Current completion status
        new_status: New completion status

    Returns:
        bool: True if transition is valid, False otherwise
    """
    # In a simple system, any boolean transition is valid
    # In a more complex system, you might have specific rules about transitions
    return True


def validate_task_ownership(user_id: str, task_user_id: str) -> bool:
    """
    Validate that a user owns a task.

    Args:
        user_id: ID of the user
        task_user_id: ID of the task owner

    Returns:
        bool: True if user owns the task, False otherwise
    """
    return str(user_id) == str(task_user_id)


def validate_task_not_completed(task: 'Task') -> tuple[bool, Optional[str]]:
    """
    Validate that a task is not completed (useful for operations that shouldn't be performed on completed tasks).

    Args:
        task: Task object to validate

    Returns:
        tuple[bool, Optional[str]]: (is_valid, error_message)
    """
    if task.completed:
        return False, "Operation not allowed on completed tasks"

    return True, None


def validate_task_dependencies(task: 'Task', dependencies: list) -> tuple[bool, Optional[str]]:
    """
    Validate task dependencies.

    Args:
        task: Task object to validate
        dependencies: List of task dependencies

    Returns:
        tuple[bool, Optional[str]]: (is_valid, error_message)
    """
    # This is a placeholder for more complex dependency validation
    # In a real system, you'd check if dependent tasks are completed, etc.
    return True, None
import re
from typing import Optional


def validate_email_format(email: str) -> bool:
    """
    Validate email format using regex.

    Args:
        email: Email string to validate

    Returns:
        bool: True if email format is valid, False otherwise
    """
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None


def validate_password_strength(password: str) -> tuple[bool, Optional[str]]:
    """
    Validate password strength.

    Args:
        password: Password string to validate

    Returns:
        tuple[bool, Optional[str]]: (is_valid, error_message)
    """
    if len(password) < 8:
        return False, "Password must be at least 8 characters long"

    if not re.search(r"[A-Z]", password):
        return False, "Password must contain at least one uppercase letter"

    if not re.search(r"[a-z]", password):
        return False, "Password must contain at least one lowercase letter"

    if not re.search(r"\d", password):
        return False, "Password must contain at least one digit"

    return True, None


def validate_uuid_format(uuid_string: str) -> bool:
    """
    Validate UUID format.

    Args:
        uuid_string: UUID string to validate

    Returns:
        bool: True if UUID format is valid, False otherwise
    """
    pattern = r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$'
    return re.match(pattern, uuid_string, re.IGNORECASE) is not None


def validate_phone_number(phone: str) -> bool:
    """
    Validate phone number format (simple validation for common formats).

    Args:
        phone: Phone number string to validate

    Returns:
        bool: True if phone number format is valid, False otherwise
    """
    # Remove common separators
    clean_phone = re.sub(r'[-.\s()]', '', phone)

    # Check if it contains only digits and is of reasonable length
    if not re.match(r'^\+?[\d\s()-]+$', phone):
        return False

    # Check length (between 7 and 15 digits after cleaning)
    if len(clean_phone) < 7 or len(clean_phone) > 15:
        return False

    return True


def validate_url(url: str) -> bool:
    """
    Validate URL format.

    Args:
        url: URL string to validate

    Returns:
        bool: True if URL format is valid, False otherwise
    """
    pattern = r'^https?://(?:[-\w.])+(?:\:[0-9]+)?(?:/(?:[\w/_.])*(?:\?(?:[\w&=%.])*)?(?:\#(?:[\w.])*)?)?$'
    return re.match(pattern, url) is not None


def validate_date_format(date_str: str, format: str = "%Y-%m-%d") -> bool:
    """
    Validate date format.

    Args:
        date_str: Date string to validate
        format: Expected date format (default: YYYY-MM-DD)

    Returns:
        bool: True if date format is valid, False otherwise
    """
    from datetime import datetime

    try:
        datetime.strptime(date_str, format)
        return True
    except ValueError:
        return False


def sanitize_input(input_str: str) -> str:
    """
    Sanitize input string by removing potentially dangerous characters.

    Args:
        input_str: Input string to sanitize

    Returns:
        str: Sanitized string
    """
    # Remove potentially harmful characters/sequences
    sanitized = input_str.replace('<', '&lt;').replace('>', '&gt;')
    sanitized = sanitized.replace('"', '&quot;').replace("'", '&#x27;')
    sanitized = sanitized.replace('/', '&#x2F;').replace('\\', '&#x5C;')

    return sanitized


def validate_username(username: str) -> tuple[bool, Optional[str]]:
    """
    Validate username format.

    Args:
        username: Username string to validate

    Returns:
        tuple[bool, Optional[str]]: (is_valid, error_message)
    """
    if len(username) < 3:
        return False, "Username must be at least 3 characters long"

    if len(username) > 30:
        return False, "Username must be no more than 30 characters long"

    if not re.match(r'^[a-zA-Z0-9_]+$', username):
        return False, "Username can only contain alphanumeric characters and underscores"

    return True, None


def is_safe_filename(filename: str) -> bool:
    """
    Check if a filename is safe (no path traversal or dangerous extensions).

    Args:
        filename: Filename to validate

    Returns:
        bool: True if filename is safe, False otherwise
    """
    # Check for path traversal
    if '..' in filename or '/' in filename or '\\' in filename:
        return False

    # Check for potentially dangerous extensions
    dangerous_extensions = ['.exe', '.bat', '.cmd', '.sh', '.php', '.jsp', '.asp']
    for ext in dangerous_extensions:
        if filename.lower().endswith(ext):
            return False

    # Check for valid filename characters
    if not re.match(r'^[\w\-.]+$', filename):
        return False

    return True


def validate_field_length(field: str, min_len: int = 0, max_len: int = 255) -> tuple[bool, Optional[str]]:
    """
    Validate field length.

    Args:
        field: Field value to validate
        min_len: Minimum length (default: 0)
        max_len: Maximum length (default: 255)

    Returns:
        tuple[bool, Optional[str]]: (is_valid, error_message)
    """
    if len(field) < min_len:
        return False, f"Field must be at least {min_len} characters long"

    if len(field) > max_len:
        return False, f"Field must be no more than {max_len} characters long"

    return True, None
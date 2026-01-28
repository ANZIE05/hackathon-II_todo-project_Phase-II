from passlib.context import CryptContext
from typing import Union


# Create password context for hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    """
    Hash a password using bcrypt.

    Args:
        password: Plain text password

    Returns:
        str: Hashed password
    """
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a plain password against its hashed version.

    Args:
        plain_password: Plain text password
        hashed_password: Hashed password

    Returns:
        bool: True if passwords match, False otherwise
    """
    return pwd_context.verify(plain_password, hashed_password)


def is_hash_valid(hashed_password: str) -> bool:
    """
    Check if a hashed password is valid.

    Args:
        hashed_password: Hashed password to validate

    Returns:
        bool: True if valid, False otherwise
    """
    return pwd_context.identify_hash(hashed_password) is not None


def rehash_if_needed(hashed_password: str) -> Union[str, None]:
    """
    Check if a password needs to be rehashed (for algorithm updates).

    Args:
        hashed_password: Hashed password to check

    Returns:
        str: New hash if rehashing is needed, None otherwise
    """
    if pwd_context.needs_update(hashed_password):
        # Extract the plain password by prompting user (not possible here)
        # In practice, this would be handled differently
        return None
    return None


def get_password_strength(password: str) -> dict:
    """
    Analyze the strength of a password.

    Args:
        password: Password to analyze

    Returns:
        dict: Strength analysis results
    """
    import re

    score = 0
    feedback = []

    # Length check
    if len(password) >= 8:
        score += 1
    else:
        feedback.append("Password should be at least 8 characters long")

    # Complexity checks
    if re.search(r"[a-z]", password):
        score += 1
    else:
        feedback.append("Add lowercase letters")

    if re.search(r"[A-Z]", password):
        score += 1
    else:
        feedback.append("Add uppercase letters")

    if re.search(r"\d", password):
        score += 1
    else:
        feedback.append("Add numbers")

    if re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
        score += 1
    else:
        feedback.append("Add special characters")

    strength_levels = ["Very Weak", "Weak", "Fair", "Good", "Strong"]
    strength = strength_levels[min(score, 4)]

    return {
        "score": score,
        "strength": strength,
        "feedback": feedback
    }


def validate_password_requirements(password: str) -> tuple[bool, str]:
    """
    Validate password against requirements.

    Args:
        password: Password to validate

    Returns:
        tuple[bool, str]: (is_valid, error_message)
    """
    if len(password) < 8:
        return False, "Password must be at least 8 characters long"

    import re
    if not re.search(r"[A-Z]", password):
        return False, "Password must contain at least one uppercase letter"

    if not re.search(r"[a-z]", password):
        return False, "Password must contain at least one lowercase letter"

    if not re.search(r"\d", password):
        return False, "Password must contain at least one digit"

    return True, ""
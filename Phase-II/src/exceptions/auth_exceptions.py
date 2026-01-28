from fastapi import HTTPException, status
from typing import Optional


class AuthException(HTTPException):
    """
    Base authentication exception.
    """
    def __init__(self, detail: str = "Authentication error", headers: Optional[dict] = None):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=detail,
            headers=headers or {"WWW-Authenticate": "Bearer"}
        )


class InvalidCredentialsException(AuthException):
    """
    Exception raised when user provides invalid credentials.
    """
    def __init__(self, detail: str = "Invalid credentials"):
        super().__init__(detail=detail)


class UserNotFoundException(AuthException):
    """
    Exception raised when a user is not found.
    """
    def __init__(self, detail: str = "User not found"):
        super().__init__(detail=detail)


class UserInactiveException(AuthException):
    """
    Exception raised when a user account is inactive.
    """
    def __init__(self, detail: str = "User account is inactive"):
        super().__init__(detail=detail)


class TokenValidationException(HTTPException):
    """
    Exception raised when token validation fails.
    """
    def __init__(self, detail: str = "Could not validate credentials"):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=detail,
            headers={"WWW-Authenticate": "Bearer"}
        )


class ExpiredTokenException(TokenValidationException):
    """
    Exception raised when a token has expired.
    """
    def __init__(self, detail: str = "Token has expired"):
        super().__init__(detail=detail)


class InvalidTokenException(TokenValidationException):
    """
    Exception raised when a token is invalid.
    """
    def __init__(self, detail: str = "Invalid token"):
        super().__init__(detail=detail)


class InsufficientPermissionsException(HTTPException):
    """
    Exception raised when a user doesn't have sufficient permissions.
    """
    def __init__(self, detail: str = "Insufficient permissions"):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=detail
        )


class AccountLockedException(AuthException):
    """
    Exception raised when a user account is locked.
    """
    def __init__(self, detail: str = "Account is locked"):
        super().__init__(detail=detail)


class PasswordResetRequiredException(AuthException):
    """
    Exception raised when password reset is required.
    """
    def __init__(self, detail: str = "Password reset required"):
        super().__init__(detail=detail)


class TooManyLoginAttemptsException(HTTPException):
    """
    Exception raised when too many login attempts have been made.
    """
    def __init__(self, detail: str = "Too many login attempts. Account locked temporarily"):
        super().__init__(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=detail
        )


class EmailNotVerifiedException(AuthException):
    """
    Exception raised when user's email is not verified.
    """
    def __init__(self, detail: str = "Email not verified"):
        super().__init__(detail=detail)


class AccountDeactivatedException(AuthException):
    """
    Exception raised when user's account is deactivated.
    """
    def __init__(self, detail: str = "Account has been deactivated"):
        super().__init__(detail=detail)


class RegistrationClosedException(HTTPException):
    """
    Exception raised when registration is closed.
    """
    def __init__(self, detail: str = "Registration is currently closed"):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=detail
        )


class DuplicateEmailException(HTTPException):
    """
    Exception raised when trying to register with an email that already exists.
    """
    def __init__(self, detail: str = "Email already registered"):
        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            detail=detail
        )


def handle_auth_error(error_msg: str, status_code: int = status.HTTP_401_UNAUTHORIZED):
    """
    Helper function to handle authentication errors consistently.

    Args:
        error_msg: Error message
        status_code: HTTP status code

    Raises:
        HTTPException: With the specified status code and message
    """
    raise HTTPException(
        status_code=status_code,
        detail=error_msg,
        headers={"WWW-Authenticate": "Bearer"} if status_code == status.HTTP_401_UNAUTHORIZED else None
    )
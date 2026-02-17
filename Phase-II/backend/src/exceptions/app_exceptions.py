from typing import Optional, Dict, Any
from fastapi import HTTPException, status


class AppBaseException(Exception):
    """
    Base application exception class.
    """
    def __init__(
        self,
        message: str,
        error_code: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
        status_code: int = 500
    ):
        super().__init__(message)
        self.message = message
        self.error_code = error_code
        self.details = details or {}
        self.status_code = status_code


class ResourceNotFoundException(AppBaseException):
    """
    Exception raised when a requested resource is not found.
    """
    def __init__(self, resource_type: str, identifier: str):
        message = f"{resource_type.capitalize()} with identifier '{identifier}' not found"
        super().__init__(
            message=message,
            error_code="RESOURCE_NOT_FOUND",
            status_code=status.HTTP_404_NOT_FOUND
        )


class ValidationErrorException(AppBaseException):
    """
    Exception raised for validation errors.
    """
    def __init__(self, message: str, field_errors: Optional[Dict[str, str]] = None):
        super().__init__(
            message=message,
            error_code="VALIDATION_ERROR",
            details={"field_errors": field_errors} if field_errors else {},
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY
        )


class AuthenticationException(AppBaseException):
    """
    Exception raised for authentication errors.
    """
    def __init__(self, message: str = "Authentication failed"):
        super().__init__(
            message=message,
            error_code="AUTHENTICATION_ERROR",
            status_code=status.HTTP_401_UNAUTHORIZED
        )


class AuthorizationException(AppBaseException):
    """
    Exception raised for authorization errors.
    """
    def __init__(self, message: str = "Insufficient permissions"):
        super().__init__(
            message=message,
            error_code="AUTHORIZATION_ERROR",
            status_code=status.HTTP_403_FORBIDDEN
        )


class DuplicateResourceException(AppBaseException):
    """
    Exception raised when attempting to create a duplicate resource.
    """
    def __init__(self, resource_type: str, field: str, value: str):
        message = f"{resource_type.capitalize()} with {field} '{value}' already exists"
        super().__init__(
            message=message,
            error_code="DUPLICATE_RESOURCE",
            status_code=status.HTTP_409_CONFLICT
        )


class BusinessLogicException(AppBaseException):
    """
    Exception raised for business logic violations.
    """
    def __init__(self, message: str, error_code: Optional[str] = None):
        super().__init__(
            message=message,
            error_code=error_code or "BUSINESS_LOGIC_ERROR",
            status_code=status.HTTP_400_BAD_REQUEST
        )


class DatabaseException(AppBaseException):
    """
    Exception raised for database-related errors.
    """
    def __init__(self, message: str = "Database operation failed"):
        super().__init__(
            message=message,
            error_code="DATABASE_ERROR",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


class ExternalServiceException(AppBaseException):
    """
    Exception raised for external service errors.
    """
    def __init__(self, service_name: str, message: str = "External service error"):
        super().__init__(
            message=f"{service_name.title()} service error: {message}",
            error_code="EXTERNAL_SERVICE_ERROR",
            status_code=status.HTTP_502_BAD_GATEWAY
        )


class RateLimitException(AppBaseException):
    """
    Exception raised when rate limits are exceeded.
    """
    def __init__(self, message: str = "Rate limit exceeded"):
        super().__init__(
            message=message,
            error_code="RATE_LIMIT_EXCEEDED",
            status_code=status.HTTP_429_TOO_MANY_REQUESTS
        )


class DataIntegrityException(AppBaseException):
    """
    Exception raised for data integrity violations.
    """
    def __init__(self, message: str = "Data integrity violation"):
        super().__init__(
            message=message,
            error_code="DATA_INTEGRITY_ERROR",
            status_code=status.HTTP_400_BAD_REQUEST
        )


# HTTP Exception converters
def create_http_exception_from_app_exception(exc: AppBaseException) -> HTTPException:
    """
    Convert an AppBaseException to an HTTPException.

    Args:
        exc: The application exception to convert

    Returns:
        HTTPException: Converted HTTP exception
    """
    return HTTPException(
        status_code=exc.status_code,
        detail={
            "success": False,
            "error": exc.error_code,
            "message": exc.message,
            "details": exc.details
        }
    )
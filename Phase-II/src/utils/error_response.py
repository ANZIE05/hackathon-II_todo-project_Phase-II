from typing import Optional, Dict, Any
from fastapi import Request
from datetime import datetime
from src.schemas.error import ErrorResponse


def create_error_response(
    error: str,
    message: str,
    status_code: int,
    path: Optional[str] = None,
    details: Optional[Dict[str, Any]] = None,
    request: Optional[Request] = None
) -> dict:
    """
    Create a standardized error response.

    Args:
        error: Error code/type
        message: Human-readable error message
        status_code: HTTP status code
        path: Request path (optional, can be derived from request)
        details: Additional error details (optional)
        request: FastAPI request object (optional, to extract path)

    Returns:
        dict: Standardized error response
    """
    if request and not path:
        path = str(request.url)

    return {
        "success": False,
        "error": error,
        "message": message,
        "timestamp": datetime.now().isoformat(),
        "path": path,
        "status_code": status_code,
        "details": details or {}
    }


def create_validation_error_response(
    message: str,
    field_errors: Optional[Dict[str, Any]] = None,
    path: Optional[str] = None,
    request: Optional[Request] = None
) -> dict:
    """
    Create a standardized validation error response.

    Args:
        message: Human-readable error message
        field_errors: Dictionary of field-specific validation errors
        path: Request path (optional, can be derived from request)
        request: FastAPI request object (optional, to extract path)

    Returns:
        dict: Standardized validation error response
    """
    return create_error_response(
        error="VALIDATION_ERROR",
        message=message,
        status_code=422,
        path=path,
        details=field_errors,
        request=request
    )


def create_not_found_error(
    resource_type: str,
    identifier: str,
    path: Optional[str] = None,
    request: Optional[Request] = None
) -> dict:
    """
    Create a standardized not found error response.

    Args:
        resource_type: Type of resource that wasn't found
        identifier: Identifier of the resource that wasn't found
        path: Request path (optional, can be derived from request)
        request: FastAPI request object (optional, to extract path)

    Returns:
        dict: Standardized not found error response
    """
    message = f"{resource_type.capitalize()} with identifier '{identifier}' not found"
    return create_error_response(
        error="RESOURCE_NOT_FOUND",
        message=message,
        status_code=404,
        path=path,
        request=request
    )


def create_forbidden_error(
    message: str = "Access denied",
    path: Optional[str] = None,
    request: Optional[Request] = None
) -> dict:
    """
    Create a standardized forbidden error response.

    Args:
        message: Human-readable error message
        path: Request path (optional, can be derived from request)
        request: FastAPI request object (optional, to extract path)

    Returns:
        dict: Standardized forbidden error response
    """
    return create_error_response(
        error="FORBIDDEN",
        message=message,
        status_code=403,
        path=path,
        request=request
    )


def create_unauthorized_error(
    message: str = "Authentication required",
    path: Optional[str] = None,
    request: Optional[Request] = None
) -> dict:
    """
    Create a standardized unauthorized error response.

    Args:
        message: Human-readable error message
        path: Request path (optional, can be derived from request)
        request: FastAPI request object (optional, to extract path)

    Returns:
        dict: Standardized unauthorized error response
    """
    return create_error_response(
        error="UNAUTHORIZED",
        message=message,
        status_code=401,
        path=path,
        request=request
    )


def create_duplicate_resource_error(
    resource_type: str,
    field: str,
    value: str,
    path: Optional[str] = None,
    request: Optional[Request] = None
) -> dict:
    """
    Create a standardized duplicate resource error response.

    Args:
        resource_type: Type of resource that already exists
        field: Field that caused the duplication
        value: Value that already exists
        path: Request path (optional, can be derived from request)
        request: FastAPI request object (optional, to extract path)

    Returns:
        dict: Standardized duplicate resource error response
    """
    message = f"{resource_type.capitalize()} with {field} '{value}' already exists"
    return create_error_response(
        error="DUPLICATE_RESOURCE",
        message=message,
        status_code=409,
        path=path,
        request=request
    )


def create_internal_error(
    message: str = "Internal server error",
    path: Optional[str] = None,
    request: Optional[Request] = None
) -> dict:
    """
    Create a standardized internal server error response.

    Args:
        message: Human-readable error message
        path: Request path (optional, can be derived from request)
        request: FastAPI request object (optional, to extract path)

    Returns:
        dict: Standardized internal server error response
    """
    return create_error_response(
        error="INTERNAL_SERVER_ERROR",
        message=message,
        status_code=500,
        path=path,
        request=request
    )


def create_bad_request_error(
    message: str,
    path: Optional[str] = None,
    request: Optional[Request] = None
) -> dict:
    """
    Create a standardized bad request error response.

    Args:
        message: Human-readable error message
        path: Request path (optional, can be derived from request)
        request: FastAPI request object (optional, to extract path)

    Returns:
        dict: Standardized bad request error response
    """
    return create_error_response(
        error="BAD_REQUEST",
        message=message,
        status_code=400,
        path=path,
        request=request
    )


def create_rate_limit_error(
    message: str = "Rate limit exceeded",
    path: Optional[str] = None,
    request: Optional[Request] = None
) -> dict:
    """
    Create a standardized rate limit error response.

    Args:
        message: Human-readable error message
        path: Request path (optional, can be derived from request)
        request: FastAPI request object (optional, to extract path)

    Returns:
        dict: Standardized rate limit error response
    """
    return create_error_response(
        error="RATE_LIMIT_EXCEEDED",
        message=message,
        status_code=429,
        path=path,
        request=request
    )
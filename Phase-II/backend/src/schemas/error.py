from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime


class ErrorResponse(BaseModel):
    """
    Standard error response schema for all API endpoints.
    """
    success: bool = False
    error: str
    message: str
    timestamp: datetime
    path: Optional[str] = None
    status_code: int
    details: Optional[Dict[str, Any]] = None

    class Config:
        json_encoders = {
            datetime: lambda dt: dt.isoformat()
        }


class ValidationErrorResponse(ErrorResponse):
    """
    Error response schema specifically for validation errors.
    """
    details: Dict[str, Any]  # Contains field-specific validation errors


class FieldValidationError(BaseModel):
    """
    Schema for individual field validation errors.
    """
    field: str
    message: str
    error_type: Optional[str] = None


class ValidationErrorResponse(BaseModel):
    """
    Schema for validation error responses with field-specific details.
    """
    success: bool = False
    error: str = "validation_error"
    message: str
    timestamp: datetime
    path: Optional[str] = None
    status_code: int = 422
    details: Dict[str, Any]

    class Config:
        json_encoders = {
            datetime: lambda dt: dt.isoformat()
        }
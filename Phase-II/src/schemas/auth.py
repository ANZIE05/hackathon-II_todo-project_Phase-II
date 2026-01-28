from pydantic import BaseModel, validator
from typing import Optional
from datetime import datetime
import re
from sqlmodel import SQLModel


class RegisterRequest(SQLModel):
    """
    Schema for user registration request.
    """
    email: str
    password: str
    confirm_password: str

    @validator('password')
    def validate_password(cls, v):
        """
        Validate password strength.

        Args:
            v: Password value

        Returns:
            str: Validated password

        Raises:
            ValueError: If password doesn't meet requirements
        """
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')

        # Check for at least one uppercase, lowercase, digit
        if not re.search(r'[A-Z]', v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not re.search(r'[a-z]', v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not re.search(r'\d', v):
            raise ValueError('Password must contain at least one digit')

        return v

    @validator('confirm_password')
    def passwords_match(cls, v, values):
        """
        Validate that passwords match.

        Args:
            v: Confirm password value
            values: Other field values

        Returns:
            str: Validated confirm password

        Raises:
            ValueError: If passwords don't match
        """
        if 'password' in values and v != values['password']:
            raise ValueError('Passwords do not match')
        return v


class LoginRequest(SQLModel):
    """
    Schema for user login request.
    """
    email: str
    password: str


class AuthResponse(BaseModel):
    """
    Schema for authentication response.
    """
    success: bool
    token: str
    user: dict


class TokenData(BaseModel):
    """
    Schema for token data.
    """
    user_id: str
    email: str
    exp: Optional[datetime] = None


class Token(BaseModel):
    """
    Schema for JWT token.
    """
    access_token: str
    token_type: str = "bearer"


class RefreshTokenRequest(BaseModel):
    """
    Schema for token refresh request.
    """
    refresh_token: str


class RefreshTokenResponse(BaseModel):
    """
    Schema for token refresh response.
    """
    access_token: str
    token_type: str = "bearer"
    expires_in: int
from datetime import datetime, timedelta
from typing import Optional, Union
import jwt
from src.config.settings import settings
from src.schemas.auth import TokenData
from fastapi import HTTPException, status
from jose import JWTError


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Create an access token with the provided data.

    Args:
        data: Data to encode in the token
        expires_delta: Optional expiration time delta

    Returns:
        str: Encoded JWT token
    """
    to_encode = data.copy()

    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        # Use default expiration from settings (convert hours to timedelta)
        expire = datetime.utcnow() + timedelta(hours=settings.JWT_EXPIRATION_HOURS)

    to_encode.update({"exp": expire})

    encoded_jwt = jwt.encode(
        to_encode,
        settings.BETTER_AUTH_SECRET,
        algorithm="HS256"
    )
    return encoded_jwt


def create_refresh_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Create a refresh token with the provided data.

    Args:
        data: Data to encode in the token
        expires_delta: Optional expiration time delta

    Returns:
        str: Encoded refresh token
    """
    to_encode = data.copy()

    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        # Refresh tokens typically have longer expiration (e.g., 7 days)
        expire = datetime.utcnow() + timedelta(days=7)

    to_encode.update({"exp": expire, "type": "refresh"})

    encoded_jwt = jwt.encode(
        to_encode,
        settings.BETTER_AUTH_SECRET,
        algorithm="HS256"
    )
    return encoded_jwt


def verify_token(token: str, credentials_exception: Optional[HTTPException] = None) -> TokenData:
    """
    Verify a JWT token and return the token data.

    Args:
        token: JWT token to verify
        credentials_exception: Exception to raise if verification fails

    Returns:
        TokenData: Decoded token data

    Raises:
        HTTPException: If token is invalid or expired
    """
    if credentials_exception is None:
        credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        payload = jwt.decode(
            token,
            settings.BETTER_AUTH_SECRET,
            algorithms=["HS256"]
        )
        user_id: str = payload.get("sub")
        email: str = payload.get("email")

        if user_id is None or email is None:
            raise credentials_exception

        token_data = TokenData(user_id=user_id, email=email)
    except JWTError:
        raise credentials_exception

    return token_data


def verify_access_token(token: str) -> TokenData:
    """
    Verify an access token specifically.

    Args:
        token: Access token to verify

    Returns:
        TokenData: Decoded token data
    """
    return verify_token(token)


def verify_refresh_token(token: str) -> TokenData:
    """
    Verify a refresh token specifically.

    Args:
        token: Refresh token to verify

    Returns:
        TokenData: Decoded token data
    """
    try:
        payload = jwt.decode(
            token,
            settings.BETTER_AUTH_SECRET,
            algorithms=["HS256"]
        )

        # Check if it's a refresh token
        token_type = payload.get("type")
        if token_type != "refresh":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token type",
                headers={"WWW-Authenticate": "Bearer"},
            )

        user_id: str = payload.get("sub")
        email: str = payload.get("email")

        if user_id is None or email is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )

        token_data = TokenData(user_id=user_id, email=email)
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate refresh token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return token_data


def decode_token_payload(token: str) -> dict:
    """
    Decode the payload of a token without verifying it.
    Use this only for debugging purposes!

    Args:
        token: JWT token to decode

    Returns:
        dict: Decoded token payload
    """
    return jwt.decode(
        token,
        settings.BETTER_AUTH_SECRET,
        algorithms=["HS256"],
        options={"verify_signature": False}
    )


def is_token_expired(token: str) -> bool:
    """
    Check if a token is expired without raising an exception.

    Args:
        token: JWT token to check

    Returns:
        bool: True if token is expired, False otherwise
    """
    try:
        payload = jwt.decode(
            token,
            settings.BETTER_AUTH_SECRET,
            algorithms=["HS256"]
        )
        exp = payload.get("exp")
        if exp is None:
            return True

        return datetime.fromtimestamp(exp) < datetime.utcnow()
    except JWTError:
        return True


def get_token_expiration_time(token: str) -> Optional[datetime]:
    """
    Get the expiration time of a token.

    Args:
        token: JWT token to check

    Returns:
        Optional[datetime]: Expiration time if token is valid, None otherwise
    """
    try:
        payload = jwt.decode(
            token,
            settings.BETTER_AUTH_SECRET,
            algorithms=["HS256"]
        )
        exp = payload.get("exp")
        if exp is None:
            return None

        return datetime.fromtimestamp(exp)
    except JWTError:
        return None


def refresh_access_token(refresh_token: str) -> str:
    """
    Generate a new access token using a refresh token.

    Args:
        refresh_token: Valid refresh token

    Returns:
        str: New access token
    """
    # Verify the refresh token
    token_data = verify_refresh_token(refresh_token)

    # Create new access token with user data
    new_token_data = {
        "sub": token_data.user_id,
        "email": token_data.email
    }

    return create_access_token(new_token_data)
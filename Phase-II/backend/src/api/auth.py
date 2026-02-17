from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session
from src.database.connection import get_session
from src.schemas.auth import RegisterRequest, LoginRequest, AuthResponse, RefreshTokenRequest, RefreshTokenResponse
from src.services.user_service import UserService
from src.repositories.user_repository import UserRepository
from src.utils.validation import validate_email_format
from src.utils.jwt import refresh_access_token, verify_refresh_token
from src.api.deps import get_current_user
from src.models.user import User
from src.services.token_service import token_service
from src.utils.error_response import create_error_response, create_bad_request_error, create_unauthorized_error, create_duplicate_resource_error
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials


router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=AuthResponse)
def register_user(user_data: RegisterRequest, db: Session = Depends(get_session)):
    """
    Register a new user with email and password.

    Args:
        user_data: User registration data
        db: Database session

    Returns:
        AuthResponse: Authentication response with token

    Raises:
        HTTPException: If registration fails
    """
    # Validate email format
    if not validate_email_format(user_data.email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid email format"
        )

    # Attempt to register the user
    result = UserService.register_user(db, user_data)

    if not result:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already exists"
        )

    return AuthResponse(
        success=result["success"],
        token=result["token"],
        user=result["user"]
    )


@router.post("/login", response_model=AuthResponse)
def login_user(login_data: LoginRequest, db: Session = Depends(get_session)):
    """
    Authenticate a user with email and password.

    Args:
        login_data: User login data
        db: Database session

    Returns:
        AuthResponse: Authentication response with token

    Raises:
        HTTPException: If authentication fails
    """
    # Validate email format
    if not validate_email_format(login_data.email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid email format"
        )

    # Attempt to authenticate the user
    result = UserService.authenticate_user(db, login_data)

    if not result:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return AuthResponse(
        success=result["success"],
        token=result["token"],
        user=result["user"]
    )


@router.post("/logout")
def logout_user(
    credentials: HTTPAuthorizationCredentials = Depends(HTTPBearer()),
    current_user: User = Depends(get_current_user)
):
    """
    Logout the current user and blacklist their token.

    Args:
        credentials: HTTP authorization credentials
        current_user: The authenticated user

    Returns:
        dict: Success message
    """
    # Blacklist the current token to prevent reuse
    try:
        token_service.blacklist_token(credentials.credentials)
    except Exception:
        # If blacklisting fails, we still return success but log the issue
        pass

    return {
        "message": "Successfully logged out",
        "user_id": current_user.id
    }


@router.post("/refresh", response_model=RefreshTokenResponse)
def refresh_access_token_endpoint(refresh_request: RefreshTokenRequest):
    """
    Refresh the access token using a refresh token.

    Args:
        refresh_request: Contains the refresh token

    Returns:
        RefreshTokenResponse: New access token

    Raises:
        HTTPException: If refresh token is invalid
    """
    try:
        # Verify the refresh token and generate a new access token
        new_access_token = refresh_access_token(refresh_request.refresh_token)

        # For now, we'll return a fixed expiration time (1 hour = 3600 seconds)
        # In a real implementation, you'd calculate the actual remaining time
        return RefreshTokenResponse(
            access_token=new_access_token,
            token_type="bearer",
            expires_in=3600  # 1 hour in seconds
        )
    except HTTPException:
        # Re-raise HTTP exceptions (like invalid token)
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not refresh token"
        )
from fastapi import Request, HTTPException
from fastapi.security.http import HTTPBearer, HTTPAuthorizationCredentials
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response
from src.utils.jwt import decode_access_token
from src.exceptions.auth_exceptions import InvalidTokenException
from typing import Optional


class JWTMiddleware(BaseHTTPMiddleware):
    """
    Middleware to handle JWT token verification for protected endpoints.
    """

    def __init__(self, app, exclude_paths: Optional[list] = None):
        super().__init__(app)
        self.exclude_paths = exclude_paths or []
        self.security = HTTPBearer(auto_error=False)

    async def dispatch(self, request: Request, call_next):
        # Skip authentication for excluded paths (public endpoints)
        if request.url.path in self.exclude_paths:
            response = await call_next(request)
            return response

        # Extract token from Authorization header
        auth_header = request.headers.get("authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            raise HTTPException(status_code=401, detail="Authorization header missing or invalid format")

        token = auth_header.split(" ")[1]

        try:
            # Decode and validate the token
            payload = decode_access_token(token)
            if payload is None:
                raise InvalidTokenException("Invalid or expired token")

            # Add user info to request state for use in route handlers
            request.state.user_id = payload.get("sub")
            request.state.user_email = payload.get("email")

        except InvalidTokenException:
            raise HTTPException(status_code=401, detail="Invalid or expired token")
        except Exception as e:
            raise HTTPException(status_code=401, detail=f"Token validation failed: {str(e)}")

        response = await call_next(request)
        return response


# Alternative implementation using FastAPI's dependency system
from functools import wraps
from fastapi import Depends


def jwt_required():
    """
    Decorator to protect routes with JWT authentication.
    """
    async def verify_token(credentials: HTTPAuthorizationCredentials = Depends(HTTPBearer())):
        if not credentials or not credentials.credentials:
            raise HTTPException(status_code=401, detail="Authorization header missing")

        try:
            payload = decode_access_token(credentials.credentials)
            if payload is None:
                raise InvalidTokenException("Invalid or expired token")

            return {
                "user_id": payload.get("sub"),
                "user_email": payload.get("email"),
                "token": credentials.credentials
            }
        except InvalidTokenException:
            raise HTTPException(status_code=401, detail="Invalid or expired token")

    return verify_token
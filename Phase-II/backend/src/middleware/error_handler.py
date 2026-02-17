from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.exceptions import HTTPException as StarletteHTTPException
from datetime import datetime
import traceback
import logging
from typing import Optional

from src.exceptions.app_exceptions import (
    AppBaseException,
    ResourceNotFoundException,
    ValidationErrorException,
    AuthenticationException,
    AuthorizationException,
    DuplicateResourceException,
    BusinessLogicException,
    DatabaseException,
    ExternalServiceException,
    RateLimitException,
    DataIntegrityException
)


logger = logging.getLogger(__name__)


class ErrorHandlerMiddleware(BaseHTTPMiddleware):
    """
    Middleware to handle exceptions and return standardized error responses.
    """

    async def dispatch(self, request: Request, call_next):
        try:
            response = await call_next(request)

            # Handle cases where an exception was caught by FastAPI but not converted to response
            if isinstance(response, JSONResponse) and response.status_code >= 400:
                # If the response is already an error response, we might want to standardize it
                pass

            return response

        except HTTPException as http_exc:
            # Handle FastAPI HTTPExceptions
            return await self.handle_http_exception(request, http_exc)

        except StarletteHTTPException as starlette_exc:
            # Handle Starlette HTTPExceptions
            return await self.handle_starlette_http_exception(request, starlette_exc)

        except AppBaseException as app_exc:
            # Handle custom application exceptions
            return await self.handle_app_exception(request, app_exc)

        except Exception as exc:
            # Handle unexpected exceptions
            return await self.handle_unexpected_exception(request, exc)


    async def handle_http_exception(self, request: Request, exc: HTTPException):
        """
        Handle FastAPI HTTP exceptions and return standardized error response.
        """
        logger.error(f"HTTP Exception: {exc.detail}", exc_info=True)

        # Extract error details from the exception
        error_detail = exc.detail
        error_code = "UNKNOWN_ERROR"
        message = "An unknown error occurred"
        details = {}

        # Try to parse the error detail if it's a dictionary
        if isinstance(error_detail, dict):
            message = error_detail.get("message", str(exc.detail))
            error_code = error_detail.get("error", error_code)
            details = error_detail.get("details", {})
        elif isinstance(error_detail, str):
            message = error_detail
        else:
            message = str(error_detail)

        error_response = {
            "success": False,
            "error": error_code,
            "message": message,
            "timestamp": datetime.now().isoformat(),
            "path": str(request.url),
            "status_code": exc.status_code,
            "details": details
        }

        return JSONResponse(
            status_code=exc.status_code,
            content=error_response
        )


    async def handle_starlette_http_exception(self, request: Request, exc: StarletteHTTPException):
        """
        Handle Starlette HTTP exceptions and return standardized error response.
        """
        logger.error(f"Starlette HTTP Exception: {exc.detail}", exc_info=True)

        error_response = {
            "success": False,
            "error": "STARLETTE_ERROR",
            "message": exc.detail,
            "timestamp": datetime.now().isoformat(),
            "path": str(request.url),
            "status_code": exc.status_code,
            "details": {}
        }

        return JSONResponse(
            status_code=exc.status_code,
            content=error_response
        )


    async def handle_app_exception(self, request: Request, exc: AppBaseException):
        """
        Handle custom application exceptions and return standardized error response.
        """
        logger.error(f"App Exception: {exc.message}", exc_info=True)

        error_response = {
            "success": False,
            "error": exc.error_code or "APPLICATION_ERROR",
            "message": exc.message,
            "timestamp": datetime.now().isoformat(),
            "path": str(request.url),
            "status_code": exc.status_code,
            "details": exc.details
        }

        return JSONResponse(
            status_code=exc.status_code,
            content=error_response
        )


    async def handle_unexpected_exception(self, request: Request, exc: Exception):
        """
        Handle unexpected exceptions and return a generic error response.
        """
        logger.error(f"Unexpected error: {str(exc)}", exc_info=True)

        # Log the full traceback for debugging
        tb_str = traceback.format_exception(type(exc), exc, exc.__traceback__)
        logger.error("Full traceback:\n" + "".join(tb_str))

        error_response = {
            "success": False,
            "error": "INTERNAL_SERVER_ERROR",
            "message": "An internal server error occurred",
            "timestamp": datetime.now().isoformat(),
            "path": str(request.url),
            "status_code": 500,
            "details": {}
        }

        return JSONResponse(
            status_code=500,
            content=error_response
        )


# Convenience function to register error handlers
def register_error_handlers(app):
    """
    Register error handlers for the FastAPI application.

    Args:
        app: FastAPI application instance
    """
    # Register handler for 422 validation errors (they are handled differently by FastAPI)
    @app.exception_handler(422)
    async def validation_exception_handler(request: Request, exc: HTTPException):
        return await ErrorHandlerMiddleware(None).handle_http_exception(request, exc)

    # Register handler for 404 not found errors
    @app.exception_handler(404)
    async def not_found_exception_handler(request: Request, exc: HTTPException):
        return await ErrorHandlerMiddleware(None).handle_http_exception(request, exc)

    # Register handler for 500 internal server errors
    @app.exception_handler(500)
    async def internal_exception_handler(request: Request, exc: HTTPException):
        return await ErrorHandlerMiddleware(None).handle_http_exception(request, exc)
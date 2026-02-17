"""
API Version 1 Module

This module defines the first version of the API, establishing the initial
contract between the frontend and backend applications. All endpoints in this
version follow RESTful principles and use consistent response formats.
"""

from fastapi import APIRouter
from ..auth import router as auth_router
from ..tasks import router as tasks_router
from ..health import router as health_router


# Create API v1 router
api_v1_router = APIRouter(prefix="/v1")


# Include all v1 endpoints
api_v1_router.include_router(auth_router, prefix="/auth", tags=["Authentication"])
api_v1_router.include_router(tasks_router, prefix="/tasks", tags=["Tasks"])
api_v1_router.include_router(health_router, prefix="/health", tags=["Health"])


def get_api_v1_router():
    """
    Get the API v1 router instance.

    Returns:
        APIRouter: Configured API router for version 1
    """
    return api_v1_router


# For backward compatibility, expose the individual routers
__all__ = [
    "api_v1_router",
    "auth_router",
    "tasks_router",
    "health_router",
    "get_api_v1_router"
]
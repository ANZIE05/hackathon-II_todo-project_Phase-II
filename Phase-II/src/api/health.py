from fastapi import APIRouter, Depends
from typing import Dict, Any
from datetime import datetime
from sqlalchemy import text
from sqlmodel import Session
from src.database.connection import get_session
from src.config.settings import settings


router = APIRouter(tags=["Health"])


@router.get("/health", response_model=Dict[str, Any])
def health_check():
    """
    Basic health check endpoint to verify the application is running.

    Returns:
        Dict[str, Any]: Health status information
    """
    return {
        "status": "healthy",
        "service": "todo-backend",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0",
        "environment": settings.ENVIRONMENT
    }


@router.get("/health/database", response_model=Dict[str, Any])
def database_health_check(db: Session = Depends(get_session)):
    """
    Database health check endpoint to verify database connectivity.

    Args:
        db: Database session

    Returns:
        Dict[str, Any]: Database health status information
    """
    try:
        # Execute a simple query to test database connectivity
        result = db.exec(text("SELECT 1"))
        db_connected = True
        db_status = "connected"
    except Exception as e:
        db_connected = False
        db_status = f"connection failed: {str(e)}"

    return {
        "status": "healthy" if db_connected else "unhealthy",
        "service": "database",
        "connected": db_connected,
        "timestamp": datetime.now().isoformat(),
        "details": db_status
    }


@router.get("/health/ready", response_model=Dict[str, Any])
def readiness_check():
    """
    Readiness check endpoint to verify the application is ready to serve traffic.

    Returns:
        Dict[str, Any]: Readiness status information
    """
    # In a real application, you might check for:
    # - Database connectivity
    # - External service availability
    # - Configuration validity

    # For now, we'll just return healthy
    return {
        "status": "ready",
        "service": "todo-backend",
        "timestamp": datetime.now().isoformat(),
        "ready": True
    }


@router.get("/health/live", response_model=Dict[str, Any])
def liveness_check():
    """
    Liveness check endpoint to verify the application is alive and responsive.

    Returns:
        Dict[str, Any]: Liveness status information
    """
    return {
        "status": "alive",
        "service": "todo-backend",
        "timestamp": datetime.now().isoformat(),
        "alive": True
    }


# Include the router in the main application
def include_router(app):
    """
    Include health check routes in the main application.

    Args:
        app: FastAPI application instance
    """
    app.include_router(router, prefix="/api")


# Export the router directly for versioned APIs
__all__ = ["router"]
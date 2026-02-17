"""
Monitoring endpoints for the Todo Application Backend.
Provides metrics and health information for system monitoring.
"""

from fastapi import APIRouter, Depends
from typing import Dict, Any, List
import psutil
import time
import os
from datetime import datetime
from sqlalchemy import text
from sqlmodel import Session
from src.database.connection import get_session
from src.models.user import User
from src.models.task import Task
from src.config.settings import settings


router = APIRouter(prefix="/monitoring", tags=["Monitoring"])


@router.get("/metrics")
def get_metrics(db: Session = Depends(get_session)) -> Dict[str, Any]:
    """
    Get application metrics for monitoring.

    Args:
        db: Database session

    Returns:
        Dict[str, Any]: Metrics data
    """
    metrics = {}

    # System metrics
    metrics["system"] = {
        "cpu_percent": psutil.cpu_percent(interval=1),
        "memory_percent": psutil.virtual_memory().percent,
        "disk_usage_percent": psutil.disk_usage('/').percent,
        "uptime_seconds": time.time() - getattr(getattr(get_metrics, '__wrapped__', get_metrics), '_start_time', time.time()),
    }

    # Process metrics
    process = psutil.Process(os.getpid())
    metrics["process"] = {
        "memory_mb": process.memory_info().rss / 1024 / 1024,
        "num_threads": process.num_threads(),
        "num_fds": process.num_fds() if os.name != 'nt' else 0,  # Not available on Windows
    }

    # Application metrics
    try:
        # Count users
        user_count = db.exec(text("SELECT COUNT(*) FROM user")).one()[0]
        metrics["users"] = {"total": user_count}

        # Count tasks
        task_count = db.exec(text("SELECT COUNT(*) FROM task")).one()[0]
        metrics["tasks"] = {"total": task_count}

        # Recent activity (last 24 hours)
        from datetime import datetime, timedelta
        yesterday = datetime.now() - timedelta(days=1)

        recent_users = db.exec(
            text("SELECT COUNT(*) FROM user WHERE created_at > :yesterday")
        ).bindparams(yesterday=yesterday).one()[0]
        metrics["users"]["recent"] = recent_users

        recent_tasks = db.exec(
            text("SELECT COUNT(*) FROM task WHERE created_at > :yesterday")
        ).bindparams(yesterday=yesterday).one()[0]
        metrics["tasks"]["recent"] = recent_tasks

    except Exception as e:
        metrics["database_error"] = str(e)

    # Application info
    metrics["app"] = {
        "version": "1.0.0",
        "environment": settings.ENVIRONMENT,
        "debug": settings.DEBUG,
        "timestamp": datetime.now().isoformat(),
    }

    return metrics


@router.get("/status")
def get_status() -> Dict[str, Any]:
    """
    Get application status information.

    Returns:
        Dict[str, Any]: Status information
    """
    return {
        "status": "operational",
        "service": "todo-backend",
        "version": "1.0.0",
        "environment": settings.ENVIRONMENT,
        "healthy": True,
        "timestamp": datetime.now().isoformat(),
        "dependencies": {
            "database": "connected",
            "redis": "connected" if settings.REDIS_URL else "not configured",
        }
    }


@router.get("/health/extended")
def extended_health_check(db: Session = Depends(get_session)) -> Dict[str, Any]:
    """
    Extended health check that verifies all system components.

    Args:
        db: Database session

    Returns:
        Dict[str, Any]: Extended health status
    """
    health_status = {
        "overall_status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "checks": {}
    }

    # Database check
    try:
        db_result = db.exec(text("SELECT 1")).one()
        health_status["checks"]["database"] = {
            "status": "healthy",
            "message": "Connected and responsive"
        }
    except Exception as e:
        health_status["checks"]["database"] = {
            "status": "unhealthy",
            "message": f"Database error: {str(e)}"
        }
        health_status["overall_status"] = "unhealthy"

    # Memory check
    memory_percent = psutil.virtual_memory().percent
    if memory_percent > 90:
        health_status["checks"]["memory"] = {
            "status": "degraded",
            "message": f"High memory usage: {memory_percent}%"
        }
        if health_status["overall_status"] == "healthy":
            health_status["overall_status"] = "degraded"
    elif memory_percent > 95:
        health_status["checks"]["memory"] = {
            "status": "unhealthy",
            "message": f"Critical memory usage: {memory_percent}%"
        }
        health_status["overall_status"] = "unhealthy"
    else:
        health_status["checks"]["memory"] = {
            "status": "healthy",
            "message": f"Memory usage: {memory_percent}%"
        }

    # CPU check
    cpu_percent = psutil.cpu_percent(interval=1)
    if cpu_percent > 90:
        health_status["checks"]["cpu"] = {
            "status": "degraded",
            "message": f"High CPU usage: {cpu_percent}%"
        }
        if health_status["overall_status"] == "healthy":
            health_status["overall_status"] = "degraded"
    elif cpu_percent > 95:
        health_status["checks"]["cpu"] = {
            "status": "unhealthy",
            "message": f"Critical CPU usage: {cpu_percent}%"
        }
        health_status["overall_status"] = "unhealthy"
    else:
        health_status["checks"]["cpu"] = {
            "status": "healthy",
            "message": f"CPU usage: {cpu_percent}%"
        }

    # Disk space check
    disk_percent = psutil.disk_usage('/').percent
    if disk_percent > 90:
        health_status["checks"]["disk"] = {
            "status": "degraded",
            "message": f"Low disk space: {disk_percent}% used"
        }
        if health_status["overall_status"] == "healthy":
            health_status["overall_status"] = "degraded"
    elif disk_percent > 95:
        health_status["checks"]["disk"] = {
            "status": "unhealthy",
            "message": f"Critical disk space: {disk_percent}% used"
        }
        health_status["overall_status"] = "unhealthy"
    else:
        health_status["checks"]["disk"] = {
            "status": "healthy",
            "message": f"Disk usage: {disk_percent}%"
        }

    return health_status


@router.get("/dependencies")
def get_dependencies_status() -> Dict[str, Any]:
    """
    Get status of all external dependencies.

    Returns:
        Dict[str, Any]: Dependencies status
    """
    dependencies = {
        "database": {
            "configured": bool(settings.NEON_DB_URL),
            "type": "PostgreSQL (Neon)",
            "required": True
        },
        "redis": {
            "configured": bool(settings.REDIS_URL),
            "type": "Redis",
            "required": False,
            "features_enabled": ["token_blacklisting", "rate_limiting"] if settings.REDIS_URL else []
        },
        "authentication": {
            "configured": bool(settings.BETTER_AUTH_SECRET),
            "type": "JWT",
            "required": True
        }
    }

    return {
        "dependencies": dependencies,
        "timestamp": datetime.now().isoformat(),
        "all_required_met": all(
            dep["configured"] for dep in dependencies.values()
            if dep.get("required", False)
        )
    }


# Initialize start time for uptime calculation
get_metrics._start_time = time.time()


def include_monitoring_routes(app):
    """
    Include monitoring routes in the main application.

    Args:
        app: FastAPI application instance
    """
    app.include_router(router)
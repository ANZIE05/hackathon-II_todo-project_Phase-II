import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import logging
import signal
import sys
from src.middleware.error_handler import ErrorHandlerMiddleware
from src.middleware.request_id import RequestIDMiddleware
from src.config.settings import settings
from src.api.health import include_router as include_health_router
from src.api.auth import router as auth_router
from src.api.tasks import router as tasks_router
from src.api.monitoring import include_monitoring_routes
from src.database.connection import engine
from sqlmodel import SQLModel


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan event handler for startup and shutdown events.
    """
    # Startup
    logger.info("Starting up the Todo Application Backend...")

    # Run startup checks
    try:
        from src.startup_checks import perform_startup_checks_sync
        if not perform_startup_checks_sync():
            logger.error("Startup checks failed, shutting down...")
            sys.exit(1)
    except Exception as e:
        logger.error(f"Error running startup checks: {e}")
        sys.exit(1)

    logger.info("Startup checks passed, application is ready.")

    yield  # Application runs here

    # Shutdown
    logger.info("Shutting down the Todo Application Backend...")

    # Close database engine
    try:
        await engine.dispose()
        logger.info("Database engine closed successfully.")
    except Exception as e:
        logger.error(f"Error closing database engine: {e}")

    logger.info("Shutdown completed.")


app = FastAPI(
    title="Todo Application Backend",
    description="""
    Backend API for the Phase-II Full-Stack Todo Application.

    ## Features

    * User authentication and authorization with JWT
    * Secure task management with user isolation
    * RESTful API design
    * Comprehensive error handling
    * Rate limiting and security measures

    ## Authentication

    All protected endpoints require a valid JWT token in the Authorization header:
    `Authorization: Bearer <token>`
    """,
    version="1.0.0",
    contact={
        "name": "Todo App API Support",
        "url": "http://todo-app.example.com/contact",
        "email": "support@todo-app.example.com",
    },
    license_info={
        "name": "MIT License",
        "url": "https://opensource.org/licenses/MIT",
    },
    openapi_tags=[
        {
            "name": "Authentication",
            "description": "Endpoints for user registration, login, and token management"
        },
        {
            "name": "Tasks",
            "description": "Endpoints for task management (CRUD operations)"
        },
        {
            "name": "Health",
            "description": "Health check endpoints"
        }
    ],
    lifespan=lifespan  # Add lifespan to handle startup/shutdown
)


# Add request ID middleware first (order matters for traceability)
app.add_middleware(RequestIDMiddleware)

# Add error handling middleware
# app.add_middleware(ErrorHandlerMiddleware)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins_list,  # Use allowed origins from settings
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"],  # Specific methods
    allow_headers=["*"],  # Allow all headers
)

@app.get("/")
async def root():
    return {"message": "Welcome to the Todo Application Backend"}

# Include API routers
app.include_router(auth_router, prefix="/api")
app.include_router(tasks_router, prefix="/api")
include_health_router(app)
include_monitoring_routes(app)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
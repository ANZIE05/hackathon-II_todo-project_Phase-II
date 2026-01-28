"""
API Documentation for the Todo Application Backend.

This module contains comprehensive documentation for all API endpoints,
including request/response schemas, authentication requirements, and examples.
"""

from fastapi import FastAPI
from typing import Dict, Any
import json


def setup_api_documentation(app: FastAPI) -> None:
    """
    Setup API documentation for the application.

    Args:
        app: FastAPI application instance
    """
    # FastAPI automatically generates OpenAPI documentation
    # This function can be used to customize or extend the documentation

    # Example of adding custom documentation
    app.docs_url = "/docs"  # Swagger UI
    app.redoc_url = "/redoc"  # ReDoc UI
    app.openapi_url = "/openapi.json"  # OpenAPI schema


# API Endpoints Documentation
API_ENDPOINTS = {
    "authentication": {
        "POST /api/auth/register": {
            "summary": "Register a new user",
            "description": "Creates a new user account with the provided credentials.",
            "request": {
                "body": {
                    "email": "string, required - User's email address",
                    "password": "string, required - User's password (min 8 chars with uppercase, lowercase, digit)",
                    "confirm_password": "string, required - Password confirmation"
                }
            },
            "responses": {
                "200": "Success response with JWT token",
                "400": "Bad request - Invalid input data",
                "409": "Conflict - Email already exists"
            },
            "auth_required": False
        },
        "POST /api/auth/login": {
            "summary": "Login user",
            "description": "Authenticates a user and returns a JWT token.",
            "request": {
                "body": {
                    "email": "string, required - User's email address",
                    "password": "string, required - User's password"
                }
            },
            "responses": {
                "200": "Success response with JWT token",
                "400": "Bad request - Invalid input data",
                "401": "Unauthorized - Invalid credentials"
            },
            "auth_required": False
        },
        "POST /api/auth/logout": {
            "summary": "Logout user",
            "description": "Logs out the current user and invalidates the token.",
            "request": {
                "headers": {
                    "Authorization": "Bearer token, required - JWT token"
                }
            },
            "responses": {
                "200": "Success response",
                "401": "Unauthorized - Invalid or expired token"
            },
            "auth_required": True
        },
        "POST /api/auth/refresh": {
            "summary": "Refresh JWT token",
            "description": "Generates a new access token using a refresh token.",
            "request": {
                "body": {
                    "refresh_token": "string, required - Valid refresh token"
                }
            },
            "responses": {
                "200": "New access token",
                "401": "Unauthorized - Invalid refresh token"
            },
            "auth_required": False
        }
    },
    "tasks": {
        "GET /api/tasks": {
            "summary": "List user tasks",
            "description": "Retrieves all tasks belonging to the authenticated user.",
            "request": {
                "headers": {
                    "Authorization": "Bearer token, required - JWT token"
                },
                "query_params": {
                    "status": "string, optional - Filter by task status (pending, completed)",
                    "priority": "string, optional - Filter by priority (low, medium, high)",
                    "due_date_from": "date, optional - Filter tasks due after this date",
                    "due_date_to": "date, optional - Filter tasks due before this date",
                    "search": "string, optional - Search term for task titles/descriptions"
                }
            },
            "responses": {
                "200": "List of user's tasks",
                "401": "Unauthorized - Invalid or expired token"
            },
            "auth_required": True
        },
        "POST /api/tasks": {
            "summary": "Create new task",
            "description": "Creates a new task for the authenticated user.",
            "request": {
                "headers": {
                    "Authorization": "Bearer token, required - JWT token"
                },
                "body": {
                    "title": "string, required - Task title",
                    "description": "string, optional - Task description",
                    "due_date": "datetime, optional - Due date for the task",
                    "priority": "string, optional - Priority level (low, medium, high)",
                    "completed": "bool, optional - Whether task is completed (default: false)"
                }
            },
            "responses": {
                "200": "Created task object",
                "400": "Bad request - Invalid input data",
                "401": "Unauthorized - Invalid or expired token"
            },
            "auth_required": True
        },
        "GET /api/tasks/{id}": {
            "summary": "Get specific task",
            "description": "Retrieves a specific task by ID for the authenticated user.",
            "request": {
                "headers": {
                    "Authorization": "Bearer token, required - JWT token"
                },
                "path_params": {
                    "id": "UUID, required - Task ID"
                }
            },
            "responses": {
                "200": "Task object",
                "401": "Unauthorized - Invalid or expired token",
                "404": "Not found - Task doesn't exist or belongs to another user"
            },
            "auth_required": True
        },
        "PUT /api/tasks/{id}": {
            "summary": "Update task",
            "description": "Updates a specific task by ID for the authenticated user.",
            "request": {
                "headers": {
                    "Authorization": "Bearer token, required - JWT token"
                },
                "path_params": {
                    "id": "UUID, required - Task ID"
                },
                "body": {
                    "title": "string, required - Task title",
                    "description": "string, optional - Task description",
                    "due_date": "datetime, optional - Due date for the task",
                    "priority": "string, optional - Priority level (low, medium, high)",
                    "completed": "bool, optional - Whether task is completed"
                }
            },
            "responses": {
                "200": "Updated task object",
                "400": "Bad request - Invalid input data",
                "401": "Unauthorized - Invalid or expired token",
                "404": "Not found - Task doesn't exist or belongs to another user"
            },
            "auth_required": True
        },
        "PATCH /api/tasks/{id}": {
            "summary": "Partially update task",
            "description": "Partially updates a specific task by ID for the authenticated user.",
            "request": {
                "headers": {
                    "Authorization": "Bearer token, required - JWT token"
                },
                "path_params": {
                    "id": "UUID, required - Task ID"
                },
                "body": {
                    "title": "string, optional - Task title",
                    "description": "string, optional - Task description",
                    "due_date": "datetime, optional - Due date for the task",
                    "priority": "string, optional - Priority level (low, medium, high)",
                    "completed": "bool, optional - Whether task is completed"
                }
            },
            "responses": {
                "200": "Updated task object",
                "400": "Bad request - Invalid input data",
                "401": "Unauthorized - Invalid or expired token",
                "404": "Not found - Task doesn't exist or belongs to another user"
            },
            "auth_required": True
        },
        "PATCH /api/tasks/{id}/complete": {
            "summary": "Mark task as complete/incomplete",
            "description": "Marks a specific task as completed or incomplete.",
            "request": {
                "headers": {
                    "Authorization": "Bearer token, required - JWT token"
                },
                "path_params": {
                    "id": "UUID, required - Task ID"
                },
                "body": {
                    "completed": "bool, required - Whether task is completed"
                }
            },
            "responses": {
                "200": "Updated task object",
                "400": "Bad request - Invalid input data",
                "401": "Unauthorized - Invalid or expired token",
                "404": "Not found - Task doesn't exist or belongs to another user"
            },
            "auth_required": True
        },
        "DELETE /api/tasks/{id}": {
            "summary": "Delete task",
            "description": "Deletes a specific task by ID for the authenticated user.",
            "request": {
                "headers": {
                    "Authorization": "Bearer token, required - JWT token"
                },
                "path_params": {
                    "id": "UUID, required - Task ID"
                }
            },
            "responses": {
                "200": "Success message",
                "401": "Unauthorized - Invalid or expired token",
                "404": "Not found - Task doesn't exist or belongs to another user"
            },
            "auth_required": True
        }
    },
    "health": {
        "GET /health": {
            "summary": "Health check",
            "description": "Basic health check endpoint.",
            "responses": {
                "200": "Health status"
            },
            "auth_required": False
        },
        "GET /health/database": {
            "summary": "Database health check",
            "description": "Checks database connectivity.",
            "responses": {
                "200": "Database health status"
            },
            "auth_required": False
        },
        "GET /health/ready": {
            "summary": "Readiness check",
            "description": "Checks if the application is ready to serve traffic.",
            "responses": {
                "200": "Readiness status"
            },
            "auth_required": False
        }
    }
}


def get_api_documentation() -> Dict[str, Any]:
    """
    Get comprehensive API documentation.

    Returns:
        Dict[str, Any]: API documentation
    """
    return {
        "title": "Todo Application API Documentation",
        "version": "1.0.0",
        "description": "Complete API documentation for the Todo Application Backend",
        "endpoints": API_ENDPOINTS,
        "authentication": {
            "scheme": "JWT Bearer Token",
            "header": "Authorization: Bearer <token>",
            "token_lifetime": "Configurable, default 24 hours",
            "refresh_tokens": "Available via /auth/refresh endpoint"
        },
        "rate_limits": {
            "global": "1000 requests per hour",
            "per_ip": "100 requests per hour",
            "per_endpoint": "10 requests per minute"
        },
        "security_features": [
            "CORS configured for frontend integration",
            "Rate limiting implemented",
            "Input validation and sanitization",
            "SQL injection protection",
            "XSS protection",
            "Proper authentication and authorization"
        ]
    }


def get_openapi_schema(app: FastAPI) -> Dict[str, Any]:
    """
    Get the OpenAPI schema for the application.

    Args:
        app: FastAPI application instance

    Returns:
        Dict[str, Any]: OpenAPI schema
    """
    return app.openapi()
# Backend Quickstart Guide: Phase-II Todo Application

## Overview
This guide provides essential information to quickly understand and begin implementing the backend for the Phase-II Todo Application.

## Prerequisites
- Python 3.9+
- FastAPI
- SQLModel
- Neon Serverless PostgreSQL
- JWT authentication libraries (PyJWT, passlib)

## Environment Setup
Required environment variables:
- `NEON_DB_URL`: Database connection string for Neon Serverless PostgreSQL
- `BETTER_AUTH_SECRET`: Secret key for JWT signing and verification
- `BETTER_AUTH_URL`: Base URL for auth-related configurations
- `JWT_EXPIRATION_HOURS`: JWT token expiration duration (default: 24)
- `ALLOWED_ORIGINS`: Comma-separated list of allowed frontend origins

## Core Components

### 1. Data Models
- **User Model**: Contains email, hashed password, timestamps, and active status
- **Task Model**: Contains title, description, due date, priority, completion status, and user reference

### 2. Authentication Layer
- Registration endpoint: `/api/auth/register`
- Login endpoint: `/api/auth/login`
- JWT-based authentication with configurable expiration

### 3. Task Management API
- Create task: `POST /api/tasks`
- List tasks: `GET /api/tasks`
- Get task: `GET /api/tasks/{id}`
- Update task: `PUT /api/tasks/{id}`
- Complete task: `PATCH /api/tasks/{id}/complete`
- Delete task: `DELETE /api/tasks/{id}`

### 4. Security Features
- JWT token validation on all protected endpoints
- User-scoped data access (users can only access their own tasks)
- Proper error handling with standardized responses

## Implementation Order
1. Set up project structure and dependencies
2. Implement data models with SQLModel
3. Configure database connection with Neon PostgreSQL
4. Implement authentication endpoints
5. Create JWT middleware for authorization
6. Build task management endpoints
7. Implement error handling
8. Test API contract compliance

## Key Architecture Points
- Stateless backend with JWT-based authentication
- All task operations are user-scoped
- Standardized error response format
- Proper middleware ordering for security
- Migration-ready database schema

## Testing Endpoints
After implementation, verify:
- User registration and login work correctly
- JWT tokens are properly issued and validated
- Users can only access their own tasks
- All API endpoints return expected responses per contract
- Error scenarios return appropriate status codes
# API Contract: Frontend-Backend Integration for Todo Application

## Authentication API Contract

### Login Endpoint
- **Method**: POST
- **Path**: `/api/auth/login`
- **Request Headers**:
  - `Content-Type: application/json`
- **Request Body**:
  ```json
  {
    "email": "string (required)",
    "password": "string (required)"
  }
  ```
- **Response Success (200)**:
  ```json
  {
    "token": "string (JWT token)",
    "user": {
      "id": "string",
      "email": "string",
      "name": "string"
    }
  }
  ```
- **Response Error (401)**:
  ```json
  {
    "error": "string (error message)"
  }
  ```

### Signup Endpoint
- **Method**: POST
- **Path**: `/api/auth/signup`
- **Request Headers**:
  - `Content-Type: application/json`
- **Request Body**:
  ```json
  {
    "email": "string (required)",
    "password": "string (required)",
    "name": "string (required)"
  }
  ```
- **Response Success (201)**:
  ```json
  {
    "token": "string (JWT token)",
    "user": {
      "id": "string",
      "email": "string",
      "name": "string"
    }
  }
  ```
- **Response Error (400, 409)**:
  ```json
  {
    "error": "string (error message)"
  }
  ```

## Task API Contract

### Get Tasks
- **Method**: GET
- **Path**: `/api/tasks`
- **Request Headers**:
  - `Authorization: Bearer {token}`
- **Response Success (200)**:
  ```json
  {
    "tasks": [
      {
        "id": "string",
        "title": "string",
        "description": "string",
        "status": "string (active|completed)",
        "priority": "string (low|medium|high)",
        "dueDate": "string (ISO date format)",
        "createdAt": "string (ISO date format)",
        "updatedAt": "string (ISO date format)",
        "userId": "string"
      }
    ]
  }
  ```
- **Response Error (401, 403)**:
  ```json
  {
    "error": "string (error message)"
  }
  ```

### Create Task
- **Method**: POST
- **Path**: `/api/tasks`
- **Request Headers**:
  - `Authorization: Bearer {token}`
  - `Content-Type: application/json`
- **Request Body**:
  ```json
  {
    "title": "string (required)",
    "description": "string (optional)",
    "status": "string (active|completed, default: active)",
    "priority": "string (low|medium|high, default: medium)",
    "dueDate": "string (ISO date format, optional)"
  }
  ```
- **Response Success (201)**:
  ```json
  {
    "task": {
      "id": "string",
      "title": "string",
      "description": "string",
      "status": "string",
      "priority": "string",
      "dueDate": "string (ISO date format)",
      "createdAt": "string (ISO date format)",
      "updatedAt": "string (ISO date format)",
      "userId": "string"
    }
  }
  ```
- **Response Error (400, 401, 403)**:
  ```json
  {
    "error": "string (error message)"
  }
  ```

### Update Task
- **Method**: PUT
- **Path**: `/api/tasks/{id}`
- **Request Headers**:
  - `Authorization: Bearer {token}`
  - `Content-Type: application/json`
- **Request Body**:
  ```json
  {
    "title": "string (optional)",
    "description": "string (optional)",
    "status": "string (active|completed, optional)",
    "priority": "string (low|medium|high, optional)",
    "dueDate": "string (ISO date format, optional)"
  }
  ```
- **Response Success (200)**:
  ```json
  {
    "task": {
      "id": "string",
      "title": "string",
      "description": "string",
      "status": "string",
      "priority": "string",
      "dueDate": "string (ISO date format)",
      "createdAt": "string (ISO date format)",
      "updatedAt": "string (ISO date format)",
      "userId": "string"
    }
  }
  ```
- **Response Error (400, 401, 403, 404)**:
  ```json
  {
    "error": "string (error message)"
  }
  ```

### Delete Task
- **Method**: DELETE
- **Path**: `/api/tasks/{id}`
- **Request Headers**:
  - `Authorization: Bearer {token}`
- **Response Success (204)**: No content
- **Response Error (401, 403, 404)**:
  ```json
  {
    "error": "string (error message)"
  }
  ```

## Error Format Contract

All error responses from the backend will follow this format:
```json
{
  "error": "string (human-readable error message)",
  "code": "string (error code, optional)",
  "timestamp": "string (ISO date format, optional)"
}
```

## Frontend Integration Requirements

1. All API requests must include the Authorization header with the JWT token
2. Error responses must be handled gracefully with user-friendly messages
3. Loading states must be displayed during API operations
4. Network errors must be communicated to the user with retry options
5. Authentication errors (401) must trigger logout and redirect to login
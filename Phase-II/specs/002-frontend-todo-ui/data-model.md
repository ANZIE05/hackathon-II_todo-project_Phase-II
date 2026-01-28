# Data Model: Frontend UI for Phase-II Todo Application

## Task Entity
- **taskId**: string (UUID) - Unique identifier for the task
- **title**: string (required) - Title of the task (max 255 characters)
- **description**: string (optional) - Detailed description of the task (max 1000 characters)
- **status**: enum ('active', 'completed') - Current status of the task
- **priority**: enum ('low', 'medium', 'high') - Priority level of the task
- **dueDate**: Date (optional) - Deadline for the task completion
- **createdAt**: Date - Timestamp when task was created
- **updatedAt**: Date - Timestamp when task was last updated
- **userId**: string (foreign key) - Owner of the task

### Validation Rules
- Title must be 1-255 characters
- Description, if provided, must be 0-1000 characters
- Status must be one of the allowed values
- Priority must be one of the allowed values
- Due date, if provided, must be a future date

### State Transitions
- From 'active' to 'completed': When user marks task as complete
- From 'completed' to 'active': When user reactivates task

## User Session Entity
- **jwtToken**: string (required) - JWT token for authentication
- **userId**: string (required) - Identifier for the authenticated user
- **expiresAt**: Date - Expiration time for the JWT token
- **refreshToken**: string (optional) - Token for refreshing the session

### Validation Rules
- JWT token must be valid and not expired
- User ID must correspond to an existing user
- Refresh token, if provided, must be valid

### State Transitions
- From 'unauthenticated' to 'authenticated': After successful login/signup
- From 'authenticated' to 'expired': When JWT token expires
- From 'authenticated'/'expired' to 'unauthenticated': When user logs out

## UI State Entity
- **route**: string - Current active route in the application
- **isLoading**: boolean - Whether an API call is in progress
- **error**: string (optional) - Error message if an error occurred
- **filters**: object - Current filter settings for task display
  - **statusFilter**: enum ('all', 'active', 'completed')
  - **priorityFilter**: enum ('all', 'low', 'medium', 'high')
  - **searchQuery**: string (optional)

### Validation Rules
- Route must be one of the defined application routes
- Error message, if present, should be displayed to the user
- Filters must contain valid values as defined above

## Form State Entity
- **formData**: object - Current values in the form
- **errors**: object - Validation errors for form fields
- **isSubmitting**: boolean - Whether the form is currently submitting
- **submitSuccess**: boolean - Whether the last submission was successful

### Validation Rules
- Form data must pass validation before submission
- Errors must be cleared when user starts correcting the form
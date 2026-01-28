# Data Model Specification: Phase-II Todo Application Backend

## Entity: User

### Fields
- **id** (UUID, Primary Key, Auto-generated)
  - Unique identifier for the user
  - UUID type for global uniqueness
  - Auto-generated using database UUID function

- **email** (String, Unique, Required)
  - User's email address for authentication
  - Maximum length: 255 characters
  - Case-insensitive uniqueness constraint
  - Indexed for fast lookup

- **hashed_password** (String, Required)
  - Securely hashed password using bcrypt
  - Maximum length: 255 characters
  - Never stored in plaintext
  - Stored as hash with salt

- **created_at** (DateTime, Required)
  - Timestamp of account creation
  - Auto-set to current time on creation
  - Stored in UTC timezone

- **updated_at** (DateTime, Required)
  - Timestamp of last account update
  - Auto-updated to current time on any change
  - Stored in UTC timezone

- **is_active** (Boolean, Default: True)
  - Flag indicating if account is active
  - Used for soft account deactivation

### Relationships
- One User → Many Tasks (user.tasks)

### Validation Rules
- Email must be valid email format
- Email must be unique across all users
- Password must be hashed before storing
- Required fields must not be null

## Entity: Task

### Fields
- **id** (UUID, Primary Key, Auto-generated)
  - Unique identifier for the task
  - UUID type for global uniqueness
  - Auto-generated using database UUID function

- **title** (String, Required)
  - Task title or name
  - Maximum length: 255 characters
  - Cannot be empty or whitespace-only

- **description** (Text, Optional)
  - Detailed description of the task
  - Unlimited length (TEXT type)
  - Can be null

- **due_date** (DateTime, Optional)
  - Deadline for completing the task
  - Can be null if no deadline specified
  - Stored in UTC timezone

- **priority** (String, Default: 'medium')
  - Priority level of the task
  - Values: 'low', 'medium', 'high'
  - Case-sensitive enum-like behavior

- **completed** (Boolean, Default: False)
  - Flag indicating if task is completed
  - Default to false when creating new tasks

- **user_id** (UUID, Foreign Key, Required)
  - Reference to the user who owns this task
  - Links to User.id field
  - Cascading delete behavior defined

- **created_at** (DateTime, Required)
  - Timestamp of task creation
  - Auto-set to current time on creation
  - Stored in UTC timezone

- **updated_at** (DateTime, Required)
  - Timestamp of last task update
  - Auto-updated to current time on any change
  - Stored in UTC timezone

### Relationships
- Many Tasks ← One User (task.user)

### Validation Rules
- Title is required and must not be empty
- Priority must be one of 'low', 'medium', 'high'
- User_id must reference an existing User
- Tasks must belong to a valid user
- Required fields must not be null

## Indexes

### User Indexes
- Primary key index on `id`
- Unique index on `email`
- Composite index on `email` and `is_active` for authentication queries

### Task Indexes
- Primary key index on `id`
- Index on `user_id` for user-specific queries
- Index on `completed` for filtering completed/pending tasks
- Index on `due_date` for deadline-based queries
- Composite index on `user_id` and `completed` for user task lists
- Composite index on `user_id` and `due_date` for user deadline queries

## State Transitions

### Task State Transitions
- **Pending** → **Completed**: When task is marked as completed
- **Completed** → **Pending**: When task is marked as incomplete (if feature supported)

### User State Transitions
- **Active** → **Inactive**: When account is deactivated
- **Inactive** → **Active**: When account is reactivated

## Constraints

### Referential Integrity
- Foreign key constraints ensure data consistency
- Cascade delete on user removal (removes user's tasks)
- Prevent orphaned tasks without valid user references

### Data Validation
- Application-level validation before database insertion
- Database-level constraints as backup validation
- Unique constraints on critical fields
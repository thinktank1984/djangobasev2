# Todo Tasks System

A comprehensive todo task management system with user sharing capabilities built for the Django Blog Application.

## Features

### Core Functionality
- **Task Management**: Create, read, update, and delete tasks
- **User Authentication**: Login-protected task management
- **Priority Levels**: Low, Medium, High, Urgent
- **Status Tracking**: Pending, In Progress, Completed, Cancelled
- **Due Dates**: Optional deadline management
- **Search & Filtering**: Filter by status, priority, and search terms
- **Pagination**: Efficient handling of large task lists

### Sharing & Collaboration
- **Task Sharing**: Share tasks with other users
- **Permission Levels**: View, Edit, Assign, Delete permissions
- **Comments**: Collaborative commenting on tasks
- **User Roles**: Owner, Assignee, Collaborator, Viewer roles
- **Shared Tasks View**: Dedicated view for tasks shared with you

### Organization
- **Task Lists**: Organize tasks into collections
- **Public/Private Lists**: Control list visibility
- **Bulk Operations**: Add multiple tasks to lists

## Models

### Task
Main task model with fields:
- `title`: Task title (required)
- `description`: Detailed description (optional)
- `priority`: Priority level (Low/Medium/High/Urgent)
- `status`: Current status (Pending/In Progress/Completed/Cancelled)
- `due_date`: Optional deadline
- `created_by`: Task creator

### UserTask
Intermediate model tracking user-task relationships:
- `user`: Associated user
- `task`: Associated task
- `role`: User role (Owner/Assignee/Collaborator/Viewer)
- `is_active`: Active status flag

### TaskShare
Task sharing between users:
- `task`: Shared task
- `shared_by`: User who shared the task
- `shared_with`: Recipient user
- `permission`: Permission level (View/Edit/Assign/Delete)
- `message`: Optional sharing message

### TaskComment
Comments for collaboration:
- `task`: Associated task
- `author`: Comment author
- `content`: Comment content
- `created_at`: Timestamp

### TaskList
Task organization:
- `name`: List name
- `description`: List description
- `created_by`: List creator
- `tasks`: Many-to-many task relationship
- `is_public`: Public visibility flag

## URL Structure

```
/tasks/                          # Task list view
/tasks/task/<id>/               # Task detail view
/tasks/task/create/             # Create new task
/tasks/task/<id>/edit/          # Edit task
/tasks/task/<id>/delete/        # Delete task
/tasks/task/<id>/share/         # Share task
/tasks/task/<id>/comment/       # Add comment
/tasks/shared-tasks/            # Tasks shared with user
/tasks/lists/                   # Task lists
/tasks/lists/<id>/             # Task list detail
```

## Views & Permissions

### Authentication
All views require `@login_required` decorator.

### Permission Checks
- **View Access**: Task creator, assigned users, or users with shared access
- **Edit Access**: Task creator or users with Edit/Delete permissions
- **Share Access**: Task creator or users with Assign permissions
- **Delete Access**: Task creator or users with Delete permissions

## Templates

### Base Template
- `base_todo.html`: Extends main base template with todo-specific layout

### Main Templates
- `task_list.html`: Main task list with filtering and pagination
- `task_detail.html`: Detailed task view with comments
- `task_form.html`: Create/edit task form
- `share_task.html`: Task sharing interface
- `task_confirm_delete.html`: Delete confirmation
- `shared_tasks.html`: View of shared tasks

## Forms

- `TaskForm`: Task creation/editing
- `TaskCommentForm`: Comment submission
- `TaskShareForm`: Task sharing with validation
- `TaskListForm`: Task list management
- `TaskFilterForm`: Search and filtering

## Admin Interface

All models are registered with the Django admin:
- Task management with filtering
- User task relationships
- Task sharing tracking
- Comment moderation
- Task list management

## Usage Examples

### Creating a Task
```python
from django.contrib.auth.models import User
from apps.todo_tasks.models import Task, UserTask

user = User.objects.get(username='testuser')
task = Task.objects.create(
    title='Complete project documentation',
    description='Write comprehensive documentation for the new feature',
    priority='high',
    status='pending',
    created_by=user
)
UserTask.objects.create(user=user, task=task, role='owner')
```

### Sharing a Task
```python
from apps.todo_tasks.models import TaskShare

share = TaskShare.objects.create(
    task=task,
    shared_by=user,
    shared_with=another_user,
    permission='edit',
    message='Can you help review this documentation?'
)
```

### Adding Comments
```python
from apps.todo_tasks.models import TaskComment

comment = TaskComment.objects.create(
    task=task,
    author=another_user,
    content='I think we should add more examples here.'
)
```

## Security Features

- **Authentication Required**: All functionality requires user login
- **Permission-Based Access**: Granular permissions for view/edit/share/delete
- **User Validation**: Prevents sharing with self
- **Owner Verification**: Only creators can delete tasks
- **Permission Inheritance**: Shared users inherit appropriate permissions

## Integration

The todo tasks system integrates with:
- Django's built-in authentication system
- Tailwind CSS for styling
- Django Messages for user feedback
- Django Forms for validation
- Django Admin for management

## Database Schema

The system creates 5 main tables:
- `todo_tasks_task`: Core task data
- `todo_tasks_usertask`: User-task relationships
- `todo_tasks_taskshare`: Sharing information
- `todo_tasks_taskcomment`: Comments
- `todo_tasks_tasklist`: Task lists
- `todo_tasks_tasklist_tasks`: Task-list relationships (many-to-many)

## Future Enhancements

Potential improvements:
- Email notifications for task sharing
- Task dependencies and subtasks
- File attachments
- Task templates
- Calendar integration
- Mobile app support
- API endpoints for external access
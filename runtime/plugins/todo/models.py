from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.urls import reverse


class Task(models.Model):
    """
    Main task model that can be shared among users
    """
    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('urgent', 'Urgent'),
    ]

    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]

    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='medium')
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='pending')
    due_date = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    # Creator of the task
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_tasks')

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Task'
        verbose_name_plural = 'Tasks'

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('todo_tasks:task_detail', kwargs={'pk': self.pk})

    def save(self, *args, **kwargs):
        # Set completed_at when status changes to completed
        if self.status == 'completed' and not self.completed_at:
            self.completed_at = timezone.now()
        elif self.status != 'completed':
            self.completed_at = None
        super().save(*args, **kwargs)


class UserTask(models.Model):
    """
    Intermediate model to track user-specific task relationships
    """
    ROLE_CHOICES = [
        ('owner', 'Owner'),
        ('assignee', 'Assignee'),
        ('collaborator', 'Collaborator'),
        ('viewer', 'Viewer'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_tasks')
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='user_tasks')
    role = models.CharField(max_length=15, choices=ROLE_CHOICES, default='assignee')
    assigned_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        unique_together = ['user', 'task']
        verbose_name = 'User Task'
        verbose_name_plural = 'User Tasks'

    def __str__(self):
        return f"{self.user.username} - {self.task.title} ({self.role})"


class TaskShare(models.Model):
    """
    Model to track task sharing between users
    """
    PERMISSION_CHOICES = [
        ('view', 'Can View'),
        ('edit', 'Can Edit'),
        ('assign', 'Can Assign'),
        ('delete', 'Can Delete'),
    ]

    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='shared_tasks')
    shared_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='shared_tasks')
    shared_with = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_tasks')
    permission = models.CharField(max_length=10, choices=PERMISSION_CHOICES, default='view')
    shared_at = models.DateTimeField(auto_now_add=True)
    message = models.TextField(blank=True, help_text="Optional message when sharing")

    class Meta:
        unique_together = ['task', 'shared_with']
        verbose_name = 'Task Share'
        verbose_name_plural = 'Task Shares'

    def __str__(self):
        return f"{self.task.title} shared with {self.shared_with.username}"


class TaskComment(models.Model):
    """
    Comments on tasks for collaboration
    """
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['created_at']
        verbose_name = 'Task Comment'
        verbose_name_plural = 'Task Comments'

    def __str__(self):
        return f"Comment by {self.author.username} on {self.task.title}"


class TaskList(models.Model):
    """
    Collections/Lists to organize tasks
    """
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='task_lists')
    tasks = models.ManyToManyField(Task, related_name='task_lists', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_public = models.BooleanField(default=False)

    class Meta:
        ordering = ['name']
        verbose_name = 'Task List'
        verbose_name_plural = 'Task Lists'

    def __str__(self):
        return self.name

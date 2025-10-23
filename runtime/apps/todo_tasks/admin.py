from django.contrib import admin
from .models import Task, UserTask, TaskShare, TaskComment, TaskList


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ['title', 'created_by', 'status', 'priority', 'due_date', 'created_at']
    list_filter = ['status', 'priority', 'created_at']
    search_fields = ['title', 'description']
    date_hierarchy = 'created_at'
    readonly_fields = ['created_at', 'updated_at', 'completed_at']


@admin.register(UserTask)
class UserTaskAdmin(admin.ModelAdmin):
    list_display = ['task', 'user', 'role', 'assigned_at', 'is_active']
    list_filter = ['role', 'is_active', 'assigned_at']
    search_fields = ['task__title', 'user__username']


@admin.register(TaskShare)
class TaskShareAdmin(admin.ModelAdmin):
    list_display = ['task', 'shared_by', 'shared_with', 'permission', 'shared_at']
    list_filter = ['permission', 'shared_at']
    search_fields = ['task__title', 'shared_by__username', 'shared_with__username']


@admin.register(TaskComment)
class TaskCommentAdmin(admin.ModelAdmin):
    list_display = ['task', 'author', 'created_at']
    list_filter = ['created_at']
    search_fields = ['task__title', 'author__username', 'content']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(TaskList)
class TaskListAdmin(admin.ModelAdmin):
    list_display = ['name', 'created_by', 'is_public', 'created_at']
    list_filter = ['is_public', 'created_at']
    search_fields = ['name', 'description']
    filter_horizontal = ['tasks']

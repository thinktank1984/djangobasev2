from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.db.models import Q
from django.http import JsonResponse, HttpResponseForbidden
from django.views.decorators.http import require_POST
from django.core.paginator import Paginator
from django.utils import timezone
from .models import Task, UserTask, TaskShare, TaskComment, TaskList
from .forms import TaskForm, TaskCommentForm, TaskShareForm, TaskListForm


@login_required
def task_list(request):
    """
    Display list of tasks for the current user
    """
    # Get tasks where user is creator, assignee, or has been shared with
    user_tasks = Task.objects.filter(
        Q(created_by=request.user) |
        Q(user_tasks__user=request.user, user_tasks__is_active=True) |
        Q(shared_tasks__shared_with=request.user)
    ).distinct()

    # Filter by status if provided
    status_filter = request.GET.get('status')
    if status_filter:
        user_tasks = user_tasks.filter(status=status_filter)

    # Filter by priority if provided
    priority_filter = request.GET.get('priority')
    if priority_filter:
        user_tasks = user_tasks.filter(priority=priority_filter)

    # Search functionality
    search_query = request.GET.get('search')
    if search_query:
        user_tasks = user_tasks.filter(
            Q(title__icontains=search_query) |
            Q(description__icontains=search_query)
        )

    # Pagination
    paginator = Paginator(user_tasks, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'status_choices': Task.STATUS_CHOICES,
        'priority_choices': Task.PRIORITY_CHOICES,
        'current_status': status_filter,
        'current_priority': priority_filter,
        'search_query': search_query,
    }
    return render(request, 'todo_tasks/task_list.html', context)


@login_required
def task_detail(request, pk):
    """
    Display task details
    """
    task = get_object_or_404(Task, pk=pk)

    # Check if user has permission to view this task
    if not (task.created_by == request.user or
            task.user_tasks.filter(user=request.user, is_active=True).exists() or
            task.shared_tasks.filter(shared_with=request.user).exists()):
        return HttpResponseForbidden("You don't have permission to view this task.")

    comments = task.comments.all()
    comment_form = TaskCommentForm()

    context = {
        'task': task,
        'comments': comments,
        'comment_form': comment_form,
    }
    return render(request, 'todo_tasks/task_detail.html', context)


@login_required
def task_create(request):
    """
    Create a new task
    """
    if request.method == 'POST':
        form = TaskForm(request.POST)
        if form.is_valid():
            task = form.save(commit=False)
            task.created_by = request.user
            task.save()

            # Create UserTask relationship for the creator
            UserTask.objects.create(
                user=request.user,
                task=task,
                role='owner'
            )

            messages.success(request, 'Task created successfully!')
            return redirect('todo_tasks:task_detail', pk=task.pk)
    else:
        form = TaskForm()

    return render(request, 'todo_tasks/task_form.html', {
        'form': form,
        'title': 'Create Task'
    })


@login_required
def task_edit(request, pk):
    """
    Edit an existing task
    """
    task = get_object_or_404(Task, pk=pk)

    # Check if user has permission to edit
    if not (task.created_by == request.user or
            task.shared_tasks.filter(shared_with=request.user, permission__in=['edit', 'delete']).exists()):
        return HttpResponseForbidden("You don't have permission to edit this task.")

    if request.method == 'POST':
        form = TaskForm(request.POST, instance=task)
        if form.is_valid():
            form.save()
            messages.success(request, 'Task updated successfully!')
            return redirect('todo_tasks:task_detail', pk=task.pk)
    else:
        form = TaskForm(instance=task)

    return render(request, 'todo_tasks/task_form.html', {
        'form': form,
        'task': task,
        'title': 'Edit Task'
    })


@login_required
def task_delete(request, pk):
    """
    Delete a task
    """
    task = get_object_or_404(Task, pk=pk)

    # Check if user has permission to delete
    if not (task.created_by == request.user or
            task.shared_tasks.filter(shared_with=request.user, permission='delete').exists()):
        return HttpResponseForbidden("You don't have permission to delete this task.")

    if request.method == 'POST':
        task.delete()
        messages.success(request, 'Task deleted successfully!')
        return redirect('todo_tasks:task_list')

    return render(request, 'todo_tasks/task_confirm_delete.html', {'task': task})


@login_required
@require_POST
def add_comment(request, pk):
    """
    Add a comment to a task
    """
    task = get_object_or_404(Task, pk=pk)

    # Check if user has permission to comment
    if not (task.created_by == request.user or
            task.user_tasks.filter(user=request.user, is_active=True).exists() or
            task.shared_tasks.filter(shared_with=request.user).exists()):
        return HttpResponseForbidden("You don't have permission to comment on this task.")

    form = TaskCommentForm(request.POST)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.task = task
        comment.author = request.user
        comment.save()
        messages.success(request, 'Comment added successfully!')

    return redirect('todo_tasks:task_detail', pk=pk)


@login_required
def share_task(request, pk):
    """
    Share a task with another user
    """
    task = get_object_or_404(Task, pk=pk)

    # Check if user has permission to share
    if not (task.created_by == request.user or
            task.shared_tasks.filter(shared_with=request.user, permission='assign').exists()):
        return HttpResponseForbidden("You don't have permission to share this task.")

    if request.method == 'POST':
        form = TaskShareForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            permission = form.cleaned_data['permission']
            message = form.cleaned_data['message']

            try:
                shared_with = User.objects.get(username=username)

                if shared_with == request.user:
                    messages.error(request, 'You cannot share a task with yourself.')
                else:
                    # Create or update task share
                    task_share, created = TaskShare.objects.update_or_create(
                        task=task,
                        shared_with=shared_with,
                        defaults={
                            'shared_by': request.user,
                            'permission': permission,
                            'message': message
                        }
                    )

                    # Create UserTask relationship if it doesn't exist
                    UserTask.objects.get_or_create(
                        user=shared_with,
                        task=task,
                        defaults={
                            'role': 'collaborator' if permission in ['edit', 'assign'] else 'viewer'
                        }
                    )

                    action = 'shared' if created else 'updated sharing for'
                    messages.success(request, f'Task {action} with {username} successfully!')

            except User.DoesNotExist:
                messages.error(request, f'User "{username}" not found.')

            return redirect('todo_tasks:task_detail', pk=pk)
    else:
        form = TaskShareForm()

    return render(request, 'todo_tasks/share_task.html', {
        'form': form,
        'task': task
    })


@login_required
def my_shared_tasks(request):
    """
    Display tasks shared with the current user
    """
    shared_tasks = Task.objects.filter(
        shared_tasks__shared_with=request.user
    ).distinct().order_by('-shared_tasks__shared_at')

    paginator = Paginator(shared_tasks, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'todo_tasks/shared_tasks.html', {
        'page_obj': page_obj
    })


@login_required
def task_lists(request):
    """
    Display and create task lists
    """
    if request.method == 'POST':
        form = TaskListForm(request.POST)
        if form.is_valid():
            task_list = form.save(commit=False)
            task_list.created_by = request.user
            task_list.save()
            messages.success(request, 'Task list created successfully!')
            return redirect('todo_tasks:task_lists')
    else:
        form = TaskListForm()

    # Get user's task lists and public lists
    task_lists = TaskList.objects.filter(
        Q(created_by=request.user) | Q(is_public=True)
    ).distinct()

    return render(request, 'todo_tasks/task_lists.html', {
        'task_lists': task_lists,
        'form': form
    })


@login_required
def task_list_detail(request, pk):
    """
    Display tasks in a specific list
    """
    task_list = get_object_or_404(TaskList, pk=pk)

    # Check permission
    if not (task_list.created_by == request.user or task_list.is_public):
        return HttpResponseForbidden("You don't have permission to view this list.")

    tasks = task_list.tasks.all()

    return render(request, 'todo_tasks/task_list_detail.html', {
        'task_list': task_list,
        'tasks': tasks
    })

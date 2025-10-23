from django.urls import path
from . import views

app_name = 'todo'

urlpatterns = [
    # Task CRUD operations
    path('', views.task_list, name='task_list'),
    path('task/<int:pk>/', views.task_detail, name='task_detail'),
    path('task/create/', views.task_create, name='task_create'),
    path('task/<int:pk>/edit/', views.task_edit, name='task_edit'),
    path('task/<int:pk>/delete/', views.task_delete, name='task_delete'),

    # Task sharing and collaboration
    path('task/<int:pk>/share/', views.share_task, name='share_task'),
    path('task/<int:pk>/comment/', views.add_comment, name='add_comment'),
    path('shared-tasks/', views.my_shared_tasks, name='my_shared_tasks'),

    # Task lists
    path('lists/', views.task_lists, name='task_lists'),
    path('lists/<int:pk>/', views.task_list_detail, name='task_list_detail'),
]
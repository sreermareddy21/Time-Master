from django.urls import path
from . import views

app_name = 'planner'

urlpatterns = [
    path('', views.home, name='home'),
    path('tasks/', views.tasks, name='tasks'),
    path('tasks/new/', views.create_task, name='create_task'),
    path('tasks/<int:task_id>/', views.task, name='task'),
    path('tasks/<int:task_id>/delete/', views.delete_task, name='delete_task'),
    path('tasks/<int:task_id>/update/', views.update_task, name='update_task'),
    path('categories/', views.manage_categories, name='manage_categories'),
    path('categories/<int:category_id>/delete/', views.delete_category, name='delete_category'),
]
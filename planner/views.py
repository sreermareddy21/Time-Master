from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from planner.forms import TaskForm, CategoryForm
from django.shortcuts import get_object_or_404
from planner.models import Category, Task
from django.db.models import Count, Q, F
from django.utils import timezone
from datetime import datetime, time, timedelta

@login_required()
def home(request):
    # Get today's date range using timezone-aware datetimes
    today = datetime.now().date()
    today_start = timezone.make_aware(datetime.combine(today, time.min))
    today_end = timezone.make_aware(datetime.combine(today, time.max))

    # Get all tasks for the current user
    user_tasks = Task.objects.filter(user=request.user)

    # Get total counts with optimized queries
    total_tasks = user_tasks.count()
    
    # Task status counts
    status_counts = user_tasks.values('status').annotate(
        count=Count('id')
    ).order_by('status')
    
    # Initialize status counts
    completed_tasks = 0
    in_progress_tasks = 0
    pending_tasks = 0
    
    # Process status counts
    for status in status_counts:
        if status['status'] == 'completed':
            completed_tasks = status['count']
        elif status['status'] == 'in_progress':
            in_progress_tasks = status['count']
        elif status['status'] == 'pending':
            pending_tasks = status['count']

    # Calculate percentages safely
    total_count = max(total_tasks, 1)  # Prevent division by zero
    completed_percentage = round((completed_tasks / total_count) * 100, 1)
    in_progress_percentage = round((in_progress_tasks / total_count) * 100, 1)
    pending_percentage = round((pending_tasks / total_count) * 100, 1)

    # Calculate tasks trend (comparing with last week)
    week_ago = today - timedelta(days=7)
    week_ago_start = timezone.make_aware(datetime.combine(week_ago, time.min))
    tasks_last_week = user_tasks.filter(created_at__lt=week_ago_start).count()
    
    if tasks_last_week > 0:
        tasks_trend = round(((total_tasks - tasks_last_week) / tasks_last_week) * 100, 1)
    else:
        tasks_trend = 0

    # Get today's tasks with category information
    today_tasks = user_tasks.filter(
        deadline__date=today
    ).select_related('category').order_by(
        'deadline'
    ).annotate(
        category_color=F('category__color')
    )

    # Get categories overview with task counts
    categories = Category.objects.filter(
        user=request.user
    ).annotate(
        task_count=Count('task', filter=Q(task__user=request.user)),
        completed_count=Count('task', filter=Q(
            task__user=request.user,
            task__status='completed'
        )),
        pending_count=Count('task', filter=Q(
            task__user=request.user,
            task__status='pending'
        )),
        in_progress_count=Count('task', filter=Q(
            task__user=request.user,
            task__status='in_progress'
        ))
    ).order_by('-task_count')

    # Calculate category percentages and prepare color classes
    total_category_tasks = max(sum(category.task_count for category in categories), 1)
    for category in categories:
        # Calculate percentage of total tasks
        category.percentage = round((category.task_count / total_category_tasks) * 100, 1)
        
        # Calculate completion rate within category
        category_total = max(category.task_count, 1)
        category.completion_rate = round((category.completed_count / category_total) * 100, 1)
        
        # Ensure color is properly formatted for Tailwind classes
        category.color_class = category.color.lower()
        
        # Add status breakdown
        category.status_breakdown = {
            'completed': category.completed_count,
            'in_progress': category.in_progress_count,
            'pending': category.pending_count
        }

    # Get upcoming deadlines (next 7 days)
    upcoming_deadline = today + timedelta(days=7)
    upcoming_tasks = user_tasks.filter(
        deadline__date__gt=today,
        deadline__date__lte=upcoming_deadline
    ).select_related('category').order_by('deadline')[:5]

    # Get overdue tasks
    overdue_tasks = user_tasks.filter(
        deadline__date__lt=today,
        status__in=['pending', 'in_progress']
    ).select_related('category').order_by('deadline')

    # Calculate productivity metrics
    this_week_completed = user_tasks.filter(
        deadline__gte=week_ago_start,
        status='completed'
    ).count()
    
    if tasks_last_week > 0:
        productivity_change = round(((this_week_completed - tasks_last_week) / tasks_last_week) * 100, 1)
    else:
        productivity_change = 0

    context = {
        # Task Statistics
        'total_tasks': total_tasks,
        'completed_tasks': completed_tasks,
        'in_progress_tasks': in_progress_tasks,
        'pending_tasks': pending_tasks,
        
        # Percentages
        'completed_percentage': completed_percentage,
        'in_progress_percentage': in_progress_percentage,
        'pending_percentage': pending_percentage,
        
        # Trends and Changes
        'tasks_trend': tasks_trend,
        'productivity_change': productivity_change,
        
        # Task Lists
        'today_tasks': today_tasks,
        'upcoming_tasks': upcoming_tasks,
        'overdue_tasks': overdue_tasks,
        
        # Categories
        'categories': categories,
        'total_category_tasks': total_category_tasks,
        
        # Date Information
        'today': today,
        'week_ago': week_ago,
        'upcoming_deadline': upcoming_deadline,
        
        'page': 'dashboard',
    }
    
    return render(request, 'planner/home.html', context)




@login_required()
def create_task(request):
    user = request.user
    categories = Category.objects.filter(user=user)
    if request.method == 'POST':
        form = TaskForm(request.POST, request=request)
        if form.is_valid():
            task = form.save(commit=False)
            task.user = user
            task.save()
            messages.success(request, 'Task created successfully!')
            return redirect('planner:tasks')
    else:
        form = TaskForm(request=request)
    
    return render(request, 'planner/new_task.html', {
        'form': form, 
        'categories': categories,
        'page': 'create_task',
        })
    
@login_required()
def update_task(request, task_id):
    user = request.user
    task = get_object_or_404(Task, id=task_id, user=user)
    categories = Category.objects.filter(user=user)
    
    if request.method == 'POST':
        form = TaskForm(request.POST, instance=task, request=request)
        if form.is_valid():
            form.save()
            messages.success(request, 'Task updated successfully!')
            return redirect('planner:tasks')
    else:
        form = TaskForm(instance=task, request=request)
    
    return render(request, 'planner/update_task.html', {
        'form': form,
        'task': task,
        'categories': categories,
        'page': 'tasks',  # Since this is part of the tasks section
    })


@login_required()
def manage_categories(request):
    user = request.user
    categories = Category.objects.filter(user=user)
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            category = form.save(commit=False)
            # Save the icon from the form to the category
            category.icon = form.cleaned_data['icon']
            category.user = user
            category.save()
            messages.success(request, 'Category created successfully!')
            return redirect('planner:manage_categories')
    else:
        form = CategoryForm()
    
    return render(request, 'planner/categories.html', {
        'form': form,
        'categories': categories,
        'page': 'categories',
    })

@login_required()
def delete_category(request, category_id):
    if request.method == 'POST':
        category = get_object_or_404(Category, id=category_id)
        try:
            category.delete()
            messages.success(request, 'Category deleted successfully!')
        except Exception as e:
            messages.error(request, 'Cannot delete category. It may be associated with tasks.')
    return redirect('planner:manage_categories')

@login_required()
def tasks(request):
    user = request.user
    categories = Category.objects.filter(user=user)
    cat = request.GET.get('category', '')
    tasks = Task.objects.all()
    if cat:
        tasks = tasks.filter(category__name=cat)
    return render(request, 'planner/tasks.html', {
        'tasks': tasks, 
        'categories': categories,
        'page': 'tasks',
        })

@login_required()
def task(request, task_id):
    user = request.user
    categories = Category.objects.filter(user=user)
    task = get_object_or_404(Task, id=task_id)
    return render(request, 'planner/task.html', {
        'task': task, 
        'categories': categories,
        'page': 'tasks',
        })

@login_required
def delete_task(request, task_id):
    task = get_object_or_404(Task, id=task_id)
    try:
        task.delete()
        messages.success(request, 'Task deleted successfully!')
    except Exception as e:
        messages.error(request, 'Cannot delete task.')
    return redirect('planner:tasks')
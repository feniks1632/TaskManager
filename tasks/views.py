from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.shortcuts import render, redirect, get_object_or_404
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.http import require_http_methods

from .models import Task
from .forms import TaskForm, SignUpForm
from .services import TaskService


@login_required
def task_list(request):
    tasks = Task.objects.filter(assignee=request.user).order_by('-created_at')
    return render(request, 'tasks/list.html', {'tasks': tasks})

@login_required
def task_create(request):
    if request.method == 'POST':
        form = TaskForm(request.POST)
        if form.is_valid():
            servece = TaskService()
            task = servece.create_task(form.cleaned_data, created_by=request.user)
            messages.success(request, f"Задача {task.title} создана и уведомление отправлено!")
            return redirect('tasks:list')
    else:
        form = TaskForm()
    return render(request, 'tasks/form.html', {
        'form': form,
        'title': "Создать задачу"
    })

@login_required
def task_update(request, pk):
    task = get_object_or_404(Task, pk=pk)
    if request.method == 'POST':
        form = TaskForm(request.POST, instance=task)
        if form.is_valid():
            service = TaskService()
            service.update_task(task, form.cleaned_data)
            messages.success(request, "Задача обновлена!")
            return redirect('tasks:list')
    else:
        form = TaskForm(instance=task)
    return render(request, 'tasks/form.html', {
        'form': form,
        'title': "Редактировать задачу"
    })        

@login_required
def task_delete(request, pk):
    task = get_object_or_404(Task, pk=pk)
    if request.method == 'POST':
        task.delete()
        messages.success(request, "Задача {task.title} Удалена")
        return redirect('tasks:list')
    return render(request, 'tasks/confirm_delete.html', {'task': task})


@csrf_protect
@require_http_methods(["GET", "POST"])
def login_view(request):
    if request.user.is_authenticated:
        return redirect('tasks:list')

    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f"Добро пожаловать, {username}!")
                next_url = request.GET.get('next', 'tasks:list')
                return redirect(next_url)
            else:
                messages.error(request, "Неверное имя пользователя или пароль.")
        else:
            messages.error(request, "Проверьте введённые данные.")
    else:
        form = AuthenticationForm()

    return render(request, 'auth/login.html', {'form': form})


@csrf_protect
@require_http_methods(["POST"])
def logout_view(request):
    if request.user.is_authenticated:
        username = request.user.username
        logout(request)
        messages.info(request, f"Вы вышли из аккаунта {username}.")
    return redirect('login')

@csrf_protect
@require_http_methods(["GET", "POST"])
def signup_view(request):
    """
    Страница регистрации нового пользователя
    """
    if request.user.is_authenticated:
        return redirect('tasks:list')

    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f"Добро пожаловать, {user.username}! Аккаунт создан.")
            return redirect('tasks:list')
        else:
            messages.error(request, "Исправьте ошибки ниже.")
    else:
        form = SignUpForm()
    return render(request, 'auth/signup.html', {'form': form})
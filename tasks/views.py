from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from .models import Task
from .forms import TaskForm
from .services import TaskService


@login_required
def task_list(request):
    tasks = Task.objects.filter(assignee=request.user).order_by('-created_at')
    return render(request, 'tasks/list.html', {'task': tasks})

@login_required
def task_create(request):
    if request.method == 'POST':
        form = TaskForm(request.POST)
        if form.is_valid():
            servece = TaskService()
            task = servece.create_task(form.cleaned_data, created_by=request.user)
            messages.success(request, f"Задача {task.title} создана и уведомление отправлено!")
            return redirect('task:list')
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
            return redirect('task:list')
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
    return render(request, 'task/confirm_delete.html', {'task': task})
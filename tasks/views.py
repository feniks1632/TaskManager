from django.shortcuts import render
from django.http import HttpResponse  # ← добавь это!

# Create your views here.
def task_list(request):
    return HttpResponse('Это список тасков')

def task_create(request):
    return HttpResponse('Это создание таски')

def task_update(request, pk):
    return HttpResponse('это обновление таски')

def task_delete(request, pk):
    return HttpResponse('это удаление таски')
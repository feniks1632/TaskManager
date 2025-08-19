from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

from notifications.services import NotificationService
from .models import Task


class TaskService:
    """
    Сервис для управления задачами — вся бизнес-логика здесь
    """
    def __init__(self):
        self.notification_service = NotificationService()
        self.channel_layer = get_channel_layer() # Для рассылки

    def create_task(self, data: dict, created_by):
        """
        Создаём задачу и отправляем уведомление
        """
        assignee = data.pop('assignee', None)
        task = Task.objects.create(
            created_by=created_by,
            assignee=assignee,
            **data
        )
        # Если назначена — уведомляем
        if assignee:
            self.notification_service.send_task_assigned(task)
        
        if self.channel_layer:
            async_to_sync(self.channel_layer.group_send)(
                "tasks_list",  # группа для всех на странице задач
                {
                    "type": "task_update",
                    "action": "created",
                    "task": {
                        "id": task.id, # type: ignore
                        "title": task.title,
                        "status": task.get_status_display(), # type: ignore
                        "priority": task.get_priority_display(), # type: ignore
                        "due_date": task.due_date.isoformat() if task.due_date else None,
                        "assignee": task.assignee.username if task.assignee else "",
                        "is_overdue": task.is_overdue(),
                    }
                }
            )
        return task

    def update_task(self, task: Task, data: dict):
        """
        Обновляем задачу, проверяем изменения
        """
        old_assignee = task.assignee
        for key, value in data.items():
            setattr(task, key, value)
        task.save()

        # Если изменили исполнителя — уведомляем нового
        if task.assignee and task.assignee != old_assignee:
            self.notification_service.send_task_assigned(task)

        return task

    def check_overdue_tasks(self):
        """
        Находим просроченные задачи и уведомляем
        (будет использоваться в Celery)
        """
        from django.utils import timezone
        overdue_tasks = Task.objects.filter(
            status__in=['todo', 'in_progress'],
            due_date__lt=timezone.now()
        )
        for task in overdue_tasks:
            self.notification_service.send_task_overdue(task)
        return overdue_tasks
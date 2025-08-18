import logging
from celery import shared_task
from django.utils import timezone
from datetime import timedelta

from core.singleton import NotificationManager
from .models import Task
from .services import NotificationService

logger = logging.getLogger(__name__)

@shared_task
def check_overdue_tasks():
    """
    Проверяет задачи, которые скоро или уже просрочены
    """
    now = timezone.now()
    
    # Задачи, у которых дедлайн через 1 час
    soon_due = Task.objects.filter(
        status='todo',
        due_date__gte=now,
        due_date__lte=now + timedelta(hours=1),
        notified_soon=False,
    )

    # Задачи, которые уже просрочены
    overdue = Task.objects.filter(
        status='todo',
        due_date__lt=now,
        notified_overdue=False,
    )

    service = NotificationService()

    sent_count = 0
    for task in (soon_due | overdue).distinct():
        if not task.assignee or not task.assignee.email:
            continue


        local_due = timezone.localtime(task.due_date)
        due_time = local_due.strftime('%H:%M')

        if task in soon_due:
            message = f"⏰ Напоминание: Задача '{task.title}' истекает в {due_time}"
            subject = "Напоминание о дедлайне"
            task.notified_soon = True

        else:
            message = f"⚠️ Задача просрочена: '{task.title}'"
            subject = "Задача просрочена"
            task.notified_overdue = True

        try:
            email_notif = NotificationManager().get_notification("email")
            email_notif.send(task.assignee.email, message)
            logger.info(f"✅ Напоминание отправлено: {task.assignee.email} — {message[:50]}...")
            task.save()
            sent_count += 1
        except Exception as e:
            logger.error(f"❌ Ошибка отправки email для задачи {task.id}: {e}")

    logger.info(f"✅ Проверка завершена: обработано {sent_count} напоминаний")
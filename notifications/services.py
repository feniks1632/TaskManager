import logging

from core.singleton import NotificationManager

logger = logging.getLogger(__name__)


class NotificationService:
    """
    Сервис для отправки уведомлений через разные каналы.
    Использует NotificationManager (Singleton) и паттерн Factory Method.
    """

    def __init__(self):
        self.manager = NotificationManager()

    def send_task_assigned(self, task):
        """
        Отправляет уведомление исполнителю о назначении задачи.
        """
        if not task.assignee:
            return

        message = f"Вам назначена задача: «{task.title}»"

        # Отправка email
        try:
            email_notif = self.manager.get_notification("email")
            email_notif.send(task.assignee.email, message)
            logger.info(f"Email sent to {task.assignee.email} about task assignment: {task.title}")
        except Exception as e:
            logger.error(f"Failed to send email to {task.assignee.email}: {e}")

        # Отправка WebSocket-уведомления
        try:
            ws_notif = self.manager.get_notification("websocket")
            ws_notif.send(task.assignee.id, message)
            logger.info(f"WebSocket notification sent to user {task.assignee.id}")
        except Exception as e:
            logger.warning(f"WebSocket notification failed for user {task.assignee.id}: {e}")

    def send_task_overdue(self, task):
        """
        Отправляет уведомление о просроченной задаче.
        """
        if not task.assignee:
            return

        message = f"Задача просрочена: «{task.title}»"

        # Отправка email
        try:
            email_notif = self.manager.get_notification("email")
            email_notif.send(task.assignee.email, message)
            logger.info(f"Overdue email sent to {task.assignee.email}: {task.title}")
        except Exception as e:
            logger.error(f"Failed to send overdue email to {task.assignee.email}: {e}")

        # Отправка WebSocket
        try:
            ws_notif = self.manager.get_notification("websocket")
            ws_notif.send(task.assignee.id, message)
            logger.info(f"WebSocket overdue notification sent to user {task.assignee.id}")
        except Exception as e:
            logger.warning(f"WebSocket failed for overdue task {task.id}: {e}")
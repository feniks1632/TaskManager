# tasks/apps.py
from django.apps import AppConfig
from core.singleton import NotificationManager
from notifications.factories import (
    EmailNotificationFactory,
    WebSocketNotificationFactory,
)

import logging

logger = logging.getLogger(__name__)

class TasksConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'tasks'

    def ready(self):
        import tasks.celery_tasks
        logger.info("✅ Запуск TasksConfig: регистрация фабрик уведомлений")
        # Регистрируем фабрики при старте приложения
        nm = NotificationManager()
        nm.register_factory("email", EmailNotificationFactory())
        nm.register_factory("websocket", WebSocketNotificationFactory())

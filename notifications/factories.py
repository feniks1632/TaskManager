import logging
from abc import ABC, abstractmethod

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.conf import settings
from django.core.mail import send_mail

logger = logging.getLogger(__name__)


# Объект
class Notification(ABC):
    @abstractmethod
    def send(self, recipient, message: str):
        pass


# Конкретные объекты
class EmailNotification(Notification):
    __slots__ = ()

    def send(self, recipient, message: str):
        try:
            send_mail(
                subject="Уведомление от TaskFlow",
                message=message,
                html_message=f"<p>{message}</p>",
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[recipient],
                fail_silently=False,
            )
            logger.info(f"Email отправлен на {recipient}")
        except Exception as e:
            logger.error(f"Ошибка отправки email на {recipient}: {e}")

    def __str__(self):
        return "EmailNotification"


class WebSocketNotification(Notification):
    __slots__ = ('channel_layer',)

    def __init__(self):
        self.channel_layer = get_channel_layer()
        if self.channel_layer is None:
            logger.warning("Channel layer не настроен. Проверь ASGI и настройки.")

    def send(self, recipient, message: str):
        if self.channel_layer is None:
            return

        try:
            async_to_sync(self.channel_layer.group_send)(
                f"user_{recipient}",
                {
                    "type": "send_notification",
                    "message": message,
                }
            )
            logger.info(f"WebSocket: отправлено пользователю {recipient}")
        except Exception as e:
            logger.error(f"Ошибка отправки WebSocket-уведомления: {e}")

    def __str__(self):
        return "WebSocketNotification"


# Фабрики
class NotificationFactory(ABC):
    @abstractmethod
    def create_notification(self) -> Notification:
        pass


class EmailNotificationFactory(NotificationFactory):
    _instance = None

    def create_notification(self) -> Notification:
        if self._instance is None:
            self._instance = EmailNotification()
        return self._instance


class WebSocketNotificationFactory(NotificationFactory):
    _instance = None

    def create_notification(self) -> Notification:
        if self._instance is None:
            self._instance = WebSocketNotification()
        return self._instance
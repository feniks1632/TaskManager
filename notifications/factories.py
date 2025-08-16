# notifications/factories.py
from abc import ABC, abstractmethod
from django.core.mail import send_mail
from django.conf import settings
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
import json
from django.utils import timezone
import logging

logger = logging.getLogger(__name__)

# ------ Продукт ------
class Notification(ABC):
    @abstractmethod
    def send(self, recipient, message: str):
        pass

# ------ Конкретные продукты ------
class EmailNotification(Notification):
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
            logger.info(f"✅ Email отправлен на {recipient}")
        except Exception as e:
            logger.error(f"❌ Ошибка отправки email на {recipient}: {e}")

class WebSocketNotification(Notification):
    def send(self, recipient, message: str):
        """
        recipient — это ID пользователя
        """
        try:
            channel_layer = get_channel_layer()
            if channel_layer is None:
                logger.warning("Channel layer не настроен. Проверь ASGI и настройки.")
                return

            async_to_sync(channel_layer.group_send)(
                f"user_{recipient}",
                {
                    "type": "send_notification",
                    "message": message,
                }
            )
            logger.info(f"🌐 WebSocket: отправлено пользователю {recipient}")
        except Exception as e:
            logger.error(f"❌ Ошибка отправки WebSocket-уведомления пользователю {recipient}: {e}")

# ------ Фабрики ------
class NotificationFactory(ABC):
    @abstractmethod
    def create_notification(self) -> Notification:
        pass

class EmailNotificationFactory(NotificationFactory):
    def create_notification(self) -> Notification:
        return EmailNotification()

class WebSocketNotificationFactory(NotificationFactory):
    def create_notification(self) -> Notification:
        return WebSocketNotification()
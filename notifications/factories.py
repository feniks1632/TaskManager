from abc import ABC, abstractmethod
from django.core.mail import send_mail
from django.conf import settings

# Продукт
class Notification(ABC):
    @abstractmethod
    def send(self, recipient, message: str):
        pass

class EmailNotification(Notification):
    def send(self, recipient, message: str):
        try:
            send_mail(
                subject="Уведомление от TaskFlow",
                message=message,
                html_message=f"<p>{message}</p><br><small>Система управления задачами TaskFlow</small>",
                from_email=settings.base.DEFAULT_FROM_EMAIL,
                recipient_list=[recipient],
                fail_silently=False,
            )
            print(f"✅ Email отправлен на {recipient}")
        except Exception as e:
            print(f"❌ Ошибка отправки email на {recipient}: {e}")

class WebSocketNotification(Notification):
    def send(self, recipient, message: str):
        print(f"🌐 Отправлено через WebSocket пользователю {recipient}: {message}")

# Фабрики 
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
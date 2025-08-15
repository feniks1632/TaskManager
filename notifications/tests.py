# notifications/tests.py
from django.test import TestCase
from unittest.mock import patch

# Наши компоненты
from core.singleton import NotificationManager
from notifications.factories import (
    EmailNotificationFactory,
    WebSocketNotificationFactory,
    EmailNotification,
    WebSocketNotification,
)
from notifications.services import NotificationService
from tasks.models import Task
from django.contrib.auth.models import User


class NotificationPatternsTest(TestCase):
    def setUp(self):
        # Создаём пользователя и задачу для тестов
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='pass'
        )
        self.task = Task.objects.create(
            title="Тестовая задача",
            assignee=self.user,
            created_by=self.user,
            status='todo',
            priority='high'
        )

    # --- Тесты для Singleton ---
    def test_notification_manager_is_singleton(self):
        """Проверяем, что NotificationManager — действительно Singleton"""
        nm1 = NotificationManager()
        nm2 = NotificationManager()
        self.assertIs(nm1, nm2, "NotificationManager должен быть Singleton")

    def test_singleton_shared_state(self):
        """Проверяем, что состояние (factories) общее"""
        nm1 = NotificationManager()
        nm2 = NotificationManager()

        nm1.register_factory("email", EmailNotificationFactory())

        self.assertIn("email", nm2.factories)
        self.assertEqual(nm1.factories, nm2.factories)

    # --- Тесты для Factory Method ---
    def test_email_factory_creates_email_notification(self):
        """Фабрика Email должна создавать EmailNotification"""
        factory = EmailNotificationFactory()
        notification = factory.create_notification()
        self.assertIsInstance(notification, EmailNotification)

    def test_websocket_factory_creates_websocket_notification(self):
        """Фабрика WebSocket должна создавать WebSocketNotification"""
        factory = WebSocketNotificationFactory()
        notification = factory.create_notification()
        self.assertIsInstance(notification, WebSocketNotification)

    def test_notification_manager_get_notification(self):
        """NotificationManager должен возвращать правильный тип уведомления"""
        nm = NotificationManager()
        nm.register_factory("email", EmailNotificationFactory())
        nm.register_factory("websocket", WebSocketNotificationFactory())

        email_notif = nm.get_notification("email")
        ws_notif = nm.get_notification("websocket")

        self.assertIsInstance(email_notif, EmailNotification)
        self.assertIsInstance(ws_notif, WebSocketNotification)

    def test_notification_manager_raises_error_for_unknown_method(self):
        """Должен выбросить ValueError, если метод не зарегистрирован"""
        nm = NotificationManager()
        with self.assertRaises(ValueError) as context:
            nm.get_notification("sms")
        self.assertIn("Фабрика не найдена", str(context.exception))

    # --- Тесты для NotificationService ---
    @patch('notifications.factories.EmailNotification.send')
    def test_notification_service_sends_email_on_task_assignment(self, mock_send):
        """Проверяем, что при назначении задачи отправляется email"""
        service = NotificationService()
        service.send_task_assigned(self.task)

        mock_send.assert_called_once()
        args, kwargs = mock_send.call_args
        recipient, message = args
        self.assertEqual(recipient, self.user.email)
        self.assertIn("Тестовая задача", message)

    @patch('notifications.factories.WebSocketNotification.send')
    def test_notification_service_sends_websocket_on_task_assignment(self, mock_send):
        """Проверяем, что отправляется WebSocket-уведомление"""
        service = NotificationService()
        service.send_task_assigned(self.task)

        mock_send.assert_called_once()
        args, kwargs = mock_send.call_args
        user_id, message = args
        self.assertEqual(user_id, self.user.id)
        self.assertIn("Тестовая задача", message)

    @patch('notifications.factories.EmailNotification.send')
    def test_notification_service_sends_overdue_email(self, mock_send):
        """Проверяем, что отправляется email о просрочке"""
        service = NotificationService()
        service.send_task_overdue(self.task)

        mock_send.assert_called_once()
        args, kwargs = mock_send.call_args
        recipient, message = args
        self.assertEqual(recipient, self.user.email)
        self.assertIn("просрочена", message)

    def test_notification_service_handles_missing_assignee_gracefully(self):
        """Если нет assignee — сервис не должен падать"""
        self.task.assignee = None
        self.task.save()

        service = NotificationService()

        # Не должно быть исключений
        service.send_task_assigned(self.task)
        service.send_task_overdue(self.task)

        # Просто не отправляем
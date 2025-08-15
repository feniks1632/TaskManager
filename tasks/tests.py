# tasks/tests.py
from django.test import TestCase
from core.singleton import NotificationManager
from notifications.factories import EmailNotificationFactory

class SingletonTest(TestCase):
    def test_singleton_instance(self):
        nm1 = NotificationManager()
        nm2 = NotificationManager()
        self.assertIs(nm1, nm2)

    def test_factory_registration(self):
        nm = NotificationManager()
        nm.register_factory("test", EmailNotificationFactory())
        notif = nm.get_notification("test")
        self.assertIsInstance(notif, EmailNotification())
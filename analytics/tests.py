from datetime import timedelta
from django.contrib.auth.models import User
from django.test import TestCase
from django.utils import timezone

from .services import AnalyticsService
from tasks.models import Task


class AnalyticsServiceTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser')
        self.service = AnalyticsService(self.user)

    def test_get_stats(self):
        # Создаём задачи
        Task.objects.create(assignee=self.user, status='done', created_by=self.user)
        Task.objects.create(assignee=self.user, status='in_progress', created_by=self.user)
        Task.objects.create(assignee=self.user, status='todo', due_date=timezone.now() + timedelta(days=1), created_by=self.user)
        Task.objects.create(assignee=self.user, status='todo', due_date=timezone.now() - timedelta(days=1), created_by=self.user)

        stats = self.service.get_stats()
        self.assertEqual(stats['total'], 4)
        self.assertEqual(stats['completed'], 1)
        self.assertEqual(stats['in_progress'], 1)
        self.assertEqual(stats['overdue'], 1)
        self.assertEqual(stats['todo'], 1)

    def test_get_weekly_data(self):
        now = timezone.now()
        # Создаём задачу сегодня
        Task.objects.create(
            assignee=self.user,
            title='Сегодня',
            created_at=now,
            created_by=self.user
        )
        weekly = self.service.get_weekly_data()
        self.assertIn(now.strftime('%a'), weekly['labels'])
        # Убедимся, что хотя бы один день имеет 1
        self.assertGreaterEqual(max(weekly['data']), 1)
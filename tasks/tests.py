from django.contrib.auth.models import User
from django.test import TestCase
from django.utils import timezone

from .models import Task
from .services import TaskService


class TaskServiceTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser', 
            first_name='testname', 
            last_name='testlatsname', 
            email='testemail@gmail.com', 
            password='testpassword56f'
        )
        self.service = TaskService()

    def create_task(self):
        data = {
            'title': 'Новая задача',
            'description': 'Описание',
            'status': 'todo',
            'priority': 'medium',
            'due_date': timezone.datetime(2025, 12, 31, 10, 0, 0, tzinfo=timezone.utc),
            'assignee': self.user,
            'created_by': self.user,
        }
        task = self.service.create_task(data, created_by=self.user)
        self.assertEqual(task.title, "Новая задача")
        self.assertEqual(task.assignee, self.user)

    def test_update_task(self):
        task = Task.objects.create(
            title='Старая', 
            assignee=self.user,
            created_by=self.user
        )
        data = {'title': 'Обновлённая'}
        self.service.update_task(task, data)
        task.refresh_from_db()
        self.assertEqual(task.title, 'Обновлённая')
from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils import timezone


class Task(models.Model):
    STATUS_CHOISES = [
        ('todo', 'To DO'),
        ('in_progress', 'In progress'),
        ('done', 'Done')
    ]
    
    PRIORITY_CHOISES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
    ]

    title = models.CharField('Название', max_length=300)
    description = models.CharField('Описание', blank=True)
    status = models.CharField(
        'Статус',
        max_length=20,
        choices=STATUS_CHOISES,
        default='todo',
    )

    priority = models.CharField(
        "Приоритет",
        max_length=10,
        choices=PRIORITY_CHOISES,
        default='medium'
    )

    due_date = models.DateTimeField("Срок выполнения", null=True, blank=True)
    created_at = models.DateTimeField("Создано", auto_now_add=True)
    updated_at = models.DateTimeField("Обновлено", auto_now=True)

    assignee = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_tasks',
        verbose_name='Исполнитель'
    )

    created_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='created_tasks',
        verbose_name='Создал'
    )

    notified_soon = models.BooleanField(default=False)
    notified_overdue = models.BooleanField(default=False)

    class Meta:
        verbose_name = 'Задача',
        verbose_name_plural = 'Задачи',
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status']),
            models.Index(fields=['priority']),
            models.Index(fields=['due_date']),
            models.Index(fields=['assignee']),
        ]

    def __str__(self):
        return self.title
    
    def get_absolute_url(self):
        return reverse('task:update', kwargs={'pk': self.pk})
    
    def is_overdue(self):
        """Проверка задачи на просрочку"""
        if self.due_date and self.status != 'done':
            return self.due_date < timezone.now()
        return False
    
    def is_high_priority(self):
        return self.priority == 'high'
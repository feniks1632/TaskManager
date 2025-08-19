from datetime import timedelta

from django.db.models import Case, Count, IntegerField, When
from django.db.models.functions import TruncDate
from django.utils import timezone

from tasks.models import Task


class AnalyticsService:
    def __init__(self, user):
        self.user = user

    def get_stats(self):

        now = timezone.now()

        stats = Task.objects.filter(assignee=self.user).aggregate(
            total=Count('id'),
            completed=Count(Case(When(status='done', then=1), output_field=IntegerField())),
            in_progress=Count(Case(When(status='in_progress', then=1), output_field=IntegerField())),
            overdue=Count(
                Case(
                    When(status='todo', due_date__lt=now, then=1),
                    output_field=IntegerField()
                )
            ),
            todo=Count(
                Case(
                    When(status='todo', due_date__gte=now, then=1),
                    output_field=IntegerField()
                )
            ),
        )

        # Если нет задач, Django вернёт None заменим на 0
        return {k: (v or 0) for k, v in stats.items()}
    
    def get_weekly_data(self):

        now = timezone.now()

        week_ago = now - timedelta(days=7)

        print(f"📅 now = {now}")
        print(f"📅 week_ago = {week_ago}")

        # Группируем по дате создания
        daily_data = (
            Task.objects
            .filter(
                assignee=self.user,
                created_at__gte=week_ago
            )
            .annotate(day=TruncDate('created_at'))
            .values('day')
            .annotate(count=Count('id'))
            .order_by('day')
        )

        print("🔍 Найденные задачи за неделю:")
        for item in daily_data:
            print(f"  Дата: {item['day']}, Количество: {item['count']}")

        # Подготовка данных для графика
        day_map = {now.date() - timedelta(days=i): 0 for i in range(7)}
        for item in daily_data:
            day_map[item['day']] = item['count']

        labels = [now.date() - timedelta(days=i) for i in range(6, -1, -1)]
        data = [day_map[day] for day in labels]

        print("📊 Финальные данные для графика:")
        print("Labels:", [day.strftime('%a') for day in labels])
        print("Data:", data)

        return {
            'labels': [day.strftime('%a') for day in labels],
            'data': data
        }